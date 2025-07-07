from fastapi import APIRouter, HTTPException, Depends
from supabase import Client
from db.supabase_client import get_supabase_client
from stripe import StripeClient
from coinbase_commerce import Client as CoinbaseClient
import flutterwave_python
from sendgrid import SendGridAPIClient
from twilio.rest import Client as TwilioClient
from python_dotenv import load_dotenv
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from scripts.exness_trade import BinanceBroker, ExnessBroker
from src.auth_middleware import get_current_user
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
scheduler = AsyncIOScheduler()

class PaymentService:
    def __init__(self):
        self.stripe = StripeClient(os.getenv("STRIPE_API_KEY"))
        self.coinbase = CoinbaseClient(os.getenv("COINBASE_API_KEY"))
        self.flutterwave = flutterwave_python.Flutterwave(os.getenv("FLUTTERWAVE_API_KEY"))
        self.sendgrid = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        self.twilio = TwilioClient(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    async def initiate_payment(self, amount: float, currency: str, user_id: str):
        try:
            if currency in ["BTC", "ETH", "USDT"]:
                charge = self.coinbase.create_charge(
                    name="Deposit",
                    description=f"Deposit for user {user_id}",
                    amount=amount,
                    currency=currency,
                    metadata={"user_id": user_id}
                )
                logger.info(f"Coinbase charge created: {charge.id}")
                return charge.hosted_url
            else:
                session = self.stripe.checkout.sessions.create(
                    payment_method_types=["card", "bank_transfer"],
                    line_items=[{
                        "price_data": {
                            "currency": currency,
                            "unit_amount": int(amount * 100),
                            "product_data": {"name": "Deposit"}
                        },
                        "quantity": 1
                    }],
                    mode="payment",
                    success_url=os.getenv("SUCCESS_URL", "https://app.swift-ai-trader.com/success"),
                    cancel_url=os.getenv("CANCEL_URL", "https://app.swift-ai-trader.com/cancel"),
                    metadata={"user_id": user_id}
                )
                logger.info(f"Stripe session created: {session.id}")
                return session.url
        except Exception as e:
            logger.error(f"Payment initiation failed: {str(e)}")
            raise

    async def process_withdrawal(self, user_id: str, amount: float, currency: str, address: str):
        try:
            if currency in ["BTC", "ETH", "USDT"]:
                payout = self.coinbase.create_payout(
                    amount=amount,
                    currency=currency,
                    destination=address,
                    metadata={"user_id": user_id}
                )
                logger.info(f"Coinbase payout created: {payout.id}")
                return payout.id
            else:
                payout = self.stripe.payouts.create(
                    amount=int(amount * 100),
                    currency=currency,
                    destination=address,
                    metadata={"user_id": user_id}
                )
                logger.info(f"Stripe payout created: {payout.id}")
                return payout.id
        except Exception as e:
            logger.error(f"Withdrawal failed: {str(e)}")
            raise

    async def create_subscription(self, user_id: str, tier: str, amount: float):
        try:
            session = self.stripe.checkout.sessions.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(amount * 100),
                        "product_data": {"name": f"{tier} Subscription"},
                        "recurring": {"interval": "month"}
                    },
                    "quantity": 1
                }],
                mode="subscription",
                success_url=os.getenv("SUCCESS_URL", "https://app.swift-ai-trader.com/success"),
                cancel_url=os.getenv("CANCEL_URL", "https://app.swift-ai-trader.com/cancel"),
                metadata={"user_id": user_id, "tier": tier}
            )
            logger.info(f"Stripe subscription session created: {session.id}")
            return session.url
        except Exception as e:
            logger.error(f"Subscription creation failed: {str(e)}")
            raise

    async def notify_owner_withdrawal(self, user_id: str, amount: float, currency: str, address: str):
        try:
            self.sendgrid.send(
                from_email="owner@swift-ai-trader.com",
                to_emails=os.getenv("OWNER_EMAIL", "owner@example.com"),
                subject="Withdrawal Request",
                html_content=f"User {user_id} requests {amount} {currency} withdrawal to {address}. Approve: {os.getenv('ADMIN_URL', 'https://app.swift-ai-trader.com/admin')}/approve-withdrawal/{user_id}"
            )
            logger.info(f"Withdrawal notification sent for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send withdrawal notification: {str(e)}")

@router.post("/subscribe")
async def subscribe_premium(
    tier: str,
    supabase: Client = Depends(get_supabase_client),
    current_user: dict = Depends(get_current_user)
):
    try:
        amount = 12.0 if tier == "premium" else 25.0
        payment_service = PaymentService()
        subscription_url = await payment_service.create_subscription(current_user["id"], tier, amount)
        await supabase.table("subscriptions").insert({
            "user_id": current_user["id"],
            "tier": tier,
            "status": "active",
            "renewal_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }).execute()
        logger.info(f"Subscription created for user {current_user['id']}: {tier}")
        return {"subscription_url": subscription_url}
    except Exception as e:
        logger.error(f"Subscription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.on_event("startup")
async def startup_event():
    scheduler.start()
    scheduler.add_job(daily_profit_deduction, "cron", hour=0, minute=0)
    logger.info("Scheduler started for daily profit deduction")

async def daily_profit_deduction():
    supabase = get_supabase_client()
    users = await supabase.table("users").select("id").execute()
    for user in users.data:
        for broker in ["binance", "exness"]:
            try:
                profits = await calculate_profit(user["id"], broker)
                fee = profits * 0.2
                if fee >= 10:
                    await supabase.table("fees").insert({
                        "user_id": user["id"],
                        "broker": broker,
                        "amount": fee,
                        "timestamp": datetime.utcnow().isoformat()
                    }).execute()
                    await transfer_to_owner_wallet(fee, broker)
                    logger.info(f"Fee deducted: {fee} for user {user['id']} on {broker}")
            except Exception as e:
                logger.error(f"Profit deduction failed for user {user['id']}: {str(e)}")

async def calculate_profit(user_id: str, broker: str):
    supabase = get_supabase_client()
    trades = await supabase.table("trades").select("volume, price, side").eq("user_id", user_id).eq("broker", broker).gte("timestamp", (datetime.utcnow() - timedelta(days=1)).isoformat()).execute()
    profit = 0
    for trade in trades.data:
        multiplier = 1 if trade["side"] == "sell" else -1
        profit += trade["volume"] * trade["price"] * multiplier
    logger.info(f"Calculated profit for user {user_id} on {broker}: {profit}")
    return profit

async def transfer_to_owner_wallet(amount: float, broker: str):
    try:
        if broker == "binance":
            await BinanceBroker().withdraw("USDT", amount, os.getenv("OWNER_USDT_WALLET"))
        elif broker == "exness":
            await ExnessBroker().request_withdrawal(amount, os.getenv("OWNER_USDT_WALLET"))
        logger.info(f"Transferred {amount} to owner wallet on {broker}")
    except Exception as e:
        logger.error(f"Owner wallet transfer failed: {str(e)}")
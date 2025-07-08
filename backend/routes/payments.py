import os
import requests
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from stripe import stripe
from coinbase_commerce.client import Client as CoinbaseClient
from sendgrid import SendGridAPIClient
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv
from supabase import Client
from db.supabase_client import get_supabase_client
from scripts.exness_trade import BinanceBroker, ExnessBroker
from src.auth_middleware import get_current_user

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
scheduler = AsyncIOScheduler()

class PaymentService:
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_API_KEY")
        self.coinbase = CoinbaseClient(api_key=os.getenv("COINBASE_API_KEY"))
        self.flutterwave_key = os.getenv("FLUTTERWAVE_API_KEY")
        self.sendgrid = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        self.twilio = TwilioClient(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    async def initiate_payment(self, amount: float, currency: str, user_id: str):
        try:
            if currency in ["BTC", "ETH", "USDT"]:
                charge = self.coinbase.charge.create(
                    name="Deposit",
                    description=f"Deposit for user {user_id}",
                    local_price={"amount": str(amount), "currency": currency},
                    pricing_type="fixed_price",
                    metadata={"user_id": user_id}
                )
                logger.info(f"Coinbase charge created: {charge['id']}")
                return charge["hosted_url"]
            elif currency.lower() == "ngn":  # Flutterwave use-case
                return self.initiate_flutterwave_payment(amount, currency, "user@example.com", f"tx_{user_id}_{datetime.utcnow().timestamp()}")
            else:
                session = stripe.checkout.Session.create(
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

    def initiate_flutterwave_payment(self, amount, currency, email, tx_ref):
        url = "https://api.flutterwave.com/v3/payments"
        headers = {
            "Authorization": f"Bearer {self.flutterwave_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": currency,
            "redirect_url": os.getenv("SUCCESS_URL", "https://app.swift-ai-trader.com/success"),
            "payment_options": "card,banktransfer",
            "customer": {
                "email": email
            },
            "customizations": {
                "title": "Swift-AI Trader",
                "description": "Deposit for trading"
            }
        }
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        logger.info(f"Flutterwave session created: {response_data}")
        return response_data["data"]["link"]

    async def process_withdrawal(self, user_id: str, amount: float, currency: str, address: str):
        try:
            if currency in ["BTC", "ETH", "USDT"]:
                payout = self.coinbase.payout.create(
                    amount=amount,
                    currency=currency,
                    destination=address,
                    metadata={"user_id": user_id}
                )
                logger.info(f"Coinbase payout created: {payout.id}")
                return payout.id
            else:
                payout = stripe.Payout.create(
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
            session = stripe.checkout.Session.create(
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
                html_content=(
                    f"User {user_id} requests {amount} {currency} withdrawal to {address}. "
                    f"<br>Approve: {os.getenv('ADMIN_URL', 'https://app.swift-ai-trader.com/admin')}/approve-withdrawal/{user_id}"
                )
            )
            logger.info(f"Withdrawal notification sent for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send withdrawal notification: {str(e)}")

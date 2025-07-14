from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from core.models.user import User
from core.models.transaction import Transaction, TransactionType, TransactionStatus
from core.schemas.transaction import DepositRequest, WithdrawRequest, TransactionResponse
from services.payment_service import PaymentService
from api.auth import get_current_user
from typing import List
import uuid

router = APIRouter()

@router.post("/deposit-initiate")
async def initiate_deposit(
    request: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Initiate deposit via Paystack"""
    reference = f"WV_{uuid.uuid4().hex[:12].upper()}"
    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.DEPOSIT,
        amount=request.amount,
        reference=reference,
        description=f"Deposit of ${request.amount}"
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    payment_service = PaymentService()
    payment_url = await payment_service.initialize_payment(
        amount=request.amount,
        email=current_user.email,
        reference=reference
    )
    return {"payment_url": payment_url, "reference": reference, "amount": request.amount}

@router.post("/deposit-webhook")
async def deposit_webhook(
    reference: str,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    payment_service = PaymentService()
    is_valid = await payment_service.verify_payment(reference)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment")

    result = await db.execute(
        select(Transaction).where(Transaction.reference == reference)
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.status = TransactionStatus.SUCCESS
    await db.commit()
    await db.refresh(transaction)

    background_tasks.add_task(update_portfolio_balance, transaction.user_id, transaction.amount)
    return {"status": "success", "reference": reference}

@router.post("/withdraw-request")
async def request_withdrawal(
    request: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.WITHDRAWAL,
        amount=request.amount,
        description=f"Withdrawal of ${request.amount}"
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return {
        "message": "Withdrawal request submitted",
        "transaction_id": transaction.id,
        "amount": request.amount
    }

@router.get("/transactions")
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TransactionResponse]:
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == current_user.id).order_by(Transaction.timestamp.desc())
    )
    transactions = result.scalars().all()
    return transactions

async def update_portfolio_balance(user_id: str, amount: float):
    # TODO: Implement actual balance update logic
    pass

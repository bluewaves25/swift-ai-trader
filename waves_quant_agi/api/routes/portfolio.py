### api/routes/portfolio.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from waves_quant_agi.core.database import get_db
from waves_quant_agi.core.models.portfolio import InvestorPortfolio
from waves_quant_agi.core.schemas.portfolio import PortfolioResponse
from waves_quant_agi.api.auth import get_current_user
from waves_quant_agi.core.models.user import User

router = APIRouter()

@router.get("/me", response_model=PortfolioResponse)
async def get_my_portfolio(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(InvestorPortfolio).where(InvestorPortfolio.user_id == current_user.id))
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return portfolio


@router.get("/performance", response_model=PortfolioResponse)
async def get_portfolio_performance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(InvestorPortfolio).where(InvestorPortfolio.user_id == current_user.id))
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Performance data not found")

    # In future, attach analytics and advanced KPIs
    return portfolio

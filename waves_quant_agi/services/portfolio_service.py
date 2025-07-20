### services/portfolio_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from waves_quant_agi.core.models.portfolio import InvestorPortfolio
from waves_quant_agi.core.models.user import User
import logging

logger = logging.getLogger(__name__)

class PortfolioService:
    """
    Business logic for managing investor portfolios.
    """

    @staticmethod
    async def get_portfolio(user_id: int, db: AsyncSession) -> InvestorPortfolio:
        stmt = select(InvestorPortfolio).where(InvestorPortfolio.user_id == user_id)
        result = await db.execute(stmt)
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise ValueError("Portfolio not found")

        return portfolio

    @staticmethod
    async def update_portfolio_balance(user_id: int, amount: float, db: AsyncSession):
        portfolio = await PortfolioService.get_portfolio(user_id, db)
        logger.info(f"Updating portfolio balance for user {user_id} by {amount}")
        portfolio.balance += amount
        await db.commit()

    @staticmethod
    async def calculate_nav(user_id: int, db: AsyncSession) -> float:
        portfolio = await PortfolioService.get_portfolio(user_id, db)
        if portfolio.invested_amount == 0:
            return 1.0
        nav = portfolio.current_value / portfolio.invested_amount
        logger.info(f"Calculated NAV for user {user_id}: {nav:.4f}")
        return nav

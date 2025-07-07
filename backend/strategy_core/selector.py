from stable_baselines3 import PPO
from ai_brains.breakout import BreakoutStrategy
from ai_brains.mean_reversion import MeanReversionStrategy
from ai_brains.scalping import ScalpingStrategy
from ai_brains.arbitrage import ArbitrageStrategy
from data_feed.market_data import MarketData

class StrategySelector:
    def __init__(self):
        self.model = PPO.load("strategy_model")
        self.strategies = {
            "breakout": BreakoutStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "scalping": ScalpingStrategy(),
            "arbitrage": ArbitrageStrategy()
        }
        self.market_data = MarketData()

    async def select_strategy(self, symbol: str):
        data = await self.market_data.get_binance_data(symbol)  # Example
        state = self.prepare_state(data)
        action = self.model.predict(state)[0]
        strategy_name = list(self.strategies.keys())[action]
        return self.strategies[strategy_name]
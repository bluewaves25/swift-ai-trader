from supabase import Client
from db.supabase_client import get_supabase_client
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
import numpy as np
from datetime import datetime, timedelta
import ccxt.async_support as ccxt
import os
from python_dotenv import load_dotenv
import logging
import gym
from gym import spaces

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingEnv(gym.Env):
    def __init__(self, trades, losses):
        super(TradingEnv, self).__init__()
        self.trades = trades
        self.losses = losses
        self.current_step = 0
        self.max_steps = len(trades)
        self.action_space = spaces.Discrete(3)  # 0: hold, 1: reduce lot size, 2: suspend
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(5,), dtype=np.float32)

    def reset(self):
        self.current_step = 0
        return self._get_observation()

    def step(self, action):
        self.current_step += 1
        done = self.current_step >= self.max_steps
        reward = self._calculate_reward(action)
        obs = self._get_observation() if not done else np.zeros(5)
        return obs, reward, done, {}

    def _get_observation(self):
        trade = self.trades[self.current_step] if self.current_step < self.max_steps else {}
        loss = next((l for l in self.losses if l['timestamp'] >= trade.get('timestamp', '')), {})
        return np.array([
            trade.get('volume', 0.0),
            trade.get('price', 0.0),
            loss.get('amount', 0.0),
            1 if trade.get('side', '') == 'buy' else -1 if trade.get('side', '') == 'sell' else 0,
            float(loss.get('type', 'small') == 'large')
        ], dtype=np.float32)

    def _calculate_reward(self, action):
        loss = next((l for l in self.losses if l['timestamp'] >= self.trades[self.current_step]['timestamp']), {})
        loss_amount = loss.get('amount', 0.0)
        if action == 0:  # Hold
            return -loss_amount * 0.1
        elif action == 1:  # Reduce lot size
            return -loss_amount * 0.05 if loss_amount > 0 else 0.1
        else:  # Suspend
            return 0.2 if loss_amount > 0.015 else -0.1

class RiskManager:
    def __init__(self):
        self.model = PPO.load("risk_model") if os.path.exists("risk_model.zip") else PPO("MlpPolicy", make_vec_env(TradingEnv, n_envs=1, env_kwargs={"trades": [], "losses": []}))
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_SECRET"),
            'enableRateLimit': True
        })

    async def check_risk(self, trade, broker: str, account: str):
        supabase = get_supabase_client()
        portfolio = await supabase.table("wallets").select("balance").eq("account_number", account).eq("user_id", trade.user_id).execute()
        if not portfolio.data:
            logger.error(f"Wallet not found for account {account}")
            return {"approved": False, "reason": "Wallet not found"}
        if trade.volume > 0.07 * portfolio.data[0]["balance"]:
            logger.warning(f"Position size too large: {trade.volume} > {0.07 * portfolio.data[0]['balance']}")
            return {"approved": False, "reason": "Position size too large"}
        if await self.is_high_volatility(trade.symbol):
            logger.warning(f"High volatility detected for {trade.symbol}")
            return {"approved": False, "reason": "Market volatility too high"}
        return {"approved": True}

    async def is_high_volatility(self, symbol: str):
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, '1h', limit=24)
            prices = [candle[4] for candle in ohlcv]
            returns = np.diff(prices) / prices[:-1]
            volatility = np.std(returns)
            logger.info(f"Volatility for {symbol}: {volatility}")
            return volatility > 0.02  # 2% threshold
        except Exception as e:
            logger.error(f"Volatility check failed: {str(e)}")
            return False
        finally:
            await self.exchange.close()

    async def handle_loss(self, trade, broker: str, error: str, user_id: str):
        supabase = get_supabase_client()
        pair = await supabase.table("trading_pairs").select("id").eq("symbol", trade.symbol).execute()
        pair_id = pair.data[0]["id"] if pair.data else None
        loss_size = trade.volume * trade.price * 0.015
        loss_data = {
            "user_id": user_id,
            "broker": broker,
            "type": "small" if loss_size <= 0.005 else "medium" if loss_size <= 0.015 else "large",
            "amount": loss_size,
            "timestamp": datetime.utcnow().isoformat()
        }
        if pair_id:
            loss_data["pair_id"] = pair_id
        try:
            await supabase.table("losses").insert(loss_data).execute()
            logger.info(f"Loss logged for user {user_id}: {loss_size}")
            if loss_size > 0.015:
                self.suspend_strategy(trade.symbol)
                await self.retrain_model()
            elif loss_size > 0.005:
                self.adjust_lot_size(0.7)
        except Exception as e:
            logger.error(f"Failed to log loss: {str(e)}")

    def adjust_lot_size(self, factor: float):
        self.model.policy.set_lot_size(factor)
        logger.info(f"Lot size adjusted by factor {factor}")

    def suspend_strategy(self, symbol: str):
        logger.info(f"Strategy suspended for {symbol}")

    async def retrain_model(self):
        supabase = get_supabase_client()
        try:
            # Fetch trade and loss data
            trades = await supabase.table("trades").select("user_id, pair_id, symbol, side, volume, price, timestamp").execute()
            losses = await supabase.table("losses").select("user_id, pair_id, amount, type, timestamp").execute()
            if not trades.data or not losses.data:
                logger.warning("No trade or loss data for retraining")
                return

            # Create training environment
            env = make_vec_env(TradingEnv, n_envs=4, env_kwargs={"trades": trades.data, "losses": losses.data})
            
            # Retrain PPO model
            self.model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003, n_steps=2048)
            self.model.learn(total_timesteps=10000)
            
            # Save updated model
            self.model.save("risk_model")
            logger.info("Risk model retrained and saved as risk_model.zip")
        except Exception as e:
            logger.error(f"Model retraining failed: {str(e)}")
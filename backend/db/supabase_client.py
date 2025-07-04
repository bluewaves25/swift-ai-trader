from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    def save_trade(self, trade_data: dict):
        return self.client.table("trades").insert(trade_data).execute()

    def get_historical_data(self, symbol: str, start_time: str, end_time: str):
        return self.client.table("market_data").select("*").eq("symbol", symbol).gte("timestamp", start_time).lte("timestamp", end_time).execute()

    def save_strategy_performance(self, performance_data: dict):
        return self.client.table("pair_strategies").insert(performance_data).execute()

    def get_strategy_performance(self, symbol: str):
        return self.client.table("pair_strategies").select("*").eq("symbol", symbol).execute()

    def save_market_data(self, data: dict):
        return self.client.table("market_data").insert(data).execute()
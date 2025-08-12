"""
Dependency injection for the API.
Provides common dependencies for routes.
"""
import os
from typing import Optional
from waves_quant_agi.engine_agents.adapters.brokers.mt5_plugin import MT5Broker

def get_mt5_broker() -> Optional[MT5Broker]:
    """
    Get MT5 broker instance with credentials from environment.
    Returns None if credentials are not available.
    """
    try:
        mt5_login = os.getenv("MT5_LOGIN")
        mt5_password = os.getenv("MT5_PASSWORD")
        mt5_server = os.getenv("MT5_SERVER", "Exness-MT5Trial")
        
        if not mt5_login or not mt5_password:
            return None
        
        broker = MT5Broker(int(mt5_login), mt5_password, mt5_server)
        if broker.connect():
            return broker
        else:
            return None
            
    except Exception as e:
        print(f"Error creating MT5 broker: {e}")
        return None

import os
from fastapi import Depends, HTTPException
from waves_quant_agi.engine.brokers.mt5_plugin import MT5Broker

def get_mt5_broker():
    """
    FastAPI dependency to provide a connected MT5Broker instance.
    Centralizes connection logic and credential management.
    """
    mt5_login = os.getenv("MT5_LOGIN")
    mt5_password = os.getenv("MT5_PASSWORD")
    mt5_server = os.getenv("MT5_SERVER", "Exness-MT5")

    if not all([mt5_login, mt5_password, mt5_server]):
        raise HTTPException(status_code=500, detail="MT5 credentials are not configured in environment.")

    try:
        broker = MT5Broker(int(mt5_login), mt5_password, mt5_server)
        broker.connect()
        yield broker
    except Exception as e:
        # In a real app, you might want to disconnect or handle the pool here.
        raise HTTPException(status_code=503, detail=f"Could not connect to MT5 broker: {e}")
    finally:
        # This block will be executed after the response has been sent.
        # broker.disconnect() # You would add a disconnect method to your broker class.
        pass
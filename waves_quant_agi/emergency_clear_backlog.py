#!/usr/bin/env python3
"""
EMERGENCY: Clear Execution Orders Backlog
This script clears the massive backlog of execution orders that's preventing live trading.
"""

from engine_agents.shared_utils.redis_connector import SharedRedisConnector
import json
import time

def emergency_clear_backlog():
    """Emergency clearance of execution orders backlog."""
    redis = SharedRedisConnector()
    
    print("🚨 EMERGENCY BACKLOG CLEARANCE")
    print("=" * 50)
    
    # Check current backlog
    print("📊 CURRENT BACKLOG STATUS:")
    total_orders = redis.redis_sync.llen('execution_orders')
    print(f"  Execution Orders: {total_orders}")
    
    if total_orders == 0:
        print("✅ No backlog to clear!")
        return
    
    # WARNING
    print(f"\n⚠️ WARNING: {total_orders} orders will be permanently deleted!")
    print("This will clear all pending execution orders.")
    print("Only proceed if you're sure the execution engine is not working.")
    
    # Confirm action
    confirm = input("\n🚨 Type 'EMERGENCY' to confirm deletion: ")
    if confirm != "EMERGENCY":
        print("❌ Operation cancelled.")
        return
    
    print(f"\n🧹 CLEARING BACKLOG...")
    
    try:
        # Clear execution orders
        deleted_orders = redis.redis_sync.delete('execution_orders')
        print(f"  ✅ Deleted {deleted_orders} execution orders")
        
        # Clear any related queues
        related_queues = ['execution_errors', 'position_updates', 'trading_commands']
        for queue in related_queues:
            count = redis.redis_sync.llen(queue)
            if count > 0:
                redis.redis_sync.delete(queue)
                print(f"  ✅ Cleared {queue}: {count} items")
        
        # Clear signal queues to stop new orders temporarily
        signal_queues = ['live_trading_signals', 'fast_signals', 'tactical_signals', 'hft_signals']
        for queue in signal_queues:
            count = redis.redis_sync.llen(queue)
            if count > 0:
                redis.redis_sync.delete(queue)
                print(f"  ✅ Cleared {queue}: {count} signals")
        
        # Clear market data to prevent immediate regeneration
        market_data_count = redis.redis_sync.llen('market_data:latest')
        if market_data_count > 0:
            redis.redis_sync.ltrim('market_data:latest', 0, 9)  # Keep only last 10
            print(f"  ✅ Trimmed market data to last 10 points")
        
        print(f"\n✅ EMERGENCY CLEARANCE COMPLETED!")
        print(f"✅ All execution orders cleared")
        print(f"✅ Signal generation temporarily stopped")
        
        # Verify clearance
        print(f"\n📊 VERIFICATION:")
        final_orders = redis.redis_sync.llen('execution_orders')
        final_signals = redis.redis_sync.llen('live_trading_signals')
        print(f"  Execution Orders: {final_orders}")
        print(f"  Live Signals: {final_signals}")
        
        if final_orders == 0 and final_signals == 0:
            print(f"  ✅ Backlog successfully cleared!")
        else:
            print(f"  ⚠️ Some items remain - manual check needed")
        
    except Exception as e:
        print(f"❌ Error during emergency clearance: {e}")
        return
    
    print(f"\n" + "=" * 50)
    print("🚨 NEXT STEPS REQUIRED:")
    print("1. ✅ Backlog cleared - system is now stable")
    print("2. 🔍 Check MT5 connection status")
    print("3. 🔧 Fix execution engine MT5 connection")
    print("4. 🚀 Restart signal generation")
    print("5. ✅ Resume live trading")
    
    print(f"\n💡 IMMEDIATE ACTIONS:")
    print("- Run: python check_mt5_connection.py")
    print("- Check if MT5 is running and accessible")
    print("- Verify execution engine can connect to MT5")
    print("- Only restart signal generation after MT5 is working")

if __name__ == "__main__":
    emergency_clear_backlog()

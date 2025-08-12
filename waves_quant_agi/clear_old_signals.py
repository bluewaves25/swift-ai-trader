#!/usr/bin/env python3
"""
Clear Old Signals - Remove old signals to allow new ones to be generated
"""

from engine_agents.shared_utils.redis_connector import SharedRedisConnector
import json
import time

def clear_old_signals():
    """Clear old signals to allow new ones to be generated."""
    redis = SharedRedisConnector()
    
    print("🧹 CLEARING OLD SIGNALS")
    print("=" * 50)
    
    # Check current signal count
    live_signals_count = redis.redis_sync.llen('live_trading_signals')
    fast_signals_count = redis.redis_sync.llen('fast_signals')
    tactical_signals_count = redis.redis_sync.llen('tactical_signals')
    
    print(f"📊 CURRENT SIGNAL COUNTS:")
    print(f"  Live Trading Signals: {live_signals_count}")
    print(f"  Fast Signals: {fast_signals_count}")
    print(f"  Tactical Signals: {tactical_signals_count}")
    
    if live_signals_count > 0:
        print(f"\n🔍 ANALYZING SIGNAL AGES:")
        signals = redis.redis_sync.lrange('live_trading_signals', 0, 4)
        current_time = time.time()
        
        old_signals = 0
        for signal in signals:
            try:
                parsed = json.loads(signal)
                timestamp = parsed.get('timestamp', 0)
                if timestamp > 0:
                    age_hours = (current_time - timestamp) / 3600
                    if age_hours > 1:
                        old_signals += 1
            except:
                old_signals += 1
        
        print(f"  Old signals (>1 hour): {old_signals}")
        
        if old_signals > 0:
            print(f"\n🧹 CLEARING OLD SIGNALS...")
            
            # Clear all signals from all queues
            redis.redis_sync.delete('live_trading_signals')
            redis.redis_sync.delete('fast_signals')
            redis.redis_sync.delete('tactical_signals')
            redis.redis_sync.delete('hft_signals')
            
            print(f"✅ Cleared all old signals")
            print(f"💡 Strategy engine can now generate new signals")
        else:
            print(f"✅ All signals are recent, no need to clear")
    else:
        print(f"✅ No signals to clear")
    
    # Verify clearing worked
    print(f"\n📊 VERIFICATION:")
    new_live_count = redis.redis_sync.llen('live_trading_signals')
    new_fast_count = redis.redis_sync.llen('fast_signals')
    new_tactical_count = redis.redis_sync.llen('tactical_signals')
    
    print(f"  Live Trading Signals: {new_live_count}")
    print(f"  Fast Signals: {new_fast_count}")
    print(f"  Tactical Signals: {new_tactical_count}")
    
    print(f"\n" + "=" * 50)
    print("💡 NEXT STEPS:")
    print("1. Strategy engine should now generate new signals")
    print("2. Execution engine should process them")
    print("3. Check trading activity in a few minutes")

if __name__ == "__main__":
    clear_old_signals()

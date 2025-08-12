#!/usr/bin/env python3
import redis
import json

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

print("=== AGENT STATUS CHECK ===")
print()

# Check all agent stats
print("Agent Status:")
agent_stats_keys = [k.decode() for k in r.keys('agent_stats:*')]
for key in agent_stats_keys:
    agent = key.replace('agent_stats:', '')
    status = r.hget(key, 'status')
    print(f"  {agent}: {status.decode() if status else 'No status'}")

print()

# Check heartbeats
print("Agent Heartbeats:")
heartbeat_keys = [k.decode() for k in r.keys('heartbeat:*')]
for key in heartbeat_keys:
    agent = key.replace('heartbeat:', '')
    timestamp = r.get(key)
    print(f"  {agent}: {timestamp.decode() if timestamp else 'No timestamp'}")

print()

# Check market data symbols
print("Market Data Symbols:")
market_data_keys = [k.decode() for k in r.keys('market_data:*')]
for key in market_data_keys:
    symbol = key.replace('market_data:', '')
    data = r.hgetall(key)
    if data:
        bid = data.get(b'bid', b'N/A').decode()
        ask = data.get(b'ask', b'N/A').decode()
        timestamp = data.get(b'timestamp', b'N/A').decode()
        print(f"  {symbol}: Bid={bid}, Ask={ask}, Time={timestamp[:10]}...")

print()

# Check missing agents
print("Missing Agents Analysis:")
all_agents = ['core', 'intelligence', 'data_feeds', 'market_conditions', 
               'communication_hub', 'strategy_engine', 'risk_management', 
               'execution', 'validation', 'fees_monitor', 'adapters', 'failure_prevention']

heartbeat_agents = [k.replace('heartbeat:', '') for k in heartbeat_keys]
missing = [a for a in all_agents if a not in heartbeat_agents]

print(f"Expected agents: {len(all_agents)}")
print(f"Running agents: {len(heartbeat_agents)}")
print(f"Missing agents: {missing}")

#!/usr/bin/env python3
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

print("=== CURRENT AGENT STATUS ===")
print()

# Check agent stats
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

# Check missing agents
all_agents = ['core', 'intelligence', 'data_feeds', 'market_conditions', 
               'communication_hub', 'strategy_engine', 'risk_management', 
               'execution', 'validation', 'fees_monitor', 'adapters', 'failure_prevention']

heartbeat_agents = [k.replace('heartbeat:', '') for k in heartbeat_keys]
missing = [a for a in all_agents if a not in heartbeat_agents]

print(f"Expected agents: {len(all_agents)}")
print(f"Running agents: {len(heartbeat_agents)}")
print(f"Missing agents: {missing}")

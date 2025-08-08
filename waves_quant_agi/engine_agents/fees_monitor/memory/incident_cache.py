import time
import json
from typing import Dict, Any, List, Optional
import redis
from collections import defaultdict

class IncidentCache:
    """Cache for storing and managing incidents in the fees monitor agent."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, max_incidents: int = 1000):
        self.redis_client = redis_client
        self.max_incidents = max_incidents
        self.local_cache = defaultdict(list)  # Fallback local cache
        
    def store_incident(self, incident: Dict[str, Any]) -> bool:
        """Store an incident in Redis and local cache."""
        try:
            incident_id = f"incident:{int(time.time())}:{incident.get('type', 'unknown')}"
            
            # Add timestamp if not present
            if 'timestamp' not in incident:
                incident['timestamp'] = int(time.time())
                
            # Store in Redis
            if self.redis_client:
                self.redis_client.hset(incident_id, mapping=incident)
                self.redis_client.expire(incident_id, 86400)  # 24 hours
                
                # Add to incident list
                incident_list_key = "fees_monitor:incidents"
                self.redis_client.lpush(incident_list_key, incident_id)
                self.redis_client.ltrim(incident_list_key, 0, self.max_incidents - 1)
            
            # Store in local cache
            incident_type = incident.get('type', 'unknown')
            self.local_cache[incident_type].append(incident)
            
            # Trim local cache
            if len(self.local_cache[incident_type]) > self.max_incidents:
                self.local_cache[incident_type] = self.local_cache[incident_type][-self.max_incidents:]
                
            return True
            
        except Exception as e:
            # Fallback to local cache only
            incident_type = incident.get('type', 'unknown')
            self.local_cache[incident_type].append(incident)
            return False
    
    def get_incidents(self, incident_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve incidents from cache."""
        try:
            incidents = []
            
            if self.redis_client and incident_type is None:
                # Get from Redis
                incident_list_key = "fees_monitor:incidents"
                incident_ids = self.redis_client.lrange(incident_list_key, 0, limit - 1)
                
                for incident_id in incident_ids:
                    incident_data = self.redis_client.hgetall(incident_id)
                    if incident_data:
                        incidents.append(incident_data)
                        
            elif incident_type:
                # Get specific type from local cache
                incidents = self.local_cache.get(incident_type, [])[-limit:]
                
            return incidents
            
        except Exception as e:
            # Fallback to local cache
            if incident_type:
                return self.local_cache.get(incident_type, [])[-limit:]
            else:
                all_incidents = []
                for incident_list in self.local_cache.values():
                    all_incidents.extend(incident_list)
                return sorted(all_incidents, key=lambda x: x.get('timestamp', 0), reverse=True)[:limit]
    
    def get_recent_incidents(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get incidents from the last N hours."""
        cutoff_time = int(time.time()) - (hours * 3600)
        
        try:
            if self.redis_client:
                # Get from Redis with time filter
                incident_list_key = "fees_monitor:incidents"
                incident_ids = self.redis_client.lrange(incident_list_key, 0, -1)
                
                recent_incidents = []
                for incident_id in incident_ids:
                    incident_data = self.redis_client.hgetall(incident_id)
                    if incident_data and int(incident_data.get('timestamp', 0)) >= cutoff_time:
                        recent_incidents.append(incident_data)
                        
                return recent_incidents
                
        except Exception as e:
            pass
            
        # Fallback to local cache
        all_incidents = []
        for incident_list in self.local_cache.values():
            all_incidents.extend(incident_list)
            
        return [
            incident for incident in all_incidents 
            if incident.get('timestamp', 0) >= cutoff_time
        ]
    
    def clear_old_incidents(self, days: int = 7) -> int:
        """Clear incidents older than N days."""
        cutoff_time = int(time.time()) - (days * 86400)
        cleared_count = 0
        
        try:
            if self.redis_client:
                # Clear from Redis
                incident_list_key = "fees_monitor:incidents"
                incident_ids = self.redis_client.lrange(incident_list_key, 0, -1)
                
                for incident_id in incident_ids:
                    incident_data = self.redis_client.hgetall(incident_id)
                    if incident_data and int(incident_data.get('timestamp', 0)) < cutoff_time:
                        self.redis_client.delete(incident_id)
                        self.redis_client.lrem(incident_list_key, 0, incident_id)
                        cleared_count += 1
                        
        except Exception as e:
            pass
            
        # Clear from local cache
        for incident_type in list(self.local_cache.keys()):
            original_count = len(self.local_cache[incident_type])
            self.local_cache[incident_type] = [
                incident for incident in self.local_cache[incident_type]
                if incident.get('timestamp', 0) >= cutoff_time
            ]
            cleared_count += original_count - len(self.local_cache[incident_type])
            
        return cleared_count
    
    def get_incident_stats(self) -> Dict[str, Any]:
        """Get statistics about stored incidents."""
        try:
            stats = {
                'total_incidents': 0,
                'incidents_by_type': {},
                'recent_incidents_24h': 0,
                'recent_incidents_7d': 0
            }
            
            # Count from local cache
            for incident_type, incidents in self.local_cache.items():
                stats['incidents_by_type'][incident_type] = len(incidents)
                stats['total_incidents'] += len(incidents)
            
            # Get recent counts
            recent_24h = self.get_recent_incidents(24)
            recent_7d = self.get_recent_incidents(168)  # 7 days
            
            stats['recent_incidents_24h'] = len(recent_24h)
            stats['recent_incidents_7d'] = len(recent_7d)
            
            return stats
            
        except Exception as e:
            return {
                'total_incidents': 0,
                'incidents_by_type': {},
                'recent_incidents_24h': 0,
                'recent_incidents_7d': 0,
                'error': str(e)
            } 
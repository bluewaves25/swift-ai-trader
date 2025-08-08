import redis
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..logs.failure_agent_logger import FailureAgentLogger

class IncidentCache:
    """
    Enhanced incident cache for storing and managing failure incidents.
    Provides Redis-based storage with fallback and comprehensive incident tracking.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = FailureAgentLogger()
        
        # Redis configuration
        redis_host = self.config.get('redis_host', 'localhost')
        redis_port = self.config.get('redis_port', 6379)
        redis_db = self.config.get('redis_db', 0)
        
        # Initialize Redis
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db, 
                decode_responses=True
            )
            self.redis_client.ping()  # Test connection
            self.logger.log_info("IncidentCache Redis connection established")
        except Exception as e:
            self.logger.log_error("Redis connection failed", str(e), "IncidentCache")
            self.redis_client = None
        
        # Cache settings
        self.key_prefix = "failure_incident:"
        self.expiration_days = self.config.get('expiration_days', 7)
        self.max_incidents = self.config.get('max_incidents', 10000)
        
        # Local fallback cache
        self.local_cache = {}
    
    def store_incident(self, incident: Dict[str, Any]) -> bool:
        """Store incident in Redis with enhanced error handling"""
        try:
            # Generate unique key
            timestamp = incident.get('timestamp', int(time.time()))
            incident_type = incident.get('type', 'unknown')
            source = incident.get('source', 'unknown')
            
            key = f"{self.key_prefix}{timestamp}:{incident_type}:{source}"
            
            # Add metadata
            incident['stored_at'] = timestamp
            incident['key'] = key
            
            # Store in Redis
            if self.redis_client:
                self.redis_client.hset(key, mapping=incident)
                self.redis_client.expire(key, self.expiration_days * 86400)  # Convert days to seconds
                
                # Add to recent incidents list
                self.redis_client.lpush('failure_prevention:recent_incidents', key)
                self.redis_client.ltrim('failure_prevention:recent_incidents', 0, self.max_incidents - 1)
                
                self.logger.log_incident(
                    incident_type=incident_type,
                    source=source,
                    description=incident.get('description', 'No description'),
                    failure_count=incident.get('failure_count', 0),
                    recovery_action=incident.get('recovery_action'),
                    metadata=incident
                )
                return True
            else:
                # Fallback to local cache
                self.local_cache[key] = incident
                self.logger.log_warning(f"Using local cache for incident: {key}")
                return True
                
        except Exception as e:
            self.logger.log_error("Failed to store incident", str(e), "IncidentCache")
            return False
    
    def retrieve_incidents(self, key_pattern: str = "*", limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve incidents from Redis with enhanced filtering"""
        try:
            incidents = []
            
            if self.redis_client:
                # Get keys matching pattern
                pattern = f"{self.key_prefix}{key_pattern}"
                keys = self.redis_client.keys(pattern)
                
                # Limit results for performance
                keys = keys[:limit]
                
                for key in keys:
                    try:
                        data = self.redis_client.hgetall(key)
                        if data:
                            # Convert numeric fields
                            for field in ['timestamp', 'value', 'threshold', 'risk_score', 'confidence', 'failure_count']:
                                if field in data and data[field]:
                                    try:
                                        data[field] = float(data[field])
                                    except ValueError:
                                        pass
                            
                            incidents.append(data)
                    except Exception as e:
                        self.logger.log_error(f"Failed to retrieve incident {key}", str(e), "IncidentCache")
                        continue
                
                self.logger.log_info(f"Retrieved {len(incidents)} incidents for pattern {key_pattern}")
            else:
                # Fallback to local cache
                for key, incident in self.local_cache.items():
                    if key_pattern in key:
                        incidents.append(incident)
                        if len(incidents) >= limit:
                            break
                
                self.logger.log_info(f"Retrieved {len(incidents)} incidents from local cache")
            
            return incidents
            
        except Exception as e:
            self.logger.log_error("Failed to retrieve incidents", str(e), "IncidentCache")
            return []
    
    def get_incident_by_id(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific incident by ID"""
        try:
            if self.redis_client:
                data = self.redis_client.hgetall(incident_id)
                if data:
                    return data
            else:
                return self.local_cache.get(incident_id)
            
            return None
            
        except Exception as e:
            self.logger.log_error(f"Failed to get incident {incident_id}", str(e), "IncidentCache")
            return None
    
    def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing incident"""
        try:
            if self.redis_client:
                self.redis_client.hset(incident_id, mapping=updates)
                self.logger.log_info(f"Updated incident: {incident_id}")
                return True
            else:
                if incident_id in self.local_cache:
                    self.local_cache[incident_id].update(updates)
                    self.logger.log_info(f"Updated incident in local cache: {incident_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.log_error(f"Failed to update incident {incident_id}", str(e), "IncidentCache")
            return False
    
    def delete_incident(self, incident_id: str) -> bool:
        """Delete an incident"""
        try:
            if self.redis_client:
                result = self.redis_client.delete(incident_id)
                if result:
                    self.logger.log_info(f"Deleted incident: {incident_id}")
                    return True
            else:
                if incident_id in self.local_cache:
                    del self.local_cache[incident_id]
                    self.logger.log_info(f"Deleted incident from local cache: {incident_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.log_error(f"Failed to delete incident {incident_id}", str(e), "IncidentCache")
            return False
    
    def get_recent_incidents(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get incidents from the last N hours"""
        try:
            cutoff_time = int(time.time()) - (hours * 3600)
            incidents = []
            
            if self.redis_client:
                # Get recent incident keys
                recent_keys = self.redis_client.lrange('failure_prevention:recent_incidents', 0, -1)
                
                for key in recent_keys:
                    try:
                        data = self.redis_client.hgetall(key)
                        if data and 'timestamp' in data:
                            incident_time = float(data['timestamp'])
                            if incident_time >= cutoff_time:
                                incidents.append(data)
                    except Exception as e:
                        continue
            else:
                # Fallback to local cache
                for key, incident in self.local_cache.items():
                    if 'timestamp' in incident:
                        incident_time = float(incident['timestamp'])
                        if incident_time >= cutoff_time:
                            incidents.append(incident)
            
            # Sort by timestamp (newest first)
            incidents.sort(key=lambda x: float(x.get('timestamp', 0)), reverse=True)
            
            self.logger.log_info(f"Retrieved {len(incidents)} recent incidents (last {hours}h)")
            return incidents
            
        except Exception as e:
            self.logger.log_error("Failed to get recent incidents", str(e), "IncidentCache")
            return []
    
    def get_incident_stats(self) -> Dict[str, Any]:
        """Get statistics about stored incidents"""
        try:
            stats = {
                'total_incidents': 0,
                'incidents_by_type': {},
                'incidents_by_source': {},
                'recent_incidents_24h': 0,
                'recent_incidents_7d': 0
            }
            
            if self.redis_client:
                # Get all incident keys
                keys = self.redis_client.keys(f"{self.key_prefix}*")
                stats['total_incidents'] = len(keys)
                
                # Analyze incidents
                for key in keys[:1000]:  # Limit for performance
                    try:
                        data = self.redis_client.hgetall(key)
                        if data:
                            incident_type = data.get('type', 'unknown')
                            source = data.get('source', 'unknown')
                            
                            stats['incidents_by_type'][incident_type] = stats['incidents_by_type'].get(incident_type, 0) + 1
                            stats['incidents_by_source'][source] = stats['incidents_by_source'].get(source, 0) + 1
                    except Exception as e:
                        continue
                
                # Get recent counts
                recent_24h = self.get_recent_incidents(24)
                recent_7d = self.get_recent_incidents(168)  # 7 days
                
                stats['recent_incidents_24h'] = len(recent_24h)
                stats['recent_incidents_7d'] = len(recent_7d)
            else:
                # Local cache stats
                stats['total_incidents'] = len(self.local_cache)
                
                for incident in self.local_cache.values():
                    incident_type = incident.get('type', 'unknown')
                    source = incident.get('source', 'unknown')
                    
                    stats['incidents_by_type'][incident_type] = stats['incidents_by_type'].get(incident_type, 0) + 1
                    stats['incidents_by_source'][source] = stats['incidents_by_source'].get(source, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.log_error("Failed to get incident stats", str(e), "IncidentCache")
            return {'error': str(e)}
    
    def cleanup_old_incidents(self, days: int = 7) -> int:
        """Clean up incidents older than specified days"""
        try:
            cutoff_time = int(time.time()) - (days * 86400)
            deleted_count = 0
            
            if self.redis_client:
                keys = self.redis_client.keys(f"{self.key_prefix}*")
                
                for key in keys:
                    try:
                        data = self.redis_client.hgetall(key)
                        if data and 'timestamp' in data:
                            incident_time = float(data['timestamp'])
                            if incident_time < cutoff_time:
                                self.redis_client.delete(key)
                                deleted_count += 1
                    except Exception as e:
                        continue
                
                self.logger.log_info(f"Cleaned up {deleted_count} old incidents")
            else:
                # Clean local cache
                keys_to_delete = []
                for key, incident in self.local_cache.items():
                    if 'timestamp' in incident:
                        incident_time = float(incident['timestamp'])
                        if incident_time < cutoff_time:
                            keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.local_cache[key]
                    deleted_count += 1
                
                self.logger.log_info(f"Cleaned up {deleted_count} old incidents from local cache")
            
            return deleted_count
            
        except Exception as e:
            self.logger.log_error("Failed to cleanup old incidents", str(e), "IncidentCache")
            return 0
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
            return False
        except:
            return False
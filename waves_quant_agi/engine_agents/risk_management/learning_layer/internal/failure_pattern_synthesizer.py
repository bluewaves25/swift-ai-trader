from typing import Dict, Any, List
import time
import pandas as pd
from sklearn.cluster import KMeans

class FailurePatternSynthesizer:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
        self.num_clusters = config.get("num_clusters", 3)

    async def cluster_failures(self, incident_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Cluster failure patterns for targeted retraining."""
        try:
            failure_clusters = []
            for risk_type in incident_data["type"].unique():
                type_data = incident_data[incident_data["type"] == risk_type]
                if len(type_data) < self.num_clusters:
                    continue

                features = type_data[["timestamp", "risk_score"]].fillna(0)
                kmeans = KMeans(n_clusters=self.num_clusters, random_state=42)
                clusters = kmeans.fit_predict(features)

                for cluster_id in range(self.num_clusters):
                    cluster_data = type_data.iloc[clusters == cluster_id]
                    if not cluster_data.empty:
                        cluster = {
                            "type": "failure_cluster",
                            "risk_type": risk_type,
                            "cluster_id": cluster_id,
                            "cluster_size": len(cluster_data),
                            "timestamp": int(time.time()),
                            "description": f"Clustered {len(cluster_data)} failures for {risk_type} in cluster {cluster_id}"
                        }
                        failure_clusters.append(cluster)
                        
                        redis_client = await self.connection_manager.get_redis_client()
                        if redis_client:
                            redis_client.set(f"risk_management:failure_cluster:{risk_type}:{cluster_id}", str(cluster), ex=604800)
                        await self.notify_retraining(cluster)

            summary = {
                "type": "failure_cluster_summary",
                "cluster_count": len(failure_clusters),
                "timestamp": int(time.time()),
                "description": f"Clustered {len(failure_clusters)} failure patterns"
            }
            
            await self.notify_core(summary)
            return failure_clusters
        except Exception as e:
            print(f"Error in failure pattern synthesizer: {e}")
            return []

    async def notify_retraining(self, cluster: Dict[str, Any]):
        """Notify Retraining Module of clustered failure patterns."""
        print(f"Notifying Retraining Module: {cluster.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("retraining_module", str(cluster))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of failure clustering results."""
        print(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))
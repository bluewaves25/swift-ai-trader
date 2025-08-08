import asyncio
import time
from typing import Dict, Any, Optional, List
import redis
from .logs.intelligence_logger import IntelligenceLogger
from .pattern_recognition.correlation_matrix import CorrelationMatrix
from .pattern_recognition.anomaly_detector import AnomalyDetector
from .gnn_models.agent_graph_builder import AgentGraphBuilder
from .gnn_models.coordination_gnn import CoordinationGNN
from .online_learning.agent_feedback_trainer import AgentFeedbackTrainer
from .online_learning.reinforcement_scorer import ReinforcementScorer
from .transformers.inter_agent_transformer import InterAgentTransformer
from .transformers.conflict_resolver import ConflictResolver
from .learning_layer.internal.research_engine import ResearchEngine
from .learning_layer.internal.training_module import TrainingModule

class IntelligenceAgent:
    """Main orchestrator for all AI/ML intelligence components with advanced pattern recognition and learning."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Initialize Redis connection
        self.redis_client = self._init_redis()
        self.logger = IntelligenceLogger("intelligence_agent", self.redis_client)
        
        # Initialize pattern recognition components
        self._init_pattern_recognition()
        
        # Initialize GNN models
        self._init_gnn_models()
        
        # Initialize online learning components
        self._init_online_learning()
        
        # Initialize transformers
        self._init_transformers()
        
        # Initialize learning layer
        self._init_learning_layer()
        
        # Performance tracking
        self.stats = {
            "total_analyses": 0,
            "patterns_detected": 0,
            "anomalies_found": 0,
            "predictions_made": 0,
            "learning_sessions": 0,
            "start_time": time.time(),
            "last_analysis_time": 0
        }

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            return redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                decode_responses=True
            )
        except Exception as e:
            self.logger.log_error(f"Failed to initialize Redis: {e}")
            return None

    def _init_pattern_recognition(self):
        """Initialize pattern recognition components."""
        try:
            pattern_config = self.config.get("pattern_recognition", {})
            
            self.correlation_matrix = CorrelationMatrix(pattern_config)
            self.anomaly_detector = AnomalyDetector(pattern_config)
            
            self.logger.log_info("Pattern recognition components initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing pattern recognition: {e}")

    def _init_gnn_models(self):
        """Initialize GNN model components."""
        try:
            gnn_config = self.config.get("gnn_models", {})
            
            self.agent_graph_builder = AgentGraphBuilder(gnn_config)
            self.coordination_gnn = CoordinationGNN(gnn_config)
            
            self.logger.log_info("GNN models initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing GNN models: {e}")

    def _init_online_learning(self):
        """Initialize online learning components."""
        try:
            learning_config = self.config.get("online_learning", {})
            
            self.agent_feedback_trainer = AgentFeedbackTrainer(learning_config)
            self.reinforcement_scorer = ReinforcementScorer(learning_config)
            
            self.logger.log_info("Online learning components initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing online learning: {e}")

    def _init_transformers(self):
        """Initialize transformer components."""
        try:
            transformer_config = self.config.get("transformers", {})
            
            self.inter_agent_transformer = InterAgentTransformer(transformer_config)
            self.conflict_resolver = ConflictResolver(transformer_config)
            
            self.logger.log_info("Transformer components initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing transformers: {e}")

    def _init_learning_layer(self):
        """Initialize learning layer components."""
        try:
            learning_config = self.config.get("learning_layer", {})
            
            self.research_engine = ResearchEngine(learning_config)
            self.training_module = TrainingModule(learning_config)
            
            self.logger.log_info("Learning layer components initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing learning layer: {e}")

    async def start(self):
        """Start the intelligence agent."""
        try:
            self.logger.log_info("Starting Intelligence Agent...")
            self.is_running = True
            
            # Start all analysis tasks
            tasks = [
                asyncio.create_task(self._pattern_analysis_loop()),
                asyncio.create_task(self._anomaly_detection_loop()),
                asyncio.create_task(self._gnn_analysis_loop()),
                asyncio.create_task(self._online_learning_loop()),
                asyncio.create_task(self._transformer_analysis_loop()),
                asyncio.create_task(self._learning_layer_loop()),
                asyncio.create_task(self._stats_reporting_loop())
            ]
            
            # Start all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.log_error(f"Error starting intelligence agent: {e}")
            await self.stop()

    async def stop(self):
        """Stop the intelligence agent gracefully."""
        self.logger.log_info("Stopping Intelligence Agent...")
        self.is_running = False
        
        try:
            self.logger.log_info("Intelligence Agent stopped successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error stopping intelligence agent: {e}")

    async def _pattern_analysis_loop(self):
        """Periodic pattern analysis loop."""
        while self.is_running:
            try:
                # Get agent metrics from Redis
                agent_metrics = await self._get_agent_metrics()
                
                if agent_metrics:
                    # Perform correlation analysis
                    correlations = await self.correlation_matrix.build_correlation_matrix(agent_metrics)
                    
                    if correlations:
                        self.stats["patterns_detected"] += 1
                        self.logger.log_pattern("correlation_analysis", correlations)
                        
                        # Generate insights
                        insights = await self.correlation_matrix.get_correlation_insights(correlations)
                        for insight in insights:
                            self.logger.log_info(f"Correlation insight: {insight}")
                
                await asyncio.sleep(self.config.get("pattern_analysis_interval", 300))
                
            except Exception as e:
                self.logger.log_error(f"Error in pattern analysis loop: {e}")
                await asyncio.sleep(60)

    async def _anomaly_detection_loop(self):
        """Periodic anomaly detection loop."""
        while self.is_running:
            try:
                # Get agent metrics from Redis
                agent_metrics = await self._get_agent_metrics()
                
                if agent_metrics:
                    # Perform anomaly detection
                    anomalies = await self.anomaly_detector.detect_anomalies(agent_metrics)
                    
                    if anomalies:
                        self.stats["anomalies_found"] += len(anomalies)
                        self.logger.log_anomaly("anomaly_detection", {
                            "anomaly_count": len(anomalies),
                            "anomalies": anomalies
                        })
                        
                        # Generate insights
                        insights = await self.anomaly_detector.get_anomaly_insights(anomalies)
                        for insight in insights:
                            self.logger.log_info(f"Anomaly insight: {insight}")
                
                await asyncio.sleep(self.config.get("anomaly_detection_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in anomaly detection loop: {e}")
                await asyncio.sleep(30)

    async def _gnn_analysis_loop(self):
        """Periodic GNN analysis loop."""
        while self.is_running:
            try:
                # Build agent graph
                agent_graph = await self.agent_graph_builder.build_graph()
                
                if agent_graph:
                    # Analyze coordination patterns
                    coordination_analysis = await self.coordination_gnn.analyze_coordination(agent_graph)
                    
                    if coordination_analysis:
                        self.logger.log_pattern("gnn_coordination", coordination_analysis)
                
                await asyncio.sleep(self.config.get("gnn_analysis_interval", 600))
                
            except Exception as e:
                self.logger.log_error(f"Error in GNN analysis loop: {e}")
                await asyncio.sleep(60)

    async def _online_learning_loop(self):
        """Periodic online learning loop."""
        while self.is_running:
            try:
                # Get feedback data
                feedback_data = await self._get_feedback_data()
                
                if feedback_data:
                    # Train on feedback
                    training_result = await self.agent_feedback_trainer.train_on_feedback(feedback_data)
                    
                    if training_result:
                        self.stats["learning_sessions"] += 1
                        self.logger.log_learning("feedback_training", training_result)
                    
                    # Update reinforcement scores
                    scoring_result = await self.reinforcement_scorer.update_scores(feedback_data)
                    
                    if scoring_result:
                        self.logger.log_learning("reinforcement_scoring", scoring_result)
                
                await asyncio.sleep(self.config.get("online_learning_interval", 1800))
                
            except Exception as e:
                self.logger.log_error(f"Error in online learning loop: {e}")
                await asyncio.sleep(300)

    async def _transformer_analysis_loop(self):
        """Periodic transformer analysis loop."""
        while self.is_running:
            try:
                # Get agent interactions
                agent_interactions = await self._get_agent_interactions()
                
                if agent_interactions:
                    # Analyze inter-agent patterns
                    interaction_analysis = await self.inter_agent_transformer.analyze_interactions(agent_interactions)
                    
                    if interaction_analysis:
                        self.logger.log_pattern("inter_agent_analysis", interaction_analysis)
                    
                    # Resolve conflicts
                    conflicts = await self.conflict_resolver.detect_conflicts(agent_interactions)
                    
                    if conflicts:
                        resolution_result = await self.conflict_resolver.resolve_conflicts(conflicts)
                        self.logger.log_pattern("conflict_resolution", resolution_result)
                
                await asyncio.sleep(self.config.get("transformer_analysis_interval", 900))
                
            except Exception as e:
                self.logger.log_error(f"Error in transformer analysis loop: {e}")
                await asyncio.sleep(120)

    async def _learning_layer_loop(self):
        """Periodic learning layer loop."""
        while self.is_running:
            try:
                # Research new patterns
                research_result = await self.research_engine.research_patterns()
                
                if research_result:
                    self.logger.log_learning("pattern_research", research_result)
                
                # Update training models
                training_result = await self.training_module.update_models()
                
                if training_result:
                    self.logger.log_learning("model_training", training_result)
                
                await asyncio.sleep(self.config.get("learning_layer_interval", 3600))
                
            except Exception as e:
                self.logger.log_error(f"Error in learning layer loop: {e}")
                await asyncio.sleep(600)

    async def _stats_reporting_loop(self):
        """Periodic stats reporting loop."""
        while self.is_running:
            try:
                await self._report_stats()
                await asyncio.sleep(self.config.get("stats_interval", 300))
                
            except Exception as e:
                self.logger.log_error(f"Error in stats reporting loop: {e}")
                await asyncio.sleep(60)

    async def _get_agent_metrics(self) -> List[Dict[str, Any]]:
        """Get agent metrics from Redis."""
        try:
            if not self.redis_client:
                return []
            
            # Get metrics from Redis
            metrics_keys = self.redis_client.keys("agent_metrics:*")
            metrics = []
            
            for key in metrics_keys:
                try:
                    metric_data = self.redis_client.hgetall(key)
                    if metric_data:
                        metrics.append(metric_data)
                except Exception as e:
                    self.logger.log_error(f"Error getting metric from {key}: {e}")
                    continue
            
            return metrics
            
        except Exception as e:
            self.logger.log_error(f"Error getting agent metrics: {e}")
            return []

    async def _get_feedback_data(self) -> List[Dict[str, Any]]:
        """Get feedback data from Redis."""
        try:
            if not self.redis_client:
                return []
            
            # Get feedback from Redis
            feedback_keys = self.redis_client.keys("agent_feedback:*")
            feedback_data = []
            
            for key in feedback_keys:
                try:
                    feedback = self.redis_client.hgetall(key)
                    if feedback:
                        feedback_data.append(feedback)
                except Exception as e:
                    self.logger.log_error(f"Error getting feedback from {key}: {e}")
                    continue
            
            return feedback_data
            
        except Exception as e:
            self.logger.log_error(f"Error getting feedback data: {e}")
            return []

    async def _get_agent_interactions(self) -> List[Dict[str, Any]]:
        """Get agent interactions from Redis."""
        try:
            if not self.redis_client:
                return []
            
            # Get interactions from Redis
            interaction_keys = self.redis_client.keys("agent_interactions:*")
            interactions = []
            
            for key in interaction_keys:
                try:
                    interaction = self.redis_client.hgetall(key)
                    if interaction:
                        interactions.append(interaction)
                except Exception as e:
                    self.logger.log_error(f"Error getting interaction from {key}: {e}")
                    continue
            
            return interactions
            
        except Exception as e:
            self.logger.log_error(f"Error getting agent interactions: {e}")
            return []

    async def _report_stats(self):
        """Report agent statistics."""
        try:
            uptime = time.time() - self.stats["start_time"]
            
            stats_report = {
                "uptime_seconds": uptime,
                "total_analyses": self.stats["total_analyses"],
                "patterns_detected": self.stats["patterns_detected"],
                "anomalies_found": self.stats["anomalies_found"],
                "predictions_made": self.stats["predictions_made"],
                "learning_sessions": self.stats["learning_sessions"],
                "analyses_per_hour": self.stats["total_analyses"] / max(uptime / 3600, 1),
                "last_analysis_time": self.stats["last_analysis_time"],
                "timestamp": time.time()
            }
            
            # Store stats in Redis
            if self.redis_client:
                self.redis_client.hset("intelligence:stats", mapping=stats_report)
            
            # Log metrics
            self.logger.log_metric("total_analyses", self.stats["total_analyses"])
            self.logger.log_metric("patterns_detected", self.stats["patterns_detected"])
            self.logger.log_metric("anomalies_found", self.stats["anomalies_found"])
            
        except Exception as e:
            self.logger.log_error(f"Error reporting stats: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "stats": self.stats,
            "components": {
                "correlation_matrix": hasattr(self, 'correlation_matrix'),
                "anomaly_detector": hasattr(self, 'anomaly_detector'),
                "agent_graph_builder": hasattr(self, 'agent_graph_builder'),
                "coordination_gnn": hasattr(self, 'coordination_gnn'),
                "agent_feedback_trainer": hasattr(self, 'agent_feedback_trainer'),
                "reinforcement_scorer": hasattr(self, 'reinforcement_scorer'),
                "inter_agent_transformer": hasattr(self, 'inter_agent_transformer'),
                "conflict_resolver": hasattr(self, 'conflict_resolver'),
                "research_engine": hasattr(self, 'research_engine'),
                "training_module": hasattr(self, 'training_module')
            }
        } 
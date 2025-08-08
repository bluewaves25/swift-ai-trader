import asyncio
import time
from typing import Dict, Any, Optional
import redis
from .logs.failure_agent_logger import FailureAgentLogger
from .memory.incident_cache import IncidentCache
from .broker_fee_models.model_loader import ModelLoader
from .cost_optimizer.smart_sizer import SmartSizer
from .cost_optimizer.execution_recommender import ExecutionRecommender
from .cost_optimizer.fee_strategy_map import FeeStrategyMap
from .slippage_tracker.slippage_detector import SlippageDetector
from .slippage_tracker.execution_delta import ExecutionDelta
from .slippage_tracker.variance_analyzer import VarianceAnalyzer
from .profitability_audit.pnl_adjuster import PnlAdjuster
from .profitability_audit.hidden_fee_detector import HiddenFeeDetector
from .profitability_audit.true_profit_reporter import TrueProfitReporter

class FeesMonitorAgent:
    """Main orchestrator for the fees monitor system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Initialize Redis connection
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        
        # Initialize core components
        self.logger = FailureAgentLogger("fees_monitor_agent", self.redis_client)
        self.cache = IncidentCache(self.redis_client)
        self.model_loader = ModelLoader(config, self.logger, self.cache)
        
        # Initialize fee optimization components
        self.smart_sizer = SmartSizer(config, self.logger, self.cache, self.model_loader)
        self.execution_recommender = ExecutionRecommender(config, self.logger, self.cache, self.model_loader)
        self.fee_strategy_map = FeeStrategyMap(config, self.logger, self.cache, self.model_loader)
        
        # Initialize slippage tracking components
        self.slippage_detector = SlippageDetector(config, self.logger, self.cache)
        self.execution_delta = ExecutionDelta(config, self.logger, self.cache)
        self.variance_analyzer = VarianceAnalyzer(config, self.logger, self.cache)
        
        # Initialize profitability audit components
        self.pnl_adjuster = PnlAdjuster(config, self.logger, self.cache, self.model_loader)
        self.hidden_fee_detector = HiddenFeeDetector(config, self.logger, self.cache, self.model_loader)
        self.true_profit_reporter = TrueProfitReporter(config, self.logger, self.cache)
        
        # Initialize learning components
        self._initialize_learning_components()
        
        # Performance tracking
        self.stats = {
            "total_trades_processed": 0,
            "total_fee_savings": 0.0,
            "total_slippage_detected": 0,
            "total_hidden_fees_found": 0,
            "start_time": time.time()
        }

    def _initialize_learning_components(self):
        """Initialize learning layer components."""
        try:
            from .learning_layer.internal.research_engine import ResearchEngine
            from .learning_layer.internal.training_module import TrainingModule
            from .learning_layer.internal.retraining_loop import RetrainingLoop
            from .learning_layer.external.web_intelligence.broker_scraper import BrokerScraper
            from .learning_layer.external.web_intelligence.forum_checker import ForumChecker
            from .learning_layer.external.web_intelligence.regulation_monitor import RegulationMonitor
            from .learning_layer.external.social_analyzer.fee_sentiment_processor import FeeSentimentProcessor
            from .learning_layer.external.social_analyzer.trend_correlator import TrendCorrelator
            from .learning_layer.external.intelligence_fusion.cost_pattern_synthesizer import CostPatternSynthesizer
            from .learning_layer.external.intelligence_fusion.anomaly_predictor import AnomalyPredictor
            from .learning_layer.hybrid_training.fee_trainer import FeeTrainer
            from .learning_layer.hybrid_training.external_fee_validator import ExternalFeeValidator
            
            # Initialize learning components
            self.research_engine = ResearchEngine(self.config, self.logger, self.cache)
            self.training_module = TrainingModule(self.config, self.logger, self.cache, self.research_engine)
            self.retraining_loop = RetrainingLoop(self.config, self.logger, self.cache, self.training_module)
            
            # Initialize external intelligence
            self.broker_scraper = BrokerScraper(self.config, self.logger, self.cache, self.model_loader)
            self.forum_checker = ForumChecker(self.config, self.logger, self.cache)
            self.regulation_monitor = RegulationMonitor(self.config, self.logger, self.cache, self.model_loader)
            
            # Initialize social analysis
            self.fee_sentiment_processor = FeeSentimentProcessor(self.config, self.logger, self.cache)
            self.trend_correlator = TrendCorrelator(self.config, self.logger, self.cache)
            
            # Initialize intelligence fusion
            self.cost_pattern_synthesizer = CostPatternSynthesizer(self.config, self.logger, self.cache, self.research_engine)
            self.anomaly_predictor = AnomalyPredictor(self.config, self.logger, self.cache, self.cost_pattern_synthesizer)
            
            # Initialize hybrid training
            self.fee_trainer = FeeTrainer(self.config, self.logger, self.cache, self.research_engine, self.cost_pattern_synthesizer)
            self.external_fee_validator = ExternalFeeValidator(self.config, self.logger, self.cache, self.broker_scraper, self.fee_sentiment_processor)
            
            self.logger.log("Learning components initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing learning components: {e}")
            # Set components to None if they fail to initialize
            self.research_engine = None
            self.training_module = None
            self.retraining_loop = None
            self.broker_scraper = None
            self.forum_checker = None
            self.regulation_monitor = None
            self.fee_sentiment_processor = None
            self.trend_correlator = None
            self.cost_pattern_synthesizer = None
            self.anomaly_predictor = None
            self.fee_trainer = None
            self.external_fee_validator = None

    async def start(self):
        """Start the fees monitor agent."""
        try:
            self.logger.log("Starting Fees Monitor Agent...")
            self.is_running = True
            
            # Load fee models
            self.model_loader.load_fee_models()
            
            # Start background tasks
            tasks = [
                asyncio.create_task(self._monitor_fees_loop()),
                asyncio.create_task(self._learning_loop()),
                asyncio.create_task(self._stats_reporting_loop())
            ]
            
            # Start all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.log_error(f"Error starting fees monitor agent: {e}")
            await self.stop()

    async def stop(self):
        """Stop the fees monitor agent."""
        self.logger.log("Stopping Fees Monitor Agent...")
        self.is_running = False

    async def _monitor_fees_loop(self):
        """Main loop for monitoring fees and optimizing trades."""
        while self.is_running:
            try:
                # Process fee monitoring tasks
                await self._process_fee_optimization()
                await self._process_slippage_detection()
                await self._process_profitability_audit()
                
                # Wait before next iteration
                await asyncio.sleep(self.config.get("monitor_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in fees monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    async def _learning_loop(self):
        """Background learning and intelligence gathering loop."""
        while self.is_running:
            try:
                if self.research_engine:
                    await self.research_engine.gather_intelligence()
                
                if self.broker_scraper:
                    await self.broker_scraper.scrape_broker_info()
                
                if self.fee_sentiment_processor:
                    await self.fee_sentiment_processor.process_sentiment()
                
                # Wait before next learning cycle
                await asyncio.sleep(self.config.get("learning_interval", 3600))  # 1 hour
                
            except Exception as e:
                self.logger.log_error(f"Error in learning loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def _stats_reporting_loop(self):
        """Report statistics and metrics."""
        while self.is_running:
            try:
                await self._report_stats()
                await asyncio.sleep(self.config.get("stats_interval", 300))  # 5 minutes
                
            except Exception as e:
                self.logger.log_error(f"Error in stats reporting loop: {e}")
                await asyncio.sleep(60)

    async def _process_fee_optimization(self):
        """Process fee optimization tasks."""
        try:
            # Get pending trades from Redis
            pending_trades = self.redis_client.lrange("fees_monitor:pending_trades", 0, 9)
            
            for trade_data in pending_trades:
                try:
                    trade = eval(trade_data)  # Convert string back to dict
                    
                    # Optimize position size
                    optimized_size = await self.smart_sizer.optimize_position_size(trade)
                    
                    # Get execution recommendations
                    recommendations = await self.execution_recommender.get_recommendations(trade)
                    
                    # Update trade with optimizations
                    trade["optimized_size"] = optimized_size
                    trade["recommendations"] = recommendations
                    
                    # Store optimized trade
                    self.redis_client.lpush("fees_monitor:optimized_trades", str(trade))
                    self.redis_client.lrem("fees_monitor:pending_trades", 0, trade_data)
                    
                    self.stats["total_trades_processed"] += 1
                    
                except Exception as e:
                    self.logger.log_error(f"Error processing trade: {e}")
                    
        except Exception as e:
            self.logger.log_error(f"Error in fee optimization: {e}")

    async def _process_slippage_detection(self):
        """Process slippage detection tasks."""
        try:
            # Get recent executions
            recent_executions = self.redis_client.lrange("fees_monitor:recent_executions", 0, 19)
            
            for execution_data in recent_executions:
                try:
                    execution = eval(execution_data)
                    
                    # Detect slippage
                    slippage_info = await self.slippage_detector.detect_slippage(execution)
                    
                    if slippage_info.get("slippage_detected"):
                        self.stats["total_slippage_detected"] += 1
                        self.logger.log_issue(slippage_info)
                    
                    # Calculate execution delta
                    delta = await self.execution_delta.calculate_delta(execution)
                    
                    # Analyze variance
                    variance = await self.variance_analyzer.analyze_variance(execution)
                    
                except Exception as e:
                    self.logger.log_error(f"Error processing execution: {e}")
                    
        except Exception as e:
            self.logger.log_error(f"Error in slippage detection: {e}")

    async def _process_profitability_audit(self):
        """Process profitability audit tasks."""
        try:
            # Get recent trades for audit
            recent_trades = self.redis_client.lrange("fees_monitor:recent_trades", 0, 19)
            
            for trade_data in recent_trades:
                try:
                    trade = eval(trade_data)
                    
                    # Adjust PnL for fees
                    adjusted_pnl = await self.pnl_adjuster.adjust_pnl(trade)
                    
                    # Detect hidden fees
                    hidden_fees = await self.hidden_fee_detector.detect_hidden_fees(trade)
                    
                    if hidden_fees.get("hidden_fees_found"):
                        self.stats["total_hidden_fees_found"] += 1
                        self.logger.log_issue(hidden_fees)
                    
                    # Generate true profit report
                    true_profit = await self.true_profit_reporter.generate_report(trade)
                    
                except Exception as e:
                    self.logger.log_error(f"Error processing trade audit: {e}")
                    
        except Exception as e:
            self.logger.log_error(f"Error in profitability audit: {e}")

    async def _report_stats(self):
        """Report agent statistics."""
        try:
            uptime = time.time() - self.stats["start_time"]
            
            stats_report = {
                "uptime_seconds": uptime,
                "total_trades_processed": self.stats["total_trades_processed"],
                "total_fee_savings": self.stats["total_fee_savings"],
                "total_slippage_detected": self.stats["total_slippage_detected"],
                "total_hidden_fees_found": self.stats["total_hidden_fees_found"],
                "trades_per_second": self.stats["total_trades_processed"] / max(uptime, 1),
                "timestamp": time.time()
            }
            
            # Store stats in Redis
            self.redis_client.hset("fees_monitor:stats", mapping=stats_report)
            
            # Log metrics
            self.logger.log_metric("trades_processed", self.stats["total_trades_processed"])
            self.logger.log_metric("fee_savings", self.stats["total_fee_savings"])
            self.logger.log_metric("slippage_detected", self.stats["total_slippage_detected"])
            self.logger.log_metric("hidden_fees_found", self.stats["total_hidden_fees_found"])
            
        except Exception as e:
            self.logger.log_error(f"Error reporting stats: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "is_running": self.is_running,
            "uptime_seconds": time.time() - self.stats["start_time"],
            "stats": self.stats,
            "components": {
                "model_loader": self.model_loader is not None,
                "smart_sizer": self.smart_sizer is not None,
                "slippage_detector": self.slippage_detector is not None,
                "pnl_adjuster": self.pnl_adjuster is not None,
                "learning_components": all([
                    self.research_engine, self.training_module, self.retraining_loop
                ])
            }
        } 
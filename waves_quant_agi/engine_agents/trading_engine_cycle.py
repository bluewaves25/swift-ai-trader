#!/usr/bin/env python3
"""
Enhanced Trading Engine Cycle Pipeline
Implements a robust 9-step trading cycle with all cleaned agents.
"""

import asyncio
import time
import redis
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Import all our cleaned agents
from .core.core_agent import CoreAgent
from .data_feeds.data_feeds_agent import DataFeedsAgent
from .market_conditions.market_conditions_agent import MarketConditionsAgent
from .intelligence.intelligence_agent import IntelligenceAgent
from .strategy_engine.strategy_engine_agent import StrategyEngineAgent
from .risk_management.risk_management_agent import RiskManagementAgent
from .execution.python_bridge import ExecutionBridge
from .validation.python_bridge import ValidationBridge
from .fees_monitor.fees_monitor_agent import FeesMonitorAgent
from .adapters.adapters_agent import AdaptersAgent
from .failure_prevention.failure_prevention_agent import FailurePreventionAgent

class CycleStage(Enum):
    """Trading cycle stages"""
    INITIALIZE = "initialize"
    SENSE_MARKET = "sense_market"
    ANALYZE_PATTERNS = "analyze_patterns"
    COMPOSE_STRATEGY = "compose_strategy"
    EVALUATE_RISKS = "evaluate_risks"
    EXECUTE_STRATEGY = "execute_strategy"
    MONITOR_HEALTH = "monitor_health"
    LEARN_ADAPT = "learn_adapt"
    LOG_RESET = "log_reset"

@dataclass
class CycleState:
    """Current state of the trading cycle"""
    stage: CycleStage
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class TradingEngineCycle:
    """
    Enhanced Trading Engine Cycle Pipeline
    Orchestrates the complete 9-step trading cycle with all agents.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = self._init_logger()
        
        # Initialize Redis
        self._init_redis()
        
        # Initialize all agents
        self._init_agents()
        
        # Cycle state tracking
        self.current_cycle = None
        self.cycle_history = []
        self.is_running = False
        
        # Performance metrics
        self.metrics = {
            'total_cycles': 0,
            'successful_cycles': 0,
            'failed_cycles': 0,
            'avg_cycle_duration': 0.0,
            'last_cycle_duration': 0.0
        }
        
        # Task management
        self.tasks = []
        
    def _init_logger(self):
        """Initialize cycle logger"""
        from .core.logs.core_agent_logger import CoreAgentLogger
        return CoreAgentLogger("trading_engine_cycle")
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            redis_host = self.config.get('redis_host', 'localhost')
            redis_port = self.config.get('redis_port', 6379)
            redis_db = self.config.get('redis_db', 0)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            self.redis_client.ping()
            self.logger.log_info("Trading Engine Cycle Redis connection established")
            
        except Exception as e:
            self.logger.log_error("Redis connection failed", str(e), "TradingEngineCycle")
            self.redis_client = None
    
    def _init_agents(self):
        """Initialize all trading agents"""
        try:
            # Core orchestrator
            self.core_agent = CoreAgent(self.config)
            
            # Data collection and market sensing
            self.data_feeds_agent = DataFeedsAgent(self.config)
            self.market_conditions_agent = MarketConditionsAgent(self.config)
            
            # Analysis and intelligence
            self.intelligence_agent = IntelligenceAgent(self.config)
            
            # Strategy and risk management
            self.strategy_engine_agent = StrategyEngineAgent(self.config)
            self.risk_management_agent = RiskManagementAgent(self.config)
            
            # Execution and validation
            self.execution_bridge = ExecutionBridge(self.config)
            self.validation_bridge = ValidationBridge(self.config)
            
            # Monitoring and optimization
            self.fees_monitor_agent = FeesMonitorAgent(self.config)
            self.adapters_agent = AdaptersAgent(self.config)
            self.failure_prevention_agent = FailurePreventionAgent(self.config)
            
            self.logger.log_info("All trading agents initialized successfully")
            
        except Exception as e:
            self.logger.log_error("Agent initialization failed", str(e), "TradingEngineCycle")
            raise
    
    async def start_cycle(self):
        """Start the trading engine cycle"""
        try:
            if self.is_running:
                self.logger.log_info("Trading engine cycle is already running")
                return
            
            self.is_running = True
            self.logger.log_system_operation(
                operation="start_cycle",
                component="trading_engine",
                status="initiating"
            )
            
            # Start background monitoring
            self.tasks = [
                asyncio.create_task(self._cycle_monitor()),
                asyncio.create_task(self._health_monitor()),
                asyncio.create_task(self._metrics_reporter())
            ]
            
            # Start the main cycle loop
            await self._run_cycle_loop()
            
        except Exception as e:
            self.logger.log_error("Failed to start trading cycle", str(e), "TradingEngineCycle")
            raise
    
    async def stop_cycle(self):
        """Stop the trading engine cycle"""
        try:
            if not self.is_running:
                self.logger.log_info("Trading engine cycle is not running")
                return
            
            self.logger.log_system_operation(
                operation="stop_cycle",
                component="trading_engine",
                status="initiating"
            )
            
            # Stop background tasks
            for task in self.tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
            self.is_running = False
            
            # Report final metrics
            await self._report_final_metrics()
            
            self.logger.log_system_operation(
                operation="stop_cycle",
                component="trading_engine",
                status="stopped"
            )
            
        except Exception as e:
            self.logger.log_error("Failed to stop trading cycle", str(e), "TradingEngineCycle")
            raise
    
    async def _run_cycle_loop(self):
        """Main cycle execution loop"""
        try:
            self.logger.log_info("Starting trading engine cycle loop")
            
            while self.is_running:
                try:
                    # Execute one complete cycle
                    cycle_result = await self._execute_cycle()
                    
                    # Update metrics
                    self.metrics['total_cycles'] += 1
                    if cycle_result['success']:
                        self.metrics['successful_cycles'] += 1
                    else:
                        self.metrics['failed_cycles'] += 1
                    
                    # Wait for next cycle
                    cycle_interval = self.config.get('cycle_interval', 60)  # Default 1 minute
                    await asyncio.sleep(cycle_interval)
                    
                except Exception as e:
                    self.logger.log_error("Cycle execution error", str(e), "TradingEngineCycle")
                    self.metrics['failed_cycles'] += 1
                    await asyncio.sleep(10)  # Brief pause on error
            
        except asyncio.CancelledError:
            self.logger.log_info("Trading engine cycle loop cancelled")
        except Exception as e:
            self.logger.log_error("Trading engine cycle loop failed", str(e), "TradingEngineCycle")
    
    async def _execute_cycle(self) -> Dict[str, Any]:
        """Execute one complete trading cycle"""
        cycle_start = time.time()
        cycle_state = CycleState(
            stage=CycleStage.INITIALIZE,
            start_time=cycle_start,
            metadata={}
        )
        
        try:
            self.logger.log_info("=== STARTING TRADING CYCLE ===")
            
            # Step 1: Initialize System
            await self._step_1_initialize(cycle_state)
            
            # Step 2: Sense the Market
            await self._step_2_sense_market(cycle_state)
            
            # Step 3: Analyze Patterns
            await self._step_3_analyze_patterns(cycle_state)
            
            # Step 4: Compose Strategy
            await self._step_4_compose_strategy(cycle_state)
            
            # Step 5: Evaluate Risks
            await self._step_5_evaluate_risks(cycle_state)
            
            # Step 6: Execute Strategy
            await self._step_6_execute_strategy(cycle_state)
            
            # Step 7: Monitor Health
            await self._step_7_monitor_health(cycle_state)
            
            # Step 8: Learn & Adapt
            await self._step_8_learn_adapt(cycle_state)
            
            # Step 9: Log & Reset
            await self._step_9_log_reset(cycle_state)
            
            # Complete cycle
            cycle_state.end_time = time.time()
            cycle_state.success = True
            
            duration = cycle_state.end_time - cycle_state.start_time
            self.metrics['last_cycle_duration'] = duration
            
            # Update average duration
            self._update_avg_duration(duration)
            
            self.logger.log_info(f"=== CYCLE COMPLETED SUCCESSFULLY ({duration:.2f}s) ===")
            
            return {"success": True, "duration": duration, "state": cycle_state}
            
        except Exception as e:
            cycle_state.end_time = time.time()
            cycle_state.success = False
            cycle_state.error_message = str(e)
            
            duration = cycle_state.end_time - cycle_state.start_time
            self.logger.log_error(f"=== CYCLE FAILED ({duration:.2f}s): {str(e)} ===")
            
            return {"success": False, "duration": duration, "error": str(e), "state": cycle_state}
    
    async def _step_1_initialize(self, cycle_state: CycleState):
        """Step 1: Initialize System"""
        try:
            cycle_state.stage = CycleStage.INITIALIZE
            self.logger.log_info("Step 1: Initializing System")
            
            # Load configurations
            await self._load_configurations()
            
            # Connect adapters (brokers, data sources)
            await self._connect_adapters()
            
            # Health check: system + infrastructure
            await self._health_check()
            
            self.logger.log_info("Step 1: System initialization completed")
            
        except Exception as e:
            self.logger.log_error("Step 1 failed", str(e), "TradingEngineCycle")
            raise
    
    async def _step_2_sense_market(self, cycle_state: CycleState):
        """Step 2: Sense the Market"""
        try:
            cycle_state.stage = CycleStage.SENSE_MARKET
            self.logger.log_info("Step 2: Sensing Market")
            
            # Data feeds ingestion
            market_data = await self._collect_market_data()
            
            # Market conditions analysis
            market_conditions = await self._analyze_market_conditions(market_data)
            
            # Validate market conditions
            validation_result = await self._validate_market_conditions(market_conditions)
            
            cycle_state.metadata['market_data'] = market_data
            cycle_state.metadata['market_conditions'] = market_conditions
            cycle_state.metadata['validation_result'] = validation_result
            
            self.logger.log_info("Step 2: Market sensing completed")
            
        except Exception as e:
            self.logger.log_error("Step 2 failed", str(e), "TradingEngineCycle")
            raise
    
    async def _step_3_analyze_patterns(self, cycle_state: CycleState):
        """Step 3: Analyze + Detect Patterns"""
        try:
            cycle_state.stage = CycleStage.ANALYZE_PATTERNS
            self.logger.log_info("Step 3: Analyzing Patterns")
            
            # Intelligence analysis
            intelligence_result = await self._run_intelligence_analysis(cycle_state.metadata['market_data'])
            
            # Forecast and simulate scenarios
            forecasts = await self._generate_forecasts(intelligence_result)
            
            # Feed to market conditions approver
            approval_result = await self._get_market_approval(forecasts)
            
            cycle_state.metadata['intelligence_result'] = intelligence_result
            cycle_state.metadata['forecasts'] = forecasts
            cycle_state.metadata['approval_result'] = approval_result
            
            self.logger.log_info("Step 3: Pattern analysis completed")
            
        except Exception as e:
            self.logger.log_error("Step 3 failed", str(e), "TradingEngineCycle")
            raise
    
    async def _step_4_compose_strategy(self, cycle_state: CycleState):
        """Step 4: Compose Strategy"""
        try:
            cycle_state.stage = CycleStage.COMPOSE_STRATEGY
            self.logger.log_info("Step 4: Composing Strategy")
            
            # Strategy composition
            strategy = await self._compose_strategy(cycle_state.metadata)
            
            # Apply market conditions, account state, and risk limits
            applied_strategy = await self._apply_strategy_constraints(strategy)
            
            # Validate strategy
            validation_result = await self._validate_strategy(applied_strategy)
            
            cycle_state.metadata['strategy'] = strategy
            cycle_state.metadata['applied_strategy'] = applied_strategy
            cycle_state.metadata['strategy_validation'] = validation_result
            
            self.logger.log_info("Step 4: Strategy composition completed")
            
        except Exception as e:
            self.logger.log_error("Step 4 failed", str(e), "TradingEngineCycle")
            raise
    
    async def _step_5_evaluate_risks(self, cycle_state: CycleState):
        """Step 5: Evaluate Risks"""
        try:
            cycle_state.stage = CycleStage.EVALUATE_RISKS
            self.logger.log_info("Step 5: Evaluating Risks")
            
            # Risk evaluation
            risk_assessment = await self._evaluate_risks(cycle_state.metadata['applied_strategy'])
            
            # Risk validation
            risk_validation = await self._validate_risks(risk_assessment)
            
            cycle_state.metadata['risk_assessment'] = risk_assessment
            cycle_state.metadata['risk_validation'] = risk_validation
            
            self.logger.log_info("Step 5: Risk evaluation completed")
            
        except Exception as e:
            self.logger.log_error("Step 5 failed", str(e), "TradingEngineCycle")
            raise
    
    async def _step_6_execute_strategy(self, cycle_state: CycleState):
        """Step 6: Execute Strategy"""
        try:
            cycle_state.stage = CycleStage.EXECUTE_STRATEGY
            self.logger.log_info("Step 6: Executing Strategy")
            
            # Execute strategy
            execution_result = await self._execute_strategy(cycle_state.metadata['applied_strategy'])
            
            # Monitor execution
            execution_monitoring = await self._monitor_execution(execution_result)
            
            cycle_state.metadata['execution_result'] = execution_result
            cycle_state.metadata['execution_monitoring'] = execution_monitoring
            
            self.logger.log_info("Step 6: Strategy execution completed")
            
        except Exception as e:
            self.logger.log_error("Step 6 failed", str(e), "TradingEngineCycle")
            raise
    
    async def _step_7_monitor_health(self, cycle_state: CycleState):
        """Step 7: Monitor System Health"""
        try:
            cycle_state.stage = CycleStage.MONITOR_HEALTH
            self.logger.log_info("Step 7: Monitoring System Health")
            
            # System health monitoring
            health_status = await self._monitor_system_health()
            
            # Failure prevention
            failure_prevention = await self._run_failure_prevention()
            
            cycle_state.metadata['health_status'] = health_status
            cycle_state.metadata['failure_prevention'] = failure_prevention
            
            self.logger.log_info("Step 7: System health monitoring completed")
            
        except Exception as e:
            self.logger.log_error("Step 7 failed", str(e), "TradingEngineCycle")
            raise
    
    async def _step_8_learn_adapt(self, cycle_state: CycleState):
        """Step 8: Learn & Adapt"""
        try:
            cycle_state.stage = CycleStage.LEARN_ADAPT
            self.logger.log_info("Step 8: Learning & Adapting")
            
            # Online learning
            learning_result = await self._run_online_learning(cycle_state.metadata)
            
            # Strategy testing and improvement
            strategy_improvement = await self._improve_strategies(cycle_state.metadata)
            
            # System refinement
            system_refinement = await self._refine_system(cycle_state.metadata)
            
            cycle_state.metadata['learning_result'] = learning_result
            cycle_state.metadata['strategy_improvement'] = strategy_improvement
            cycle_state.metadata['system_refinement'] = system_refinement
            
            self.logger.log_info("Step 8: Learning & adaptation completed")
            
        except Exception as e:
            self.logger.log_error("Step 8 failed", str(e), "TradingEngineCycle")
            raise
    
    async def _step_9_log_reset(self, cycle_state: CycleState):
        """Step 9: Log, Report, & Reset"""
        try:
            cycle_state.stage = CycleStage.LOG_RESET
            self.logger.log_info("Step 9: Logging, Reporting & Resetting")
            
            # Write reports
            await self._write_reports(cycle_state.metadata)
            
            # Store state snapshots
            await self._store_state_snapshots(cycle_state)
            
            # Prepare for next cycle
            await self._prepare_next_cycle()
            
            self.logger.log_info("Step 9: Logging, reporting & reset completed")
            
        except Exception as e:
            self.logger.log_error("Step 9 failed", str(e), "TradingEngineCycle")
            raise
    
    # Implementation of individual step methods
    async def _load_configurations(self):
        """Load system configurations"""
        # Implementation for loading configurations
        pass
    
    async def _connect_adapters(self):
        """Connect to brokers and data sources"""
        # Implementation for connecting adapters
        pass
    
    async def _health_check(self):
        """Perform system health check"""
        # Implementation for health checking
        pass
    
    async def _collect_market_data(self):
        """Collect market data from data feeds"""
        # Implementation for collecting market data
        pass
    
    async def _analyze_market_conditions(self, market_data):
        """Analyze market conditions"""
        # Implementation for market conditions analysis
        pass
    
    async def _validate_market_conditions(self, market_conditions):
        """Validate market conditions"""
        # Implementation for market conditions validation
        pass
    
    async def _run_intelligence_analysis(self, market_data):
        """Run intelligence analysis"""
        # Implementation for intelligence analysis
        pass
    
    async def _generate_forecasts(self, intelligence_result):
        """Generate forecasts and scenarios"""
        # Implementation for forecasting
        pass
    
    async def _get_market_approval(self, forecasts):
        """Get market conditions approval"""
        # Implementation for market approval
        pass
    
    async def _compose_strategy(self, metadata):
        """Compose trading strategy"""
        # Implementation for strategy composition
        pass
    
    async def _apply_strategy_constraints(self, strategy):
        """Apply constraints to strategy"""
        # Implementation for applying constraints
        pass
    
    async def _validate_strategy(self, strategy):
        """Validate strategy"""
        # Implementation for strategy validation
        pass
    
    async def _evaluate_risks(self, strategy):
        """Evaluate risks"""
        # Implementation for risk evaluation
        pass
    
    async def _validate_risks(self, risk_assessment):
        """Validate risk assessment"""
        # Implementation for risk validation
        pass
    
    async def _execute_strategy(self, strategy):
        """Execute trading strategy"""
        # Implementation for strategy execution
        pass
    
    async def _monitor_execution(self, execution_result):
        """Monitor execution"""
        # Implementation for execution monitoring
        pass
    
    async def _monitor_system_health(self):
        """Monitor system health"""
        # Implementation for system health monitoring
        pass
    
    async def _run_failure_prevention(self):
        """Run failure prevention"""
        # Implementation for failure prevention
        pass
    
    async def _run_online_learning(self, metadata):
        """Run online learning"""
        # Implementation for online learning
        pass
    
    async def _improve_strategies(self, metadata):
        """Improve strategies"""
        # Implementation for strategy improvement
        pass
    
    async def _refine_system(self, metadata):
        """Refine system"""
        # Implementation for system refinement
        pass
    
    async def _write_reports(self, metadata):
        """Write reports"""
        # Implementation for report writing
        pass
    
    async def _store_state_snapshots(self, cycle_state):
        """Store state snapshots"""
        # Implementation for storing state snapshots
        pass
    
    async def _prepare_next_cycle(self):
        """Prepare for next cycle"""
        # Implementation for preparing next cycle
        pass
    
    # Monitoring and metrics methods
    async def _cycle_monitor(self):
        """Monitor cycle execution"""
        try:
            while self.is_running:
                # Monitor cycle performance
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
    
    async def _health_monitor(self):
        """Monitor system health"""
        try:
            while self.is_running:
                # Monitor system health
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            pass
    
    async def _metrics_reporter(self):
        """Report metrics"""
        try:
            while self.is_running:
                # Report metrics
                await asyncio.sleep(300)  # Every 5 minutes
        except asyncio.CancelledError:
            pass
    
    def _update_avg_duration(self, duration: float):
        """Update average cycle duration"""
        try:
            total_cycles = self.metrics['total_cycles']
            current_avg = self.metrics['avg_cycle_duration']
            
            if total_cycles > 0:
                new_avg = ((current_avg * (total_cycles - 1)) + duration) / total_cycles
                self.metrics['avg_cycle_duration'] = new_avg
            else:
                self.metrics['avg_cycle_duration'] = duration
                
        except Exception as e:
            self.logger.log_error("Failed to update average duration", str(e), "TradingEngineCycle")
    
    async def _report_final_metrics(self):
        """Report final metrics"""
        try:
            self.logger.log_info("=== FINAL TRADING ENGINE METRICS ===")
            self.logger.log_info(f"Total cycles: {self.metrics['total_cycles']}")
            self.logger.log_info(f"Successful cycles: {self.metrics['successful_cycles']}")
            self.logger.log_info(f"Failed cycles: {self.metrics['failed_cycles']}")
            self.logger.log_info(f"Average cycle duration: {self.metrics['avg_cycle_duration']:.2f}s")
            self.logger.log_info(f"Last cycle duration: {self.metrics['last_cycle_duration']:.2f}s")
            
        except Exception as e:
            self.logger.log_error("Failed to report final metrics", str(e), "TradingEngineCycle")
    
    def get_cycle_status(self) -> Dict[str, Any]:
        """Get current cycle status"""
        try:
            status = {
                'is_running': self.is_running,
                'current_cycle': self.current_cycle,
                'metrics': self.metrics,
                'cycle_history_count': len(self.cycle_history)
            }
            
            return status
            
        except Exception as e:
            self.logger.log_error("Failed to get cycle status", str(e), "TradingEngineCycle")
            return {'error': str(e)}
    
    def is_connected(self) -> bool:
        """Check if trading engine is connected"""
        try:
            return (self.redis_client is not None and 
                   self.core_agent.is_connected())
        except:
            return False

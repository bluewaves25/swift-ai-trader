API Documentation
Broker Fee Models

ModelLoader:
load_fee_models(): Loads fee models from JSON to Redis. Returns dict.
get_fee_model(broker): Retrieves fee model for a broker. Returns dict.
update_fee_model(broker, model): Updates fee model in Redis/memory.


FeeNormalizer:
normalize_fee_model(broker, fee_model): Standardizes fees to USD. Returns dict.



Slippage Tracker

SlippageDetector:
detect_slippage(trade): Compares expected/executed prices. Returns issue dict if slippage >0.1%.


ExecutionDelta:
analyze_execution(trade): Attributes slippage to causes (latency, depth). Returns dict.


VarianceAnalyzer:
analyze_slippage_variance(trades): Flags high variance (>0.2%). Returns issue dict.



Cost Optimizer

SmartSizer:
optimize_position_size(trade): Adjusts size to keep fees <1%. Returns float.


ExecutionRecommender:
recommend_execution(trade): Suggests limit/market order based on spread. Returns str.


FeeStrategyMap:
map_strategy_to_broker(strategy, trade): Maps strategy to low-fee broker. Returns str.



Profitability Audit

PnlAdjuster:
adjust_pnl(trade): Subtracts fees/slippage for true PnL. Returns dict.


HiddenFeeDetector:
detect_hidden_fees(trades): Flags fee discrepancies (>0.5%). Returns list of issues.


TrueProfitReporter:
generate_profit_report(trades): Generates weekly profit report. Returns dict.



Learning Layer

Internal/ResearchEngine:
analyze_cost_patterns(key_pattern): Analyzes trade logs for cost patterns. Returns dict.


Internal/TrainingModule:
prepare_dataset(key_pattern): Builds dataset from internal patterns. Returns list.
train_model(dataset): Trains model on internal data. Returns metrics dict.


Internal/RetrainingLoop:
run_retraining(): Updates models daily.


External/WebIntelligence/BrokerScraper:
scrape_broker_fees(): Scrapes fee schedules from websites. Returns list.


External/WebIntelligence/ForumChecker:
check_forum_complaints(): Collects fee complaints from forums. Returns list.


External/WebIntelligence/RegulationMonitor:
monitor_regulatory_changes(): Tracks regulatory fee changes. Returns list.


External/SocialAnalyzer/FeeSentimentProcessor:
process_sentiment(complaints): Analyzes sentiment of complaints. Returns list.


External/SocialAnalyzer/TrendCorrelator:
correlate_trends(complaints): Detects complaint spikes (>5). Returns dict.


External/IntelligenceFusion/CostPatternSynthesizer:
synthesize_patterns(internal_patterns, external_data): Merges patterns. Returns list.


External/IntelligenceFusion/AnomalyPredictor:
predict_anomalies(patterns): Flags fee anomalies (>1.5%). Returns list.


HybridTraining/FeeTrainer:
prepare_combined_dataset(internal_pattern, external_data): Merges datasets. Returns list.
train_model(dataset): Trains hybrid model. Returns metrics dict.


HybridTraining/ExternalFeeValidator:
validate_patterns(internal_patterns, external_data): Validates patterns. Returns list.



Integration

Redis Channels: Publish issues to "fee_incident" for Core Agent.
Dependencies: IncidentCache.store_incident(), FailureAgentLogger.log_issue().

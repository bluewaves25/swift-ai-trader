Training Documentation
Overview
The Fees Monitor Agent's learning layer trains models to predict high-cost brokers and symbols, using internal trade data and external sources (web, social media).
Components

ResearchEngine: Analyzes trade logs for cost patterns (e.g., high fees by broker/symbol).
TrainingModule: Prepares datasets and trains models to identify high-cost entities.
RetrainingLoop: Updates models daily to adapt to changing patterns.
FeeTrainer: Combines internal/external data for hybrid training.
ExternalFeeValidator: Validates internal patterns against scraped fees and sentiments.

Training Process

Data Collection:
Internal: ResearchEngine extracts fee impacts from IncidentCache (Redis).
External: BrokerScraper, ForumChecker, RegulationMonitor gather fee data and complaints.


Dataset Preparation:
TrainingModule.prepare_dataset() builds internal dataset from cost patterns.
FeeTrainer.prepare_combined_dataset() merges with external data (e.g., sentiment, regulatory changes).


Model Training:
TrainingModule.train_model() trains on internal data (threshold-based, placeholder for ML).
FeeTrainer.train_model() trains on combined data, storing models in Redis.


Validation:
ExternalFeeValidator.validate_patterns() checks internal patterns against external data, flagging discrepancies (>1%).


Retraining:
RetrainingLoop.run_retraining() updates models daily (configurable interval).



Model Output

Stored in Redis (fees_monitor:cost_model, fees_monitor:hybrid_cost_model).
Format: {"high_cost_brokers": [str], "high_cost_symbols": [str], "training_timestamp": int}.
Used by SmartSizer, ExecutionRecommender, and FeeStrategyMap for optimization.

Scalability

Supports new data sources via config (e.g., forum_urls, regulatory_urls).
Redis caching ensures efficient dataset access.
Placeholder ML logic (e.g., scikit-learn) allows advanced model integration.

Dependencies

Libraries: vaderSentiment (sentiment), requests, BeautifulSoup (scraping).
Internal: IncidentCache, FailureAgentLogger for data storage and logging.

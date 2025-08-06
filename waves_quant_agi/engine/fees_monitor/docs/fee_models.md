Fee Models Documentation
Overview
Fee models define broker-specific cost structures (e.g., commissions, swaps) used by the Fees Monitor Agent to track and optimize trading costs.
Fee Model Structure
Stored in broker_fee_db.json, fee models follow this schema:
{
  "broker_name": {
    "commission": float,  // Percentage (e.g., 0.001 for 0.1%)
    "swap": float,       // Overnight fee percentage
    "inactivity_fee": float, // Flat fee in USD
    "spread": float,     // Percentage of trade value
    "currency": str      // Fee currency (e.g., "USD")
  }
}

Example
{
  "binance": {
    "commission": 0.001,
    "swap": 0.0005,
    "inactivity_fee": 0.0,
    "spread": 0.0001,
    "currency": "USD"
  }
}

Components

ModelLoader: Loads fee models from broker_fee_db.json into Redis.
FeeNormalizer: Standardizes fees to USD, ensuring consistency across brokers.
BrokerScraper: Updates models with scraped data from broker websites.
RegulationMonitor: Adjusts models for regulatory changes.

Usage

Loading: ModelLoader.load_fee_models() populates Redis cache.
Normalization: FeeNormalizer.normalize_fee_model(broker, model) converts fees to standard format.
Updates: External data from BrokerScraper and RegulationMonitor refreshes models.
Access: ModelLoader.get_fee_model(broker) retrieves models for cost calculations.

Scalability

Supports new brokers via JSON updates.
Redis caching ensures low-latency access.
Configurable fields allow additional fee types (e.g., withdrawal fees).

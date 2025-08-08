from typing import Dict, Any, List
import time
from fees_monitor.logs.failure_agent_logger import FailureAgentLogger
from fees_monitor.memory.incident_cache import IncidentCache
from ..external.web_intelligence.broker_scraper import BrokerScraper
from ..external.social_analyzer.fee_sentiment_processor import FeeSentimentProcessor

class ExternalFeeValidator:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, broker_scraper: BrokerScraper, sentiment_processor: FeeSentimentProcessor):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.broker_scraper = broker_scraper
        self.sentiment_processor = sentiment_processor
        self.validation_threshold = config.get("validation_threshold", 0.01)  # 1% discrepancy

    async def validate_patterns(self, internal_patterns: Dict[str, Any], external_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate internal cost patterns against external data."""
        try:
            validated = []
            scraped_fees = await self.broker_scraper.scrape_broker_fees()
            sentiments = await self.sentiment_processor.process_sentiment(external_data)

            for pattern in internal_patterns.get("high_fee_patterns", []):
                broker = pattern["broker"]
                internal_fee_impact = pattern["fee_impact"]

                # Check against scraped fees
                scraped_fee = next((f["fees"] for f in scraped_fees if f["broker"] == broker), {})
                commission = float(scraped_fee.get("commission", 0.0))
                discrepancy = abs(internal_fee_impact - commission) / max(internal_fee_impact, commission) if max(internal_fee_impact, commission) > 0 else 0

                if discrepancy > self.validation_threshold:
                    issue = {
                        "type": "fee_validation_discrepancy",
                        "broker": broker,
                        "internal_fee_impact": internal_fee_impact,
                        "scraped_commission": commission,
                        "discrepancy": discrepancy,
                        "timestamp": int(time.time()),
                        "description": f"Fee validation discrepancy for {broker}: internal {internal_fee_impact:.4f}, scraped {commission:.4f}"
                    }
                    validated.append(issue)
                    self.logger.log_issue(issue)
                    self.cache.store_incident(issue)
                    await self.notify_core(issue)

            return validated
        except Exception as e:
            self.logger.log(f"Error validating fee patterns: {e}")
            self.cache.store_incident({
                "type": "fee_validation_error",
                "timestamp": int(time.time()),
                "description": f"Error validating fee patterns: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of validation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent
from typing import Dict, Any, List
import pandas as pd
import redis
import json
import numpy as np

class ResearchEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.pattern_threshold = config.get("pattern_threshold", 0.7)  # 70% confidence for patterns

    async def detect_patterns(self, execution_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect execution-specific patterns (e.g., slippage vs time of day)."""
        try:
            patterns = []
            for symbol in execution_data["symbol"].unique():
                symbol_data = execution_data[execution_data["symbol"] == symbol]
                slippage = symbol_data["slippage_bps"].values
                times = pd.to_datetime(symbol_data["timestamp"]).dt.hour
                correlation = np.corrcoef(slippage, times)[0, 1] if len(slippage) > 1 else 0.0

                if abs(correlation) >= self.pattern_threshold:
                    pattern = {
                        "type": "execution_pattern",
                        "symbol": symbol,
                        "correlation": correlation,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Slippage-time correlation for {symbol}: {correlation:.2f}"
                    }
                    patterns.append(pattern)
                    self.redis_client.set(f"execution:pattern:{symbol}", json.dumps(pattern), ex=604800)
                    await self.notify_training(pattern)

            summary = {
                "type": "pattern_summary",
                "pattern_count": len(patterns),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Detected {len(patterns)} execution patterns"
            }
            self.redis_client.set("execution:pattern_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return patterns
        except Exception as e:
            self.redis_client.lpush("execution:errors", json.dumps({
                "type": "research_engine_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error detecting patterns: {str(e)}"
            }))
            return []

    async def notify_training(self, pattern: Dict[str, Any]):
        """Notify Training Module of detected patterns."""
        self.redis_client.publish("training_module", json.dumps(pattern))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of pattern detection results."""
        self.redis_client.publish("execution_output", json.dumps(issue))
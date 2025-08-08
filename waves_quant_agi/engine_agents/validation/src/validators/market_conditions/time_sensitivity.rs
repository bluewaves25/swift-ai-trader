use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct TimeSensitivity {
    config: HashMap<String, Value>,
    redis_client: redis::Client,
    max_time_drift: i64,
}

impl TimeSensitivity {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        let max_time_drift = config.get("max_time_drift").and_then(|v| v.as_i64()).unwrap_or(30);
        TimeSensitivity {
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            max_time_drift,
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>> {
        let timestamp = input.get("timestamp").and_then(|v| v.as_i64()).ok_or("Missing timestamp")?;
        let symbol = input.get("symbol").and_then(|v| v.as_str()).ok_or("Missing symbol")?;

        let mut conn = self.redis_client.get_async_connection().await?;
        let market_timestamp: i64 = conn.get(format!("market:timestamp:{}", symbol)).await.unwrap_or(0);
        let time_drift = (timestamp - market_timestamp).abs();

        if market_timestamp == 0 || time_drift > self.max_time_drift {
            return Err(format!("Time drift {} seconds exceeds limit {} for {}", time_drift, self.max_time_drift, symbol).into());
        }

        Ok(())
    }
}
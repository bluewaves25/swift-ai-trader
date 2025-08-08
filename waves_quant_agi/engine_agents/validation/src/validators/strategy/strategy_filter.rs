use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct StrategyFilter {
    config: HashMap<String, Value>,
    redis_client: redis::Client,
    max_time_window: i64,
}

impl StrategyFilter {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        let max_time_window = config.get("max_time_window").and_then(|v| v.as_i64()).unwrap_or(300);
        StrategyFilter {
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            max_time_window,
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>> {
        let timestamp = input.get("timestamp").and_then(|v| v.as_i64()).ok_or("Missing timestamp")?;
        let entry_price = input.get("entry_price").and_then(|v| v.as_f64()).ok_or("Missing entry price")?;
        let exit_price = input.get("exit_price").and_then(|v| v.as_f64()).ok_or("Missing exit price")?;
        let symbol = input.get("symbol").and_then(|v| v.as_str()).ok_or("Missing symbol")?;

        let now = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH)?.as_secs() as i64;
        if (now - timestamp) > self.max_time_window {
            return Err(format!("Strategy timestamp exceeds {} seconds", self.max_time_window).into());
        }

        if entry_price <= 0.0 || exit_price <= 0.0 {
            return Err("Invalid entry or exit price".into());
        }

        let mut conn = self.redis_client.get_async_connection().await?;
        let historical_signals: Vec<String> = conn.lrange(format!("strategy:signals:{}", symbol), 0, -1).await?;
        if historical_signals.contains(&serde_json::to_string(input)?) {
            return Err("Duplicate strategy signal detected".into());
        }

        Ok(())
    }
}
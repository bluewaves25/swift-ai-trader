use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct Consistency {
    config: HashMap<String, Value>,
    redis_client: redis::Client,
}

impl Consistency {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        Consistency {
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>> {
        let symbol = input.get("symbol").and_then(|v| v.as_str()).ok_or("Missing symbol")?;
        let signal = input.get("signal").and_then(|v| v.as_str()).ok_or("Missing signal")?;
        let size = input.get("size").and_then(|v| v.as_f64()).ok_or("Missing size")?;

        let mut conn = self.redis_client.get_async_connection().await?;
        let open_positions: Vec<String> = conn.lrange(format!("positions:open:{}", symbol), 0, -1).await.unwrap_or(vec![]);
        
        for pos in open_positions {
            let pos_data: HashMap<String, Value> = serde_json::from_str(&pos)?;
            let pos_signal = pos_data.get("signal").and_then(|v| v.as_str()).ok_or("Invalid position data")?;
            if (signal == "BUY" && pos_signal == "SELL") || (signal == "SELL" && pos_signal == "BUY") {
                return Err(format!("Conflicting position detected for {}", symbol).into());
            }
        }

        let prev_signals: Vec<String> = conn.lrange(format!("signals:recent:{}", symbol), 0, 9).await.unwrap_or(vec![]);
        if prev_signals.len() >= 10 {
            return Err(format!("Too many recent signals for {}", symbol).into());
        }

        Ok(())
    }
}
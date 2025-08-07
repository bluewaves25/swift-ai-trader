use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct RiskFilters {
    config: HashMap<String, Value>,
    redis_client: redis::Client,
    max_daily_loss: f64,
    max_order_size: f64,
}

impl RiskFilters {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        let max_daily_loss = config.get("max_daily_loss").and_then(|v| v.as_f64()).unwrap_or(0.05);
        let max_order_size = config.get("max_order_size").and_then(|v| v.as_f64()).unwrap_or(100000.0);
        RiskFilters {
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            max_daily_loss,
            max_order_size,
        }
    }

    pub async fn apply_filters(&self, symbol: &str, size: f64) -> Result<(), Box<dyn Error>> {
        if size > self.max_order_size {
            return Err(format!("Order size {} exceeds limit {}", size, self.max_order_size).into());
        }

        let mut conn = self.redis_client.get_async_connection().await?;
        let daily_loss: f64 = conn.get(format!("risk:daily_loss:{}", symbol)).await.unwrap_or(0.0);
        if daily_loss >= self.max_daily_loss {
            return Err(format!("Daily loss {} exceeds limit {}", daily_loss, self.max_daily_loss).into());
        }

        Ok(())
    }

    pub async fn update_risk_limits(&mut self, max_daily_loss: f64, max_order_size: f64) -> Result<(), Box<dyn Error>> {
        if max_daily_loss <= 0.0 || max_order_size <= 0.0 {
            return Err("Invalid risk limits".into());
        }
        self.max_daily_loss = max_daily_loss;
        self.max_order_size = max_order_size;
        Ok(())
    }
}
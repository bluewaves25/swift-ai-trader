use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct RiskAssessor {
    config: HashMap<String, Value>,
    redis_client: redis::Client,
    max_leverage: f64,
    max_exposure: f64,
}

impl RiskAssessor {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        let max_leverage = config.get("max_leverage").and_then(|v| v.as_f64()).unwrap_or(10.0);
        let max_exposure = config.get("max_exposure").and_then(|v| v.as_f64()).unwrap_or(0.1);
        RiskAssessor {
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            max_leverage,
            max_exposure,
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>> {
        let symbol = input.get("symbol").and_then(|v| v.as_str()).ok_or("Missing symbol")?;
        let size = input.get("size").and_then(|v| v.as_f64()).ok_or("Missing size")?;
        let leverage = input.get("leverage").and_then(|v| v.as_f64()).unwrap_or(1.0);

        if leverage > self.max_leverage {
            return Err(format!("Leverage {} exceeds limit {}", leverage, self.max_leverage).into());
        }

        let mut conn = self.redis_client.get_async_connection().await?;
        let portfolio_exposure: f64 = conn.get(format!("portfolio:exposure:{}", symbol)).await.unwrap_or(0.0);
        let total_exposure = portfolio_exposure + (size * leverage);
        if total_exposure > self.max_exposure {
            return Err(format!("Total exposure {} exceeds limit {}", total_exposure, self.max_exposure).into());
        }

        Ok(())
    }
}
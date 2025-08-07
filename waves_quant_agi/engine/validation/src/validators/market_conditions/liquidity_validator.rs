use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct LiquidityValidator {
    config: HashMap<String, Value>,
    redis_client: redis::Client,
    min_liquidity_ratio: f64,
}

impl LiquidityValidator {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        let min_liquidity_ratio = config.get("min_liquidity_ratio").and_then(|v| v.as_f64()).unwrap_or(0.05);
        LiquidityValidator {
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            min_liquidity_ratio,
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>> {
        let symbol = input.get("symbol").and_then(|v| v.as_str()).ok_or("Missing symbol")?;
        let size = input.get("size").and_then(|v| v.as_f64()).ok_or("Missing size")?;

        let mut conn = self.redis_client.get_async_connection().await?;
        let market_depth: f64 = conn.get(format!("market:depth:{}", symbol)).await.unwrap_or(0.0);
        let liquidity_ratio = size / market_depth;

        if market_depth == 0.0 || liquidity_ratio > self.min_liquidity_ratio {
            return Err(format!("Liquidity ratio {} exceeds limit {} for {}", liquidity_ratio, self.min_liquidity_ratio, symbol).into());
        }

        Ok(())
    }
}
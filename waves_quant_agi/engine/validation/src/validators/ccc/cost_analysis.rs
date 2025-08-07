use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct CostAnalysis {
    config: HashMap<String, Value>,
    redis_client: redis::Client,
    max_slippage_bps: f64,
    max_commission_pct: f64,
}

impl CostAnalysis {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        let max_slippage_bps = config.get("max_slippage_bps").and_then(|v| v.as_f64()).unwrap_or(50.0);
        let max_commission_pct = config.get("max_commission_pct").and_then(|v| v.as_f64()).unwrap_or(0.1);
        CostAnalysis {
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            max_slippage_bps,
            max_commission_pct,
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>> {
        let symbol = input.get("symbol").and_then(|v| v.as_str()).ok_or("Missing symbol")?;
        let size = input.get("size").and_then(|v| v.as_f64()).ok_or("Missing size")?;
        let entry_price = input.get("entry_price").and_then(|v| v.as_f64()).ok_or("Missing entry price")?;

        let mut conn = self.redis_client.get_async_connection().await?;
        let commission_pct: f64 = conn.get(format!("broker:commission:{}", symbol)).await.unwrap_or(0.0);
        let slippage_bps: f64 = conn.get(format!("market:slippage:{}", symbol)).await.unwrap_or(0.0);

        if commission_pct > self.max_commission_pct {
            return Err(format!("Commission {}% exceeds limit {}% for {}", commission_pct, self.max_commission_pct, symbol).into());
        }

        let slippage_cost = (slippage_bps / 10000.0) * entry_price * size;
        let max_slippage_cost = (self.max_slippage_bps / 10000.0) * entry_price * size;
        if slippage_cost > max_slippage_cost {
            return Err(format!("Slippage cost {} exceeds limit {} for {}", slippage_cost, max_slippage_cost, symbol).into());
        }

        Ok(())
    }
}
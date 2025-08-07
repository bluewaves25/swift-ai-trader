use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct Metrics {
    redis_client: redis::Client,
    config: HashMap<String, Value>,
}

impl Metrics {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        Metrics {
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            config: config.clone(),
        }
    }

    pub async fn log_execution(&self, symbol: &str, signal: &str, size: f64, latency: u128) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        let key = format!("metrics:execution:{}", symbol);
        let value = serde_json::json!({
            "signal": signal,
            "size": size,
            "latency": latency,
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        });
        conn.set_ex(key, value.to_string(), 604800).await?;
        Ok(())
    }

    pub async fn log_error(&self, error: &str) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        let key = "metrics:errors";
        let value = serde_json::json!({
            "error": error,
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        });
        conn.lpush(key, value.to_string()).await?;
        Ok(())
    }

    pub async fn log_slippage(&self, symbol: &str, slippage_bps: f64) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        let key = format!("metrics:slippage:{}", symbol);
        let value = serde_json::json!({
            "slippage_bps": slippage_bps,
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        });
        conn.set_ex(key, value.to_string(), 604800).await?;
        Ok(())
    }

    pub async fn log_config_update(&self, param: &str, value: f64) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        let key = "metrics:config_updates";
        let value = serde_json::json!({
            "parameter": param,
            "value": value,
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        });
        conn.lpush(key, value.to_string()).await?;
        Ok(())
    }
}
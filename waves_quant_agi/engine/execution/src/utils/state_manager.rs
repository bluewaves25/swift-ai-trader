use serde_json::{Value, json};
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct StateManager {
    redis_client: redis::Client,
    config: HashMap<String, Value>,
}

impl StateManager {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        StateManager {
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            config: config.clone(),
        }
    }

    pub async fn save_trade_state(&self, symbol: &str, trade_id: &str, state: &str) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        let key = format!("state:trade:{}", trade_id);
        let value = json!({
            "symbol": symbol,
            "state": state,
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        });
        conn.set_ex(key, value.to_string(), 604800).await?;
        Ok(())
    }

    pub async fn save_session_state(&self, session_id: &str, status: &str) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        let key = format!("state:session:{}", session_id);
        let value = json!({
            "status": status,
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        });
        conn.set_ex(key, value.to_string(), 604800).await?;
        Ok(())
    }

    pub async fn get_trade_state(&self, trade_id: &str) -> Result<Option<String>, Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        let key = format!("state:trade:{}", trade_id);
        let state: Option<String> = conn.get(key).await?;
        Ok(state)
    }
}
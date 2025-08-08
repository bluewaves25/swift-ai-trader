use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use redis::AsyncCommands;

pub struct Compliance {
    config: HashMap<String, Value>,
    redis_client: redis::Client,
    allowed_regions: Vec<String>,
}

impl Compliance {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        let allowed_regions = config.get("allowed_regions")
            .and_then(|v| v.as_array())
            .map(|arr| arr.iter().filter_map(|v| v.as_str().map(String::from)).collect())
            .unwrap_or(vec!["US".to_string(), "EU".to_string()]);
        Compliance {
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            allowed_regions,
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>> {
        let symbol = input.get("symbol").and_then(|v| v.as_str()).ok_or("Missing symbol")?;
        let region = input.get("region").and_then(|v| v.as_str()).ok_or("Missing region")?;

        if !self.allowed_regions.contains(&region.to_string()) {
            return Err(format!("Region {} not allowed for {}", region, symbol).into());
        }

        let mut conn = self.redis_client.get_async_connection().await?;
        let restricted_symbols: Vec<String> = conn.get(format!("compliance:restricted:{}", region)).await.unwrap_or(vec![]);
        if restricted_symbols.contains(&symbol.to_string()) {
            return Err(format!("Symbol {} restricted in {}", symbol, region).into());
        }

        Ok(())
    }
}
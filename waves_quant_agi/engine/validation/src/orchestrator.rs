use crate::router::Router;
use crate::utils::config_loader::ConfigLoader;
use serde_json::{Value, json};
use std::collections::HashMap;
use std::error::Error;
use tokio::sync::mpsc;
use redis::AsyncCommands;

pub struct Orchestrator {
    router: Router,
    redis_client: redis::Client,
    config: HashMap<String, Value>,
    tx: mpsc::Sender<HashMap<String, Value>>,
}

impl Orchestrator {
    pub fn new(config: &HashMap<String, Value>, tx: mpsc::Sender<HashMap<String, Value>>) -> Self {
        let router = Router::new(config);
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        Orchestrator {
            router,
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            config: config.clone(),
            tx,
        }
    }

    pub async fn start(&mut self, mut rx: mpsc::Receiver<HashMap<String, Value>>) -> Result<(), Box<dyn Error>> {
        while let Some(input) = rx.recv().await {
            let result = self.router.validate(&input).await;
            let result_json = result.to_json();
            let mut conn = self.redis_client.get_async_connection().await?;
            conn.publish("validation_output", serde_json::to_string(&result_json)?).await?;
            if result.status == "valid" {
                self.tx.send(input).await?;
            } else {
                conn.lpush("validation:errors", serde_json::to_string(&result_json)?).await?;
            }
        }
        Ok(())
    }
}
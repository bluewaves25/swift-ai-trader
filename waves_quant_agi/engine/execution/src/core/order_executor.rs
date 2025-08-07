use crate::adapter::broker_interface::BrokerInterface;
use crate::utils::metrics::Metrics;
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use tokio::sync::mpsc;

pub struct OrderExecutor {
    brokers: Vec<BrokerInterface>,
    metrics: Metrics,
    config: HashMap<String, Value>,
}

impl OrderExecutor {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let brokers = BrokerInterface::from_config(config);
        let metrics = Metrics::new(config);
        OrderExecutor {
            brokers,
            metrics,
            config: config.clone(),
        }
    }

    pub async fn execute_order(&mut self, signal: &str, size: f64, symbol: &str) -> Result<(), Box<dyn Error>> {
        if !self.validate_order(signal, size, symbol) {
            self.metrics.log_error("Invalid order parameters");
            return Err("Invalid order parameters".into());
        }

        let broker = self.select_broker(symbol)?;
        let start_time = std::time::Instant::now();
        let result = broker.place_order(signal, size, symbol).await;
        let latency = start_time.elapsed().as_micros();

        self.metrics.log_execution(symbol, signal, size, latency);
        match result {
            Ok(_) => Ok(()),
            Err(e) => {
                self.metrics.log_error(&format!("Order execution failed: {}", e));
                Err(e)
            }
        }
    }

    fn validate_order(&self, signal: &str, size: f64, symbol: &str) -> bool {
        signal == "BUY" || signal == "SELL" && size > 0.0 && !symbol.is_empty()
    }

    fn select_broker(&self, symbol: &str) -> Result<&BrokerInterface, Box<dyn Error>> {
        self.brokers.iter().find(|b| b.supports_symbol(symbol)).ok_or("No suitable broker found".into())
    }
}
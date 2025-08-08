use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use async_trait::async_trait;

#[async_trait]
pub trait Broker {
    async fn place_order(&self, signal: &str, size: f64, symbol: &str) -> Result<(), Box<dyn Error>>;
    fn supports_symbol(&self, symbol: &str) -> bool;
}

pub struct BrokerInterface {
    config: HashMap<String, Value>,
    supported_symbols: Vec<String>,
}

impl BrokerInterface {
    pub fn from_config(config: &HashMap<String, Value>) -> Vec<Self> {
        let brokers = config.get("brokers").and_then(|v| v.as_array()).unwrap_or(&vec![]);
        brokers.iter().map(|b| {
            let symbols = b.get("supported_symbols")
                .and_then(|v| v.as_array())
                .unwrap_or(&vec![])
                .iter()
                .filter_map(|s| s.as_str().map(String::from))
                .collect();
            BrokerInterface {
                config: b.as_object().unwrap_or(&HashMap::new()).clone(),
                supported_symbols: symbols,
            }
        }).collect()
    }
}

#[async_trait]
impl Broker for BrokerInterface {
    async fn place_order(&self, signal: &str, size: f64, symbol: &str) -> Result<(), Box<dyn Error>> {
        // Placeholder: Simulate broker API call
        if self.supports_symbol(symbol) {
            Ok(())
        } else {
            Err(format!("Symbol {} not supported", symbol).into())
        }
    }

    fn supports_symbol(&self, symbol: &str) -> bool {
        self.supported_symbols.contains(&symbol.to_string())
    }
}
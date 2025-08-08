use crate::utils::metrics::Metrics;
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;

pub struct SlippageController {
    metrics: Metrics,
    config: HashMap<String, Value>,
    max_slippage_bps: f64,
}

impl SlippageController {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let max_slippage_bps = config.get("max_slippage_bps").and_then(|v| v.as_f64()).unwrap_or(50.0);
        SlippageController {
            metrics: Metrics::new(config),
            config: config.clone(),
            max_slippage_bps,
        }
    }

    pub async fn check_slippage(&self, symbol: &str, expected_price: f64, actual_price: f64) -> Result<(), Box<dyn Error>> {
        let slippage_bps = ((actual_price - expected_price).abs() / expected_price) * 10000.0;
        if slippage_bps > self.max_slippage_bps {
            self.metrics.log_error(&format!("Slippage exceeded for {}: {} bps", symbol, slippage_bps));
            return Err(format!("Slippage {} bps exceeds limit {} bps", slippage_bps, self.max_slippage_bps).into());
        }
        self.metrics.log_slippage(symbol, slippage_bps);
        Ok(())
    }

    pub fn update_slippage_limit(&mut self, new_limit_bps: f64) -> Result<(), Box<dyn Error>> {
        if new_limit_bps <= 0.0 {
            return Err("Invalid slippage limit".into());
        }
        self.max_slippage_bps = new_limit_bps;
        self.metrics.log_config_update("slippage_limit", new_limit_bps);
        Ok(())
    }
}
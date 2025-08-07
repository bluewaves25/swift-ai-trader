use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;

pub struct StopLossChecker {
    config: HashMap<String, Value>,
    min_sl_ratio: f64,
}

impl StopLossChecker {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let min_sl_ratio = config.get("min_sl_ratio").and_then(|v| v.as_f64()).unwrap_or(0.01);
        StopLossChecker {
            config: config.clone(),
            min_sl_ratio,
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>> {
        let stop_loss = input.get("stop_loss").and_then(|v| v.as_f64()).ok_or("Missing stop-loss")?;
        let entry_price = input.get("entry_price").and_then(|v| v.as_f64()).ok_or("Missing entry price")?;
        let signal = input.get("signal").and_then(|v| v.as_str()).ok_or("Missing signal")?;

        let sl_ratio = if signal == "BUY" {
            (entry_price - stop_loss) / entry_price
        } else {
            (stop_loss - entry_price) / entry_price
        };

        if sl_ratio.abs() < self.min_sl_ratio {
            return Err(format!("Stop-loss ratio {} below minimum {}", sl_ratio, self.min_sl_ratio).into());
        }

        Ok(())
    }
}
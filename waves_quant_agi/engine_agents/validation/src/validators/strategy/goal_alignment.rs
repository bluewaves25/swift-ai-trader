use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;

pub struct GoalAlignment {
    config: HashMap<String, Value>,
    max_risk_reward_ratio: f64,
}

impl GoalAlignment {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let max_risk_reward_ratio = config.get("max_risk_reward_ratio").and_then(|v| v.as_f64()).unwrap_or(2.0);
        GoalAlignment {
            config: config.clone(),
            max_risk_reward_ratio,
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>> {
        let stop_loss = input.get("stop_loss").and_then(|v| v.as_f64()).ok_or("Missing stop-loss")?;
        let take_profit = input.get("take_profit").and_then(|v| v.as_f64()).ok_or("Missing take-profit")?;
        let entry_price = input.get("entry_price").and_then(|v| v.as_f64()).ok_or("Missing entry price")?;
        let signal = input.get("signal").and_then(|v| v.as_str()).ok_or("Missing signal")?;

        let risk = if signal == "BUY" {
            entry_price - stop_loss
        } else {
            stop_loss - entry_price
        }.abs();

        let reward = if signal == "BUY" {
            take_profit - entry_price
        } else {
            entry_price - take_profit
        }.abs();

        if risk == 0.0 {
            return Err("Invalid risk: stop-loss equals entry price".into());
        }

        let risk_reward_ratio = reward / risk;
        if risk_reward_ratio > self.max_risk_reward_ratio {
            return Err(format!("Risk-reward ratio {} exceeds limit {}", risk_reward_ratio, self.max_risk_reward_ratio).into());
        }

        Ok(())
    }
}
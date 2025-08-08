use crate::validators::risk::risk_assessor::RiskAssessor;
use crate::validators::risk::stop_loss_checker::StopLossChecker;
use crate::validators::strategy::strategy_filter::StrategyFilter;
use crate::validators::strategy::goal_alignment::GoalAlignment;
use crate::validators::market_conditions::liquidity_validator::LiquidityValidator;
use crate::ValidationResult;
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use async_trait::async_trait;

pub struct Router {
    risk_assessor: RiskAssessor,
    stop_loss_checker: StopLossChecker,
    strategy_filter: StrategyFilter,
    goal_alignment: GoalAlignment,
    liquidity_validator: LiquidityValidator,
}

impl Router {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        Router {
            risk_assessor: RiskAssessor::new(config),
            stop_loss_checker: StopLossChecker::new(config),
            strategy_filter: StrategyFilter::new(config),
            goal_alignment: GoalAlignment::new(config),
            liquidity_validator: LiquidityValidator::new(config),
        }
    }

    pub async fn validate(&self, input: &HashMap<String, Value>) -> ValidationResult {
        let mut details = HashMap::new();
        let mut status = "valid";
        let mut reason = "All checks passed".to_string();

        if let Err(e) = self.validate_data(input, &mut details).await {
            status = "reject";
            reason = e.to_string();
        } else if let Err(e) = self.risk_assessor.validate(input).await {
            status = "reject";
            reason = format!("Risk validation failed: {}", e);
            details.insert("risk_check".to_string(), false);
        } else if let Err(e) = self.stop_loss_checker.validate(input).await {
            status = "reject";
            reason = format!("Stop-loss validation failed: {}", e);
            details.insert("stop_loss_check".to_string(), false);
        } else if let Err(e) = self.strategy_filter.validate(input).await {
            status = "reject";
            reason = format!("Strategy validation failed: {}", e);
            details.insert("strategy_check".to_string(), false);
        } else if let Err(e) = self.goal_alignment.validate(input).await {
            status = "reject";
            reason = format!("Goal alignment failed: {}", e);
            details.insert("goal_check".to_string(), false);
        } else if let Err(e) = self.liquidity_validator.validate(input).await {
            status = "reject";
            reason = format!("Liquidity validation failed: {}", e);
            details.insert("liquidity_check".to_string(), false);
        }

        details.insert("data_check".to_string(), status == "valid");
        ValidationResult::new(&status, &reason, details)
    }

    async fn validate_data(&self, input: &HashMap<String, Value>, details: &mut HashMap<String, bool>) -> Result<(), Box<dyn Error>> {
        let timestamp = input.get("timestamp").and_then(|v| v.as_i64()).ok_or("Missing timestamp")?;
        let symbol = input.get("symbol").and_then(|v| v.as_str()).ok_or("Missing symbol")?;
        let size = input.get("size").and_then(|v| v.as_f64()).ok_or("Missing size")?;
        let now = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH)?.as_secs() as i64;
        if (now - timestamp).abs() > 60 {
            details.insert("timestamp_freshness".to_string(), false);
            return Err("Timestamp not fresh".into());
        }
        if symbol.is_empty() {
            details.insert("symbol_valid".to_string(), false);
            return Err("Invalid symbol".into());
        }
        if size <= 0.0 {
            details.insert("size_valid".to_string(), false);
            return Err("Invalid size".into());
        }
        Ok(())
    }
}
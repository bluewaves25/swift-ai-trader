pub mod orchestrator;
pub mod router;
pub mod validators;
pub mod utils;

use serde_json::{Value, json};
use std::collections::HashMap;

pub struct ValidationResult {
    pub status: String,
    pub reason: String,
    pub details: HashMap<String, bool>,
}

impl ValidationResult {
    pub fn new(status: &str, reason: &str, details: HashMap<String, bool>) -> Self {
        ValidationResult {
            status: status.to_string(),
            reason: reason.to_string(),
            details,
        }
    }

    pub fn to_json(&self) -> Value {
        json!({
            "status": self.status,
            "reason": self.reason,
            "details": self.details,
        })
    }
}
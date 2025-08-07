use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use async_trait::async_trait;

#[async_trait]
pub trait Validator {
    async fn validate(&self, input: &HashMap<String, Value>) -> Result<(), Box<dyn Error>>;
}
use serde_yaml;
use std::collections::HashMap;
use std::error::Error;
use std::fs::File;
use serde_json::Value;

pub struct ConfigLoader;

impl ConfigLoader {
    pub fn load(path: &str) -> Result<HashMap<String, Value>, Box<dyn Error>> {
        let file = File::open(path)?;
        let config: HashMap<String, Value> = serde_yaml::from_reader(file)?;
        Ok(config)
    }
}
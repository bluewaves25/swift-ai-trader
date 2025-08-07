use serde_yaml;
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use std::fs::File;
use std::io::Read;

pub struct ConfigLoader;

impl ConfigLoader {
    pub fn load(file_path: &str) -> Result<HashMap<String, Value>, Box<dyn Error>> {
        let mut file = File::open(file_path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        let config: HashMap<String, Value> = serde_yaml::from_str(&contents)?;
        Ok(config)
    }
}
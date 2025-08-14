// use crate::adapters::broker_interface::BrokerInterface;
use crate::utils::metrics::Metrics;
use crate::utils::latency_monitor::LatencyMonitor;
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
// use tokio::sync::mpsc;
use redis::AsyncCommands;

pub struct OrderExecutor {
    // brokers: Vec<BrokerInterface>,
    metrics: Metrics,
    latency_monitor: LatencyMonitor,
    config: HashMap<String, Value>,
    redis_client: redis::Client,
}

impl OrderExecutor {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        // let brokers = BrokerInterface::from_config(config);
        let metrics = Metrics::new(config);
        let latency_monitor = LatencyMonitor::new(config);
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        
        OrderExecutor {
            // brokers,
            metrics,
            latency_monitor,
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
        }
    }

    pub async fn execute_order(&mut self, signal: &str, size: f64, symbol: &str) -> Result<(), Box<dyn Error>> {
        let start_time = self.latency_monitor.start_measurement("order_execution");
        
        // Validate order parameters
        if !self.validate_order(signal, size, symbol) {
            self.metrics.log_error("Invalid order parameters");
            self.latency_monitor.end_measurement("order_execution", start_time).await?;
            return Err("Invalid order parameters".into());
        }

        // Select appropriate broker (simplified for now)
        // let broker = self.select_broker(symbol)?;
        
        // Execute order with latency monitoring (simplified)
        let execution_start = self.latency_monitor.start_measurement("broker_execution");
        // let result = broker.place_order(signal, size, symbol).await;
        let result: Result<(), Box<dyn Error>> = Ok(()); // Simplified for now
        let execution_latency = self.latency_monitor.end_measurement("broker_execution", execution_start).await?;
        
        // Log execution metrics
        self.metrics.log_execution(symbol, signal, size, execution_latency.as_micros());
        
        match result {
            Ok(_) => {
                // Store successful execution in Redis
                self.store_execution_result(symbol, signal, size, execution_latency, true).await?;
                
                // Log success metrics
                self.log_successful_execution(symbol, signal, size, execution_latency).await?;
                
                let total_latency = self.latency_monitor.end_measurement("order_execution", start_time).await?;
                Ok(())
            },
            Err(e) => {
                // Store failed execution in Redis
                self.store_execution_result(symbol, signal, size, execution_latency, false).await?;
                
                // Log error metrics
                self.log_failed_execution(symbol, signal, size, &e.to_string()).await?;
                
                self.metrics.log_error(&format!("Order execution failed: {}", e));
                self.latency_monitor.end_measurement("order_execution", start_time).await?;
                Err(e)
            }
        }
    }

    async fn store_execution_result(&self, symbol: &str, signal: &str, size: f64, latency: std::time::Duration, success: bool) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        
        let execution_data = serde_json::json!({
            "symbol": symbol,
            "signal": signal,
            "size": size,
            "latency_ms": latency.as_millis(),
            "success": success,
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs()
        });
        
        let key = format!("execution:orders:{}:{}", symbol, std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs());
        
        conn.hset(&key, "execution_data", serde_json::to_string(&execution_data)?).await?;
        conn.expire(&key, 86400).await?; // 24 hours
        
        Ok(())
    }

    async fn log_successful_execution(&self, symbol: &str, signal: &str, size: f64, latency: std::time::Duration) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        
        // Update success counters
        let success_key = format!("execution:success:{}", symbol);
        let success_count: i64 = conn.get(&success_key).await.unwrap_or(0);
        conn.set(&success_key, success_count + 1).await?;
        conn.expire(&success_key, 86400).await?; // 24 hours
        
        // Update average latency for symbol
        let latency_key = format!("execution:avg_latency:{}", symbol);
        let current_avg: f64 = conn.get(&latency_key).await.unwrap_or(0.0);
        let current_count: i64 = conn.get(&format!("{}:count", latency_key)).await.unwrap_or(0);
        
        let new_avg = ((current_avg * current_count as f64) + latency.as_millis() as f64) / (current_count + 1) as f64;
        conn.set(&latency_key, new_avg).await?;
        conn.set(&format!("{}:count", latency_key), current_count + 1).await?;
        conn.expire(&latency_key, 86400).await?;
        conn.expire(&format!("{}:count", latency_key), 86400).await?;
        
        Ok(())
    }

    async fn log_failed_execution(&self, symbol: &str, signal: &str, size: f64, error: &str) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        
        // Update failure counters
        let failure_key = format!("execution:failures:{}", symbol);
        let failure_count: i64 = conn.get(&failure_key).await.unwrap_or(0);
        conn.set(&failure_key, failure_count + 1).await?;
        conn.expire(&failure_key, 86400).await?; // 24 hours
        
        // Store error details
        let error_data = serde_json::json!({
            "symbol": symbol,
            "signal": signal,
            "size": size,
            "error": error,
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs()
        });
        
        conn.lpush("execution:errors", serde_json::to_string(&error_data)?).await?;
        conn.expire("execution:errors", 86400).await?; // 24 hours
        
        Ok(())
    }

    fn validate_order(&self, signal: &str, size: f64, symbol: &str) -> bool {
        // Basic validation
        if signal != "BUY" && signal != "SELL" {
            return false;
        }
        
        if size <= 0.0 {
            return false;
        }
        
        if symbol.is_empty() {
            return false;
        }
        
        // Check size limits from config
        let max_order_size = self.config.get("max_order_size").and_then(|v| v.as_f64()).unwrap_or(100000.0);
        if size > max_order_size {
            return false;
        }
        
        true
    }

    // fn select_broker(&self, symbol: &str) -> Result<&BrokerInterface, Box<dyn Error>> {
    //     // First try to find a broker that (simplified for now)
    //     // if let Some(broker) = self.brokers.iter().find(|b| b.supports_symbol(symbol)) {
    //     //     return Ok(broker);
    //     // }
    //     
    //     // If no specific broker found, try to select based on symbol type
    //     if symbol.contains("/") {
    //         // Forex or crypto pair
    //         if let Some(broker) = self.brokers.iter().find(|b| b.get_broker_type() == "forex") {
    //             return Ok(broker);
    //         }
    //     } else {
    //         // Stock or index
    //         if let Some(broker) = self.brokers.iter().find(|b| b.get_broker_type() == "stock") {
    //             return Ok(broker);
    //         }
    //     }
    //     
    //     // Fallback to first available broker
    //     self.brokers.first().ok_or("No suitable broker found".into())
    // }

    pub async fn get_execution_stats(&self, symbol: &str) -> Result<HashMap<String, f64>, Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        
        let mut stats = HashMap::new();
        
        // Get success count
        let success_key = format!("execution:success:{}", symbol);
        let success_count: i64 = conn.get(&success_key).await.unwrap_or(0);
        stats.insert("success_count".to_string(), success_count as f64);
        
        // Get failure count
        let failure_key = format!("execution:failures:{}", symbol);
        let failure_count: i64 = conn.get(&failure_key).await.unwrap_or(0);
        stats.insert("failure_count".to_string(), failure_count as f64);
        
        // Calculate success rate
        let total = success_count + failure_count;
        if total > 0 {
            stats.insert("success_rate".to_string(), (success_count as f64 / total as f64) * 100.0);
        } else {
            stats.insert("success_rate".to_string(), 0.0);
        }
        
        // Get average latency
        let latency_key = format!("execution:avg_latency:{}", symbol);
        let avg_latency: f64 = conn.get(&latency_key).await.unwrap_or(0.0);
        stats.insert("avg_latency_ms".to_string(), avg_latency);
        
        Ok(stats)
    }

    pub async fn get_all_execution_stats(&self) -> Result<HashMap<String, HashMap<String, f64>>, Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        
        // Get all symbols that have execution data
        let success_keys: Vec<String> = conn.keys("execution:success:*").await?;
        let mut all_stats = HashMap::new();
        
        for key in success_keys {
            let symbol = key.replace("execution:success:", "");
            let stats = self.get_execution_stats(&symbol).await?;
            all_stats.insert(symbol, stats);
        }
        
        Ok(all_stats)
    }
}
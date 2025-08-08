use std::collections::HashMap;
use std::time::{Duration, Instant};
use serde_json::Value;
use redis::AsyncCommands;
use std::error::Error;

pub struct LatencyMonitor {
    config: HashMap<String, Value>,
    redis_client: redis::Client,
    latency_threshold: Duration,
    measurements: HashMap<String, Vec<Duration>>,
}

impl LatencyMonitor {
    pub fn new(config: &HashMap<String, Value>) -> Self {
        let redis_url = config.get("redis_url").and_then(|v| v.as_str()).unwrap_or("redis://localhost:6379");
        let latency_threshold_ms = config.get("latency_threshold_ms").and_then(|v| v.as_u64()).unwrap_or(100);
        
        LatencyMonitor {
            config: config.clone(),
            redis_client: redis::Client::open(redis_url).expect("Failed to connect to Redis"),
            latency_threshold: Duration::from_millis(latency_threshold_ms),
            measurements: HashMap::new(),
        }
    }

    pub fn start_measurement(&self, operation: &str) -> Instant {
        Instant::now()
    }

    pub async fn end_measurement(&mut self, operation: &str, start_time: Instant) -> Result<Duration, Box<dyn Error>> {
        let duration = start_time.elapsed();
        
        // Store measurement
        self.measurements.entry(operation.to_string())
            .or_insert_with(Vec::new)
            .push(duration);
        
        // Keep only last 100 measurements per operation
        if let Some(measurements) = self.measurements.get_mut(operation) {
            if measurements.len() > 100 {
                measurements.remove(0);
            }
        }
        
        // Check if latency exceeds threshold
        if duration > self.latency_threshold {
            self.log_high_latency(operation, duration).await?;
        }
        
        // Store in Redis for monitoring
        self.store_latency_metric(operation, duration).await?;
        
        Ok(duration)
    }

    async fn log_high_latency(&self, operation: &str, duration: Duration) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        
        let latency_data = serde_json::json!({
            "operation": operation,
            "latency_ms": duration.as_millis(),
            "threshold_ms": self.latency_threshold.as_millis(),
            "timestamp": std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs()
        });
        
        conn.lpush("execution:high_latency", serde_json::to_string(&latency_data)?).await?;
        conn.expire("execution:high_latency", 3600).await?; // 1 hour
        
        Ok(())
    }

    async fn store_latency_metric(&self, operation: &str, duration: Duration) -> Result<(), Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        
        let metric_key = format!("execution:latency:{}", operation);
        let latency_ms = duration.as_millis() as f64;
        
        // Store current measurement
        conn.hset(&metric_key, "current_ms", latency_ms).await?;
        conn.hset(&metric_key, "timestamp", std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs()).await?;
        
        // Update running statistics
        let count_key = format!("{}:count", metric_key);
        let sum_key = format!("{}:sum", metric_key);
        let min_key = format!("{}:min", metric_key);
        let max_key = format!("{}:max", metric_key);
        
        let count: i64 = conn.get(&count_key).await.unwrap_or(0);
        let sum: f64 = conn.get(&sum_key).await.unwrap_or(0.0);
        let min: f64 = conn.get(&min_key).await.unwrap_or(f64::MAX);
        let max: f64 = conn.get(&max_key).await.unwrap_or(0.0);
        
        conn.set(&count_key, count + 1).await?;
        conn.set(&sum_key, sum + latency_ms).await?;
        conn.set(&min_key, min.min(latency_ms)).await?;
        conn.set(&max_key, max.max(latency_ms)).await?;
        
        // Calculate and store average
        let avg = (sum + latency_ms) / (count + 1) as f64;
        conn.hset(&metric_key, "avg_ms", avg).await?;
        conn.hset(&metric_key, "min_ms", min.min(latency_ms)).await?;
        conn.hset(&metric_key, "max_ms", max.max(latency_ms)).await?;
        conn.hset(&metric_key, "count", count + 1).await?;
        
        // Set expiration
        conn.expire(&metric_key, 3600).await?; // 1 hour
        conn.expire(&count_key, 3600).await?;
        conn.expire(&sum_key, 3600).await?;
        conn.expire(&min_key, 3600).await?;
        conn.expire(&max_key, 3600).await?;
        
        Ok(())
    }

    pub async fn get_latency_stats(&self, operation: &str) -> Result<HashMap<String, f64>, Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        let metric_key = format!("execution:latency:{}", operation);
        
        let stats: HashMap<String, f64> = conn.hgetall(&metric_key).await?;
        Ok(stats)
    }

    pub async fn get_all_latency_stats(&self) -> Result<HashMap<String, HashMap<String, f64>>, Box<dyn Error>> {
        let mut conn = self.redis_client.get_async_connection().await?;
        let keys: Vec<String> = conn.keys("execution:latency:*").await?;
        
        let mut all_stats = HashMap::new();
        for key in keys {
            let operation = key.replace("execution:latency:", "");
            let stats: HashMap<String, f64> = conn.hgetall(&key).await?;
            all_stats.insert(operation, stats);
        }
        
        Ok(all_stats)
    }

    pub fn get_average_latency(&self, operation: &str) -> Option<Duration> {
        if let Some(measurements) = self.measurements.get(operation) {
            if !measurements.is_empty() {
                let total: Duration = measurements.iter().sum();
                Some(Duration::from_millis(total.as_millis() as u64 / measurements.len() as u64))
            } else {
                None
            }
        } else {
            None
        }
    }

    pub fn get_percentile_latency(&self, operation: &str, percentile: f64) -> Option<Duration> {
        if let Some(measurements) = self.measurements.get(operation) {
            if !measurements.is_empty() {
                let mut sorted = measurements.clone();
                sorted.sort();
                let index = (percentile * measurements.len() as f64) as usize;
                sorted.get(index).copied()
            } else {
                None
            }
        } else {
            None
        }
    }

    pub async fn reset_measurements(&mut self) {
        self.measurements.clear();
        
        // Clear Redis metrics
        if let Ok(mut conn) = self.redis_client.get_async_connection().await {
            let _: Result<(), _> = conn.del("execution:latency:*").await;
        }
    }
}

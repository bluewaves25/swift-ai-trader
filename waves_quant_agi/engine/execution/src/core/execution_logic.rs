use crate::core::order_executor::OrderExecutor;
use crate::core::slippage_controller::SlippageController;
use crate::utils::metrics::Metrics;
use crate::utils::risk_filters::RiskFilters;
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use tokio::sync::mpsc;

pub struct ExecutionLogic {
    order_executor: OrderExecutor,
    slippage_controller: SlippageController,
    risk_filters: RiskFilters,
    metrics: Metrics,
    config: HashMap<String, Value>,
    rx: mpsc::Receiver<HashMap<String, Value>>,
}

impl ExecutionLogic {
    pub fn new(config: &HashMap<String, Value>, tx: mpsc::Sender<HashMap<String, Value>>) -> Self {
        ExecutionLogic {
            order_executor: OrderExecutor::new(config),
            slippage_controller: SlippageController::new(config),
            risk_filters: RiskFilters::new(config),
            metrics: Metrics::new(config),
            config: config.clone(),
            rx: mpsc::Receiver::new(tx),
        }
    }

    pub async fn start(&mut self, mut rx: mpsc::Receiver<HashMap<String, Value>>) -> Result<(), Box<dyn Error>> {
        while let Some(signal) = rx.recv().await {
            let symbol = signal.get("symbol").and_then(|v| v.as_str()).unwrap_or("BTC/USD");
            let size = signal.get("size").and_then(|v| v.as_f64()).unwrap_or(0.0);
            let signal_type = signal.get("signal").and_then(|v| v.as_str()).unwrap_or("");
            let expected_price = signal.get("expected_price").and_then(|v| v.as_f64()).unwrap_or(0.0);

            if self.risk_filters.apply_filters(symbol, size).await.is_ok() {
                if self.slippage_controller.check_slippage(symbol, expected_price, expected_price).await.is_ok() {
                    if let Err(e) = self.order_executor.execute_order(signal_type, size, symbol).await {
                        self.metrics.log_error(&format!("Execution failed: {}", e));
                    }
                }
            }
        }
        Ok(())
    }
}
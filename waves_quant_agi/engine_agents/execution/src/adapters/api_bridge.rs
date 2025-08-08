use serde_json::{Value, json};
use std::collections::HashMap;
use std::error::Error;
use tokio::sync::mpsc;
use tonic::{transport::Server, Request, Response, Status};
use proto::execution_service_server::{ExecutionService, ExecutionServiceServer};
use proto::execution::{ExecuteTradeRequest, ExecuteTradeResponse};

mod proto {
    tonic::include_proto!("execution");
}

pub struct ApiBridge {
    tx: mpsc::Sender<HashMap<String, Value>>,
}

impl ApiBridge {
    pub fn new(tx: mpsc::Sender<HashMap<String, Value>>) -> Self {
        ApiBridge { tx }
    }

    pub async fn start_server(&self, addr: &str) -> Result<(), Box<dyn Error>> {
        let addr = addr.parse()?;
        Server::builder()
            .add_service(ExecutionServiceServer::new(self))
            .serve(addr)
            .await?;
        Ok(())
    }
}

#[tonic::async_trait]
impl ExecutionService for ApiBridge {
    async fn execute_trade(
        &self,
        request: Request<ExecuteTradeRequest>,
    ) -> Result<Response<ExecuteTradeResponse>, Status> {
        let req = request.into_inner();
        let signal = json!({
            "signal": req.signal,
            "size": req.size,
            "symbol": req.symbol,
            "expected_price": req.expected_price,
        });
        self.tx.send(signal.as_object().unwrap().clone()).await
            .map_err(|e| Status::internal(format!("Failed to send signal: {}", e)))?;
        Ok(Response::new(ExecuteTradeResponse {
            status: "success".to_string(),
        }))
    }
}
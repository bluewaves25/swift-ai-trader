use crate::core::execution_logic::ExecutionLogic;
use crate::utils::config_loader::ConfigLoader;
use std::error::Error;
use tokio::sync::mpsc;

pub async fn start_execution() -> Result<(), Box<dyn Error>> {
    let config = ConfigLoader::load("config.yaml")?;
    let (tx, rx) = mpsc::channel(100);
    let mut execution_logic = ExecutionLogic::new(&config, tx);
    execution_logic.start(rx).await?;
    Ok(())
}
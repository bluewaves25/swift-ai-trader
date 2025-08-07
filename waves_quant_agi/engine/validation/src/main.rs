use quantum_agents_validation::orchestrator::Orchestrator;
use quantum_agents_validation::utils::config_loader::ConfigLoader;
use std::error::Error;
use tokio::sync::mpsc;

mod lib;
mod orchestrator;
mod router;
mod validators;
mod utils;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let config = ConfigLoader::load("config.yaml")?;
    let (tx, rx) = mpsc::channel(100);
    let mut orchestrator = Orchestrator::new(&config, tx);
    orchestrator.start(rx).await?;
    Ok(())
}
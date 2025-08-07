Validators Agent Overview
Purpose
The Validators Agent ensures only safe, sane, and provably correct instructions, data, and decisions reach the Execution Agent or critical operations in the QUANTUM_AGENTS trading system. It acts as a strict gatekeeper, validating market data, strategies, trade orders, and execution requests without performing execution, manipulation, or analytics.
Core Principle
"Every action must be provably valid."
Key Traits

Independent: Operates autonomously, decoupled from strategy, execution, or adapter agents.
Modular: Plugs into systems via gRPC, IPC, or FFI interfaces.
Fast & Scalable: Validates in real-time or batch-mode using Rust's concurrency (tokio).
Self-Learning: Adapts validation rules via a Python learning layer with PyO3.
Strict: Rejects invalid inputs with detailed reasons.

Responsibilities

Data Validation: Checks timestamp freshness, data integrity, and source authenticity.
Strategy Validation: Ensures strategies are logical, not overfit, and risk-compliant.
Order Validation: Verifies trade symbols, sizes, types, and risk controls.
Execution Request Validation: Confirms alignment with signals and broker specs.
Verdict Output: Provides "valid," "warning," or "reject" with metadata.

Architecture

Rust Core: Handles low-latency validation (validators/ modules).
Python Learning Layer: Analyzes outcomes and refines rules (learning_layer/).
Redis Communication: Uses validation_input and validation_output channels.
APIs: Exposes REST/gRPC endpoints for external integration.

Scope
Supports HFT across Forex, Crypto, Indices, and Commodities, ensuring system integrity and safety.
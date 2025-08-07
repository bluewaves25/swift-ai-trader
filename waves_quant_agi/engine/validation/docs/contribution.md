Contribution Guidelines
Overview
Contributions to the Validators Agent enhance its role as a gatekeeper for safe, provably correct trading decisions in QUANTUM_AGENTS.
Guidelines

Code Style:
Rust: Follow Rustfmt and Clippy for src/ files.
Python: Adhere to PEP 8 for learning_layer/ files.
Documentation: Use Markdown with clear headings and examples.


Validation Rules:
Add new validators in validators/ (e.g., new_validator.rs under risk/ or strategy/).
Ensure rules are modular, configurable via config.yaml, and log to validation:errors.
Example: Add max_volatility_check.rs to validate against volatility spikes.


Learning Layer:
Extend learning_layer/internal/ (e.g., new anomaly detection in anomaly_detector.py).
Use sklearn for models, store outputs in Redis (validation:model:*).
Trigger retraining via retraining_loop.py for new rules.


Testing:
Add unit tests in validators/ for 95% coverage (use cargo test).
Include integration tests for Redis communication and API endpoints.
Simulate edge cases (e.g., black swan events) in counterfactual_simulator.py.


Documentation:
Update docs/ with new validators (workflow.md), APIs (api_documentation.md), or integration details (integration.md).
Provide examples: JSON payloads, error cases, expected outputs.


Submission:
Fork repository, create feature branch (feature/new-validator).
Submit PR with clear description, referencing updated files.
Ensure CI passes (Rustfmt, Clippy, tests).



Example Contribution

New Validator: Add max_drawdown.rs in validators/risk/.
Check: Portfolio drawdown ≤ 20%.
Log: validation:errors on failure.
Update: router.rs, workflow.md.


New Learning Module: Add pattern_analyzer.py in learning_layer/internal/.
Analyze recurring failure patterns.
Store in validation:patterns:*.
Notify retraining_loop.



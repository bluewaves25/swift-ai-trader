Training Protocols
Overview
The Validators Agent uses a Python-based learning_layer/ to refine validation rules and models, improving accuracy and reducing false positives/negatives.
Protocols

Periodic Retraining: retraining_loop.py triggers every 7 days (retrain_interval) or when error rate exceeds 15% (anomaly_threshold).
Failure-Based Retraining: Initiated when validation failures exceed 10% (error_threshold) via research_engine.py.
Training Process: training_module.py trains models (e.g., IsolationForest) on failure data, targeting 85% accuracy (accuracy_threshold).
Data Sources: Validation outcomes from validation:failures:* and validation:audit:* Redis keys.
Output: Updated models stored in validation:model:latest with 7-day expiry.

Implementation

Data Flow: Failures collected by research_engine.py, processed by training_module.py.
Validation: external_strategy_validator.py ensures external strategies align with rules.
Feedback Loop: audit_memory.py logs accuracy; counterfactual_simulator.py evaluates rejected scenarios.
Rust Integration: Model updates sent to Rust via PyO3 (orchestrator.rs).

Scope

Focuses on validation-specific improvements (e.g., detecting subtle data anomalies).
Supports Forex, Crypto, Indices, and Commodities.
Ensures autonomy with no human intervention post-stabilization.

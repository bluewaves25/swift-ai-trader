API Documentation
Pattern Recognition

CorrelationMatrix:
build_correlation_matrix(agent_metrics): Builds correlation matrix for agent metrics. Returns dict.
Input: [{"agent": str, "speed": float, "accuracy": float, "cost": float, "error_rate": float}].
Output: {"correlations": dict, "timestamp": int, "description": str}.


AnomalyDetector:
detect_anomalies(agent_metrics): Detects anomalies (>2 std dev). Returns list of issues.
Input: Same as above.
Output: [{"agent": str, "metric_type": str, "value": float, "threshold": float, "timestamp": int, "description": str}].


TimingWindowOptimizer:
optimize_timing(agent_metrics): Optimizes execution timing (>10% overlap). Returns dict.
Input: Same as above.
Output: {"agent": {"delay_ms": float}, "timestamp": int, "description": str}.



GNN Models

AgentGraphBuilder:
build_agent_graph(agent_metrics): Builds agent relationship graph. Returns dict.
Input: Same as above.
Output: {"graph": nx.DiGraph, "metadata": {"nodes": list, "edges": list, "timestamp": int, "description": str}}.


CoordinationGNN:
train_gnn(agent_metrics): Trains GNN for coordination. Returns dict.
optimize_coordination(agent_metrics): Suggests coordination improvements. Returns dict.
Input: Same as above.
Output: {"node_count": int, "timestamp": int, "description": str} or {"suggestions": [{"agent": str, "priority": float}], "timestamp": int, "description": str}.


FeedbackLoopMonitor:
monitor_feedback_loops(agent_metrics): Detects feedback loops (>0.8 weight). Returns list.
Input: Same as above.
Output: [{"agents": list, "weight": float, "timestamp": int, "description": str}].



Online Learning

ReinforcementScorer:
score_agents(agent_metrics): Scores agents with RL rewards. Returns dict.
Input: Same as above.
Output: {"agent": float, "timestamp": int, "description": str}.


EvolutionScheduler:
schedule_evolution(agent_metrics): Schedules periodic coordination updates. Runs indefinitely.
Input: Same as above.


AgentFeedbackTrainer:
train_on_feedback(feedback_data): Trains on feedback data. Returns dict.
Input: [{"agent": str, "performance_score": float}].
Output: {"agent": {"priority_adjustment": float}, "timestamp": int, "description": str}.



Transformers

InterAgentTransformer:
process_interactions(agent_interactions): Processes interactions with BERT. Returns dict.
Input: [{"agent1": str, "agent2": str, "task": str}].
Output: {"embeddings": list, "metadata": {"interaction_count": int, "timestamp": int, "description": str}}.


ConflictResolver:
resolve_conflicts(conflicts): Resolves conflicts using transformer. Returns list.
Input: Same as above.
Output: [{"agents": list, "task": str, "resolution": str, "timestamp": int, "description": str}].


ModelExplainer:
explain_decision(decision): Explains coordination decisions. Returns dict.
Input: {"agent1": str, "agent2": str, "task": str, "resolution": str}.
Output: {"agents": list, "task": str, "explanation": str, "timestamp": int, "description": str}.



Learning Layer

Internal/ResearchEngine:
analyze_coordination_patterns(key_pattern): Analyzes patterns from incidents. Returns dict.
Input: str (Redis key pattern, default "*").
Output: {"by_agent": dict, "by_task": dict, "conflict_patterns": list, "high_impact_conflicts": list, "timestamp": int, "description": str}.


Internal/TrainingModule:
prepare_dataset(key_pattern): Prepares internal dataset. Returns list.
train_model(dataset): Trains coordination model. Returns dict.
Input: str or [{"agents": list, "task": str, "score": float, "timestamp": int}].
Output: [{"agents": list, "task": str, "score": float, "timestamp": int}] or {"policy_count": int, "timestamp": int, "description": str}.


Internal/RetrainingLoop:
run_retraining(): Runs periodic retraining. Runs indefinitely.


External/WebIntelligence/AILabScraper:
scrape_ai_research(): Scrapes AI research. Returns list.
Output: [{"source": str, "title": str, "description": str, "timestamp": int}].


External/WebIntelligence/OrchestrationCases:
extract_case_studies(): Extracts case studies. Returns list.
Output: Same as above.


External/WebIntelligence/ArchitectureMonitor:
monitor_architecture_shifts(): Monitors architecture trends. Returns list.
Output: Same as above.


External/SocialAnalyzer/AgentSentiment:
analyze_sentiment(social_data): Analyzes agent feedback sentiment. Returns list.
Input: [{"agent": str, "text": str, "source": str}].
Output: [{"agent": str, "source": str, "sentiment_score": float, "timestamp": int, "description": str}].


External/SocialAnalyzer/SystemConfidence:
measure_confidence(social_data): Measures system trust. Returns dict.
Input: Same as above.
Output: {"average_score": float, "data_points": int, "timestamp": int, "description": str}.


External/IntelligenceFusion/AgentFusionEngine:
fuse_insights(key_pattern): Fuses internal/external insights. Returns list.
Input: str (Redis key pattern, default "*").
Output: [{"agents": list, "task": str, "internal_score": float, "external_relevance": float, "timestamp": int}].


External/IntelligenceFusion/SystemPredictor:
predict_system_risks(): Predicts systemic risks (>0.7). Returns list.
Output: [{"agents": list, "task": str, "risk_score": float, "timestamp": int, "description": str}].


HybridTraining/OrchestrationTrainer:
prepare_combined_dataset(key_pattern): Prepares combined dataset. Returns list.
train_model(dataset): Trains hybrid model. Returns dict.
Input: str or [{"agents": list, "task": str, "internal_score": float, "external_relevance": float, "timestamp": int}].
Output: [{"agents": list, "task": str, "internal_score": float, "external_relevance": float, "timestamp": int}] or {"policy_count": int, "timestamp": int, "description": str}.


HybridTraining/ExternalStrategyValidator:
validate_strategies(key_pattern): Validates strategies (>0.8 diff). Returns list.
Input: str.
Output: [{"agents": list, "task": str, "score_diff": float, "timestamp": int, "description": str}].



Integration

Redis Channels: Publish results to "intelligence_instruction".
Dependencies: IncidentCache.store_incident(), FailureAgentLogger.log_issue().

Adapters Agent Workflow
The Adapters Agent operates in a continuous, circular process to handle orders, monitor brokers, and improve performance. Below is the workflow:

Order Submission:

Internal system submits an order in standard format.
OrderNormalizer validates and normalizes the order.


Broker Selection:

BrokerRouter uses the current strategy (LowestFeeStrategy or FastestRouteStrategy) to select the best broker based on PerformanceTracker metrics and BrokerIntelligence recommendations.


Order Formatting:

Selected broker's adapter (BinanceAdapter, CoinbaseAdapter, or ExnessAdapter) formats the normalized order to the broker-specific format, handling quirks via handle_broker_quirks.


Order Execution:

BrokerRouter sends the formatted order to the broker via the adapter's send_order method.
RetryHandler executes the request with exponential backoff if it fails.


Order Confirmation:

Adapter confirms order status using confirm_order.
Success or failure is logged by BrokerLogger.


Performance Tracking:

PerformanceTracker records latency, success/failure, and fees.
PatternAnalyzer logs failures for pattern analysis.


Health Monitoring:

HealthChecker pings brokers periodically to update statuses.
APIMonitor checks for API updates and notifies changes.


Learning and Optimization:

PatternAnalyzer analyzes failure patterns.
BrokerIntelligence updates recommendations (e.g., disable broker, adjust priority).
RetryHandler adjusts retry parameters based on success rates.


Feedback Loop:

Recommendations and metrics feed back into BrokerRouter for future broker selection.
Process repeats for the next order, continuously improving.



Circular Nature
The workflow loops indefinitely, with each cycle refining broker selection, retry strategies, and performance through real-time monitoring and learning. Logs are maintained for auditing, and API updates are incorporated to ensure compatibility.
Diagram
graph TD
    A[Order Submission] --> B[Order Normalizer]
    B --> C[Broker Router]
    C --> D[Broker Adapter]
    D --> E[Order Execution]
    E --> F[Order Confirmation]
    F --> G[Performance Tracker]
    F --> H[Pattern Analyzer]
    G --> I[Health Checker]
    H --> J[Broker Intelligence]
    I --> K[API Monitor]
    J --> C
    K --> C
    C --> A

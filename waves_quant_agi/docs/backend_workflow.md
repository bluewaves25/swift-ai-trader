🔁 docs/backend_workflow.md – How the engine runs from start to finish

📘 Plain English Explanation:
This file explains the step-by-step process that happens whenever a user interacts with the system or when strategies are running.

Example Workflow:
User clicks a button on the frontend (e.g., to trade or deposit).

That action hits the API (like a receptionist).

The API passes the request to the services (business rules).

The services call the engine (strategies, brokers, validators).

The engine may talk to a broker to place a trade or check data.

Results are saved to the database and returned to the user.

Special Engine Flow:
Market data goes into the system

AI strategies analyze it

Signals are generated (e.g., "Buy BTC now")

The execution engine places the trade

Profit/loss is saved and used to improve the system
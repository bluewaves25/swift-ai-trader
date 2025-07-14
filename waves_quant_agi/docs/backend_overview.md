🧾 docs/backend_overview.md – What the backend is and what it does

📘 Plain English Explanation:
This document gives a general introduction to what the backend is doing. Think of the backend as the brain and memory of your AGI trading system.

It controls:

All AI strategies that decide what to trade

Who owns what (portfolios, money, strategies)

Payments and connections to platforms like Binance or MT5

Talking to databases, processing trades, logging actions, etc.

Main Components:
FastAPI → Like a receptionist; takes requests from the frontend

PostgreSQL + TimescaleDB → Memory bank that remembers trades, users, and results

Supabase → Like a customer login manager

Redis → Super-fast notepad for real-time stuff

RabbitMQ → A queue that makes sure tasks don’t crash into each other

Docker → Packages and isolates all tools so they don’t fight
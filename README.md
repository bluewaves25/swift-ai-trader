Waves Quant Engine
High-frequency trading platform for multiple brokers (Exness, Binance).
Setup

Install Dependencies:
cd backend
npm install
pip install -r requirements.txt


Configure Environment:

Copy backend/.env.example to backend/.env and fill in credentials.


Run with Docker:
docker-compose up --build


Run Locally:
cd backend/src
npm run dev


Access:

Backend: http://localhost:3000
Frontend: Integrate with your existing frontend.



API Endpoints

GET /balance/:broker/:account: Fetch balance.
POST /trade/:broker/:account: Execute trade.
POST /deposit/:broker/:account: Request deposit.
POST /withdraw/:broker/:account: Request withdrawal.

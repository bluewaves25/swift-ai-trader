
# Waves Quant Engine Backend API Documentation

## Overview
The Waves Quant Engine backend provides a comprehensive REST API for multi-asset trading platform operations, including real-time trading engine control, market data processing, and risk management.

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints require valid authentication tokens in the Authorization header:
```
Authorization: Bearer <your-token>
```

## Core Endpoints

### Health Check
- **GET** `/` - Basic API information and status
- **GET** `/health` - Detailed health check with engine status

### Trading Engine Control

#### Start Trading Engine
- **POST** `/api/engine/start`
- **Description**: Starts the automated trading engine
- **Response**: 
```json
{
  "status": "success",
  "message": "Trading engine started",
  "start_time": "2024-01-01T00:00:00Z"
}
```

#### Stop Trading Engine  
- **POST** `/api/engine/stop`
- **Description**: Stops the automated trading engine
- **Response**:
```json
{
  "status": "success",
  "message": "Trading engine stopped",
  "statistics": {
    "total_signals": 150,
    "total_trades": 45,
    "uptime": "2024-01-01T00:00:00Z"
  }
}
```

#### Emergency Stop
- **POST** `/api/engine/emergency-stop`
- **Description**: Immediately halts all trading activities and closes positions
- **Response**:
```json
{
  "status": "success",
  "message": "Emergency stop executed - All trading halted",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Engine Status
- **GET** `/api/engine/status`
- **Description**: Get current trading engine status
- **Response**:
```json
{
  "is_running": true,
  "start_time": "2024-01-01T00:00:00Z",
  "total_signals": 150,
  "total_trades": 45,
  "active_pairs": ["EURUSD", "GBPUSD", "BTCUSD"]
}
```

### Trading Operations

#### Execute Trade
- **POST** `/api/trade/execute`
- **Body**:
```json
{
  "symbol": "EURUSD",
  "trade_type": "buy",
  "amount": 0.1
}
```

#### Get Trade History
- **GET** `/api/trade/history?symbol=EURUSD`
- **Parameters**: 
  - `symbol` (optional): Filter by trading pair

### Wallet Operations

#### Get Balance
- **GET** `/api/wallet/balance?user_id={user_id}`

#### Update Balance
- **POST** `/api/wallet/update`
- **Body**:
```json
{
  "user_id": "uuid",
  "balance": 1000.00
}
```

### Strategy Operations

#### Get AI Signals
- **GET** `/api/strategies/signals?symbol=EURUSD`
- **Description**: Get AI-generated trading signals

#### Get Strategy Performance
- **GET** `/api/strategies/performance?symbol=EURUSD`
- **Description**: Get performance metrics for trading strategies

#### Update Risk Parameters
- **POST** `/api/strategies/risk`
- **Body**:
```json
{
  "max_position_size": 0.1,
  "stop_loss_percentage": 0.02,
  "take_profit_percentage": 0.04
}
```

## Trading Engine Architecture

### Real-Time Processing
The trading engine runs as a background service that:
1. Continuously monitors market data
2. Generates AI-powered trading signals
3. Executes trades based on predefined strategies
4. Manages risk parameters
5. Sends email notifications for important events

### Signal Generation Process
1. **Market Data Collection**: Real-time data from multiple sources
2. **AI Analysis**: Multiple strategy algorithms (breakout, mean reversion, momentum)
3. **Signal Generation**: Buy/sell/hold recommendations with confidence scores
4. **Risk Assessment**: Position sizing and risk validation
5. **Trade Execution**: Automated order placement via broker APIs

### Risk Management
- Maximum position size limits
- Stop-loss and take-profit automation
- Daily loss limits
- Emergency stop functionality
- Real-time monitoring and alerts

## Error Handling
All endpoints return standardized error responses:
```json
{
  "error": "Error description",
  "detail": "Detailed error information",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Rate Limiting
- 100 requests per minute for standard endpoints
- 10 requests per minute for trading execution endpoints
- 5 requests per minute for engine control endpoints

## WebSocket Support (Coming Soon)
Real-time updates for:
- Live market data
- Trading signals
- Order status
- Portfolio updates

## Security Features
- JWT token authentication
- Request/response logging
- Rate limiting
- Input validation
- SQL injection protection
- CORS configuration

## Deployment
The backend is containerized and can be deployed using:
```bash
docker-compose up -d
```

## Environment Variables
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
EXNESS_API_KEY=your_exness_api_key
EXNESS_API_SECRET=your_exness_secret
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_secret
NOTIFICATION_EMAIL=adus7661@gmail.com
```

## Support
For API support and documentation updates, contact: adus7661@gmail.com


# API Reference - Waves Quant Engine

## Overview

The Waves Quant Engine uses Supabase as its backend, providing a comprehensive REST API with real-time capabilities. This document covers all available API endpoints, data models, and integration patterns.

## Authentication

All API requests require authentication via Supabase Auth. The system uses JWT tokens for secure access.

### Authentication Endpoints

#### Sign Up
```http
POST /auth/v1/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "data": {
    "role": "investor" // or "owner"
  }
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "session": {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "expires_in": 3600
  }
}
```

#### Sign In
```http
POST /auth/v1/token?grant_type=password
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Sign Out
```http
POST /auth/v1/logout
Authorization: Bearer <access_token>
```

## Core API Endpoints

### Trading Pairs

#### Get All Trading Pairs
```http
GET /rest/v1/trading_pairs?select=*&is_active=eq.true
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "symbol": "BTCUSDT",
    "base_currency": "BTC",
    "quote_currency": "USDT",
    "is_active": true,
    "min_trade_amount": 0.001,
    "max_trade_amount": 1000,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

#### Create Trading Pair (Owner Only)
```http
POST /rest/v1/trading_pairs
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "symbol": "ETHUSDT",
  "base_currency": "ETH", 
  "quote_currency": "USDT",
  "min_trade_amount": 0.01,
  "max_trade_amount": 500
}
```

### Market Data

#### Get Market Data for Pair
```http
GET /rest/v1/market_data?select=*&pair_id=eq.<uuid>&order=timestamp.desc&limit=50
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "pair_id": "uuid",
    "timestamp": "2025-01-01T12:00:00Z",
    "open_price": 50000.00,
    "high_price": 50200.00,
    "low_price": 49800.00,
    "close_price": 50100.00,
    "volume": 1000000.00,
    "market_condition": "trending_up",
    "rsi": 65.5,
    "macd": 150.25,
    "bollinger_upper": 51000.00,
    "bollinger_lower": 49000.00,
    "support_level": 49500.00,
    "resistance_level": 50500.00
  }
]
```

#### Insert Market Data (System Only)
```http
POST /rest/v1/market_data
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "pair_id": "uuid",
  "open_price": 50000.00,
  "high_price": 50200.00,
  "low_price": 49800.00,
  "close_price": 50100.00,
  "volume": 1000000.00,
  "market_condition": "trending_up",
  "rsi": 65.5,
  "macd": 150.25
}
```

### AI Signals

#### Get Recent Signals
```http
GET /rest/v1/ai_signals?select=*,trading_pairs(symbol)&order=created_at.desc&limit=20
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "pair_id": "uuid",
    "signal": "buy",
    "confidence": 0.85,
    "strategy_used": "breakout",
    "entry_price": 50100.00,
    "stop_loss": 49000.00,
    "take_profit": 52000.00,
    "reasoning": "Strong upward breakout with high volume confirmation",
    "executed": false,
    "created_at": "2025-01-01T12:00:00Z",
    "trading_pairs": {
      "symbol": "BTCUSDT"
    }
  }
]
```

#### Create AI Signal
```http
POST /rest/v1/ai_signals
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "pair_id": "uuid",
  "signal": "buy",
  "confidence": 0.85,
  "strategy_used": "breakout",
  "entry_price": 50100.00,
  "stop_loss": 49000.00,
  "take_profit": 52000.00,
  "reasoning": "Strong upward breakout confirmed"
}
```

### Trades

#### Get Trade History
```http
GET /rest/v1/trades?select=*,trading_pairs(symbol),ai_signals(strategy_used,confidence)&order=created_at.desc&limit=100
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "signal_id": "uuid",
    "pair_id": "uuid", 
    "trade_type": "buy",
    "amount": 0.1,
    "entry_price": 50100.00,
    "exit_price": 51500.00,
    "stop_loss": 49000.00,
    "take_profit": 52000.00,
    "status": "executed",
    "profit_loss": 140.00,
    "execution_time": "2025-01-01T12:01:00Z",
    "created_at": "2025-01-01T12:00:00Z",
    "closed_at": "2025-01-01T12:30:00Z",
    "trading_pairs": {
      "symbol": "BTCUSDT"
    },
    "ai_signals": {
      "strategy_used": "breakout",
      "confidence": 0.85
    }
  }
]
```

#### Execute Trade
```http
POST /rest/v1/trades
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "signal_id": "uuid",
  "pair_id": "uuid",
  "trade_type": "buy",
  "amount": 0.1,
  "entry_price": 50100.00,
  "stop_loss": 49000.00,
  "take_profit": 52000.00
}
```

### GET /api/investor/trades

Returns the trade history for the current user.

**Response:**
- 200 OK: Array of Trade objects

**Trade object:**
- id: string
- user_id: string
- symbol: string
- side: string (buy/sell)
- volume: float
- price: float
- pnl: float
- strategy: string | null
- timestamp: datetime
- status: string (open/closed/cancelled)

Example:
```json
[
  {
    "id": "...",
    "user_id": "...",
    "symbol": "BTCUSD",
    "side": "buy",
    "volume": 0.5,
    "price": 42000.0,
    "pnl": 120.5,
    "strategy": "Breakout",
    "timestamp": "2024-07-08T12:34:56Z",
    "status": "closed"
  }
]
```

### Portfolio Management

#### Get User Portfolio
```http
GET /rest/v1/portfolios?select=*&user_id=eq.<user_uuid>
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "total_balance": 10000.00,
    "available_balance": 8500.00,
    "unrealized_pnl": 250.00,
    "realized_pnl": 450.00,
    "total_trades": 25,
    "winning_trades": 18,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  }
]
```

#### Update Portfolio
```http
PATCH /rest/v1/portfolios?user_id=eq.<user_uuid>
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "total_balance": 10500.00,
  "available_balance": 9000.00,
  "realized_pnl": 500.00,
  "total_trades": 26,
  "winning_trades": 19
}
```

### Risk Settings

#### Get Risk Settings
```http
GET /rest/v1/risk_settings?select=*&user_id=eq.<user_uuid>
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "max_daily_loss": 100.00,
    "max_position_size": 0.05,
    "stop_loss_percentage": 0.02,
    "take_profit_percentage": 0.04,
    "max_open_positions": 5,
    "risk_per_trade": 0.01,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

#### Update Risk Settings
```http
PATCH /rest/v1/risk_settings?user_id=eq.<user_uuid>
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "max_daily_loss": 150.00,
  "max_position_size": 0.08,
  "stop_loss_percentage": 0.025
}
```

### Strategy Management

#### Get Pair Strategies
```http
GET /rest/v1/pair_strategies?select=*,trading_pairs(symbol,base_currency,quote_currency)&order=performance_score.desc
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "pair_id": "uuid",
    "current_strategy": "breakout",
    "confidence_score": 0.78,
    "performance_score": 0.82,
    "total_trades": 45,
    "winning_trades": 32,
    "last_updated": "2025-01-01T12:00:00Z",
    "strategy_params": {
      "lookback_period": 20,
      "volume_threshold": 1.5
    },
    "trading_pairs": {
      "symbol": "BTCUSDT",
      "base_currency": "BTC",
      "quote_currency": "USDT"
    }
  }
]
```

#### Update Strategy
```http
PATCH /rest/v1/pair_strategies?pair_id=eq.<pair_uuid>
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_strategy": "mean_reversion",
  "confidence_score": 0.75,
  "strategy_params": {
    "rsi_oversold": 25,
    "rsi_overbought": 75
  }
}
```

### Performance Analytics

#### Get Performance Data
```http
GET /rest/v1/performance_analytics?select=*&order=date.desc&limit=30
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "date": "2025-01-01",
    "total_trades": 12,
    "winning_trades": 8,
    "total_profit": 245.50,
    "total_volume": 15000.00,
    "sharpe_ratio": 1.25,
    "max_drawdown": 0.03,
    "win_rate": 0.67,
    "avg_profit_per_trade": 20.46,
    "created_at": "2025-01-01T23:59:59Z"
  }
]
```

## Real-time Subscriptions

### WebSocket Connections

The Waves Quant Engine uses Supabase real-time subscriptions for live updates.

#### Subscribe to Market Data Updates
```javascript
const marketDataSubscription = supabase
  .channel('market_data_changes')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'market_data' },
    (payload) => {
      console.log('New market data:', payload.new);
    }
  )
  .subscribe();
```

#### Subscribe to AI Signals
```javascript
const signalsSubscription = supabase
  .channel('ai_signals_changes')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'ai_signals' },
    (payload) => {
      console.log('New AI signal:', payload.new);
    }
  )
  .subscribe();
```

#### Subscribe to Trade Updates
```javascript
const tradesSubscription = supabase
  .channel('trades_changes')
  .on('postgres_changes', 
    { event: '*', schema: 'public', table: 'trades' },
    (payload) => {
      if (payload.eventType === 'INSERT') {
        console.log('New trade:', payload.new);
      } else if (payload.eventType === 'UPDATE') {
        console.log('Trade updated:', payload.new);
      }
    }
  )
  .subscribe();
```

#### Subscribe to Portfolio Updates
```javascript
const portfolioSubscription = supabase
  .channel('portfolio_changes')
  .on('postgres_changes', 
    { 
      event: 'UPDATE', 
      schema: 'public', 
      table: 'portfolios',
      filter: `user_id=eq.${userId}`
    },
    (payload) => {
      console.log('Portfolio updated:', payload.new);
    }
  )
  .subscribe();
```

## Owner/Admin Endpoints

### POST /api/owner/engine/start
Start the AGI engine.

### POST /api/owner/engine/stop
Stop the AGI engine.

### POST /api/owner/engine/restart
Restart the AGI engine.

### POST /api/owner/engine/emergency-kill
Emergency kill: stops all trades immediately.

### GET /api/owner/health/system
Get system health (CPU, RAM, network, errors).

Sample response:
```json
{
  "cpu": "12%",
  "ram": "3.2GB/16GB",
  "network": "stable",
  "errors": []
}
```

### GET /api/owner/strategies
List all strategies and their status/performance.

### POST /api/owner/strategies/{strategy_id}/disable
Disable a strategy.

### POST /api/owner/strategies/{strategy_id}/retrain
Retrain a strategy.

### DELETE /api/owner/strategies/{strategy_id}/delete
Delete a strategy.

### GET /api/owner/investors/overview
Get AUM, inflows, top investors, and performance.

Sample response:
```json
{
  "aum": 1200000.0,
  "inflows": 50000.0,
  "top_investors": [
    {"id": "user1", "name": "Alice", "aum": 300000.0},
    {"id": "user2", "name": "Bob", "aum": 250000.0}
  ],
  "performance": 0.18
}
```

### POST /api/owner/manual-signal
Submit a manual trade signal.

### GET /api/owner/wallet/overview
Get total platform balance, Paystack funds, and pending withdrawals.

### GET /api/owner/automl/status
Get current Auto-ML status (evolving/validated models).

### GET /api/owner/logs
Fetch recent logs, API calls, and webhook actions.

Sample response:
```json
{
  "logs": [
    {"timestamp": "2024-07-08T12:00:00Z", "event": "Engine started"},
    {"timestamp": "2024-07-08T12:05:00Z", "event": "Strategy retrained"}
  ]
}
```

## Data Models

### User Model
```typescript
interface User {
  id: string;
  email: string;
  role: 'owner' | 'investor';
  created_at: string;
  updated_at: string;
}
```

### Trading Pair Model
```typescript
interface TradingPair {
  id: string;
  symbol: string;
  base_currency: string;
  quote_currency: string;
  is_active: boolean;
  min_trade_amount: number;
  max_trade_amount: number;
  created_at: string;
}
```

### Market Data Model
```typescript
interface MarketData {
  id: string;
  pair_id: string;
  timestamp: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
  market_condition: 'trending_up' | 'trending_down' | 'ranging' | 'volatile';
  volatility?: number;
  rsi?: number;
  macd?: number;
  bollinger_upper?: number;
  bollinger_lower?: number;
  support_level?: number;
  resistance_level?: number;
}
```

### AI Signal Model
```typescript
interface AISignal {
  id: string;
  pair_id: string;
  signal: 'buy' | 'sell' | 'hold';
  confidence: number;
  strategy_used: 'breakout' | 'mean_reversion' | 'momentum' | 'scalping' | 'grid';
  entry_price?: number;
  stop_loss?: number;
  take_profit?: number;
  reasoning?: string;
  executed: boolean;
  created_at: string;
}
```

### Trade Model
```typescript
interface Trade {
  id: string;
  signal_id?: string;
  pair_id: string;
  trade_type: 'buy' | 'sell';
  amount: number;
  entry_price: number;
  exit_price?: number;
  stop_loss?: number;
  take_profit?: number;
  status: 'pending' | 'executed' | 'cancelled' | 'failed';
  profit_loss: number;
  execution_time?: string;
  created_at: string;
  closed_at?: string;
}
```

### Portfolio Model
```typescript
interface Portfolio {
  id: string;
  user_id: string;
  total_balance: number;
  available_balance: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_trades: number;
  winning_trades: number;
  created_at: string;
  updated_at: string;
}
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `500` - Internal Server Error

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": "Authentication failed"
  }
}
```

### Common Error Codes
- `INVALID_CREDENTIALS` - Authentication failed
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `VALIDATION_ERROR` - Request data validation failed
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INSUFFICIENT_BALANCE` - Not enough funds for trade

## Rate Limits

- **Authentication**: 10 requests per minute
- **Market Data**: 100 requests per minute
- **Trading Operations**: 50 requests per minute
- **Real-time Subscriptions**: 10 concurrent connections

## SDK Usage Examples

### JavaScript/TypeScript Client
```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://your-project.supabase.co',
  'your-anon-key'
);

// Get trading pairs
const { data: pairs, error } = await supabase
  .from('trading_pairs')
  .select('*')
  .eq('is_active', true);

// Create AI signal
const { data, error } = await supabase
  .from('ai_signals')
  .insert({
    pair_id: 'uuid',
    signal: 'buy',
    confidence: 0.85,
    strategy_used: 'breakout'
  });

// Real-time subscription
const subscription = supabase
  .channel('signals')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'ai_signals' },
    (payload) => handleNewSignal(payload.new)
  )
  .subscribe();
```

This API reference provides comprehensive documentation for integrating with the Waves Quant Engine backend services.


# System Architecture - Waves Quant Engine

## Overview
The Waves Quant Engine is built as a modern, scalable trading system that combines real-time data processing, AI-driven decision making, and secure multi-user access. This document details the complete system architecture.

## Architecture Layers

### 1. Presentation Layer (Frontend)
```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                           │
├─────────────────────┬───────────────────┬───────────────────┤
│   Owner Dashboard   │  Investor Dash    │  Authentication   │
│                     │                   │                   │
│ • Strategy Config   │ • Portfolio View  │ • Login/Signup    │
│ • Risk Management   │ • Trade History   │ • Role Management │
│ • Full Analytics    │ • Performance     │ • Session Mgmt    │
│ • System Control    │ • Live Charts     │                   │
└─────────────────────┴───────────────────┴───────────────────┘
```

**Components:**
- **React 18** with TypeScript for type safety
- **Vite** for fast development and building
- **Tailwind CSS** with shadcn/ui for consistent design
- **React Query** for efficient data management
- **Recharts** for advanced data visualization

### 2. Business Logic Layer (AI Engine)
```
┌─────────────────────────────────────────────────────────────┐
│                    AI Strategy Engine                       │
├─────────────────────┬───────────────────┬───────────────────┤
│  Market Analysis    │  Strategy Select  │  Signal Generate  │
│                     │                   │                   │
│ • OHLC Processing   │ • Breakout        │ • Buy/Sell/Hold   │
│ • Technical Indica  │ • Mean Reversion  │ • Confidence      │
│ • Condition Detect  │ • Momentum        │ • Risk Levels     │
│ • Volatility Calc   │ • Scalping        │ • Entry/Exit      │
└─────────────────────┴───────────────────┴───────────────────┘
```

**Strategy Selection Logic:**
```typescript
Market Condition → Strategy Selection
├── Trending Up/Down → Breakout Strategy
├── Ranging/Sideways → Mean Reversion Strategy  
├── High Volatility → Scalping Strategy
└── Default → Momentum Strategy
```

### 3. Data Layer (Supabase Backend)
```
┌─────────────────────────────────────────────────────────────┐
│                    Supabase Backend                         │
├─────────────────────┬───────────────────┬───────────────────┤
│    PostgreSQL       │    Real-time      │   Authentication  │
│                     │                   │                   │
│ • Trading Data      │ • Live Updates    │ • JWT Tokens      │
│ • Market Data       │ • WebSocket       │ • Role-based      │
│ • User Portfolios   │ • Subscriptions   │ • Row Level Sec   │
│ • AI Signals        │ • Push Notifs     │ • Session Mgmt    │
└─────────────────────┴───────────────────┴───────────────────┘
```

## Data Flow Architecture

### 1. Real-Time Trading Flow
```
Market Data → Analysis → Strategy → Signal → Execution → Portfolio Update
     ↓            ↓         ↓        ↓         ↓            ↓
   OHLC+Vol   Tech Indic  AI Logic  Trade    Database    Real-time UI
```

### 2. User Interaction Flow
```
User Action → Authentication → Role Check → Data Access → UI Update
     ↓             ↓             ↓           ↓            ↓
  Dashboard     JWT Verify    RLS Policy   Supabase    Live Update
```

## Database Architecture

### Entity Relationship Diagram
```
users (1) ←→ (M) portfolios
  ↓
  └→ (1) risk_settings

trading_pairs (1) ←→ (M) market_data
      ↓
      ├→ (M) ai_signals
      ├→ (M) trades  
      └→ (1) pair_strategies

ai_signals (1) ←→ (M) trades

performance_analytics (standalone)
```

### Table Relationships & Constraints

#### Core Business Tables
1. **users**: Central user management with role-based access
2. **trading_pairs**: Cryptocurrency pairs configuration
3. **market_data**: Real-time OHLC and technical indicators
4. **ai_signals**: AI-generated trading signals
5. **trades**: Executed trades with P&L tracking
6. **portfolios**: User portfolio balances and statistics

#### Configuration Tables
1. **pair_strategies**: AI strategy configuration per pair
2. **risk_settings**: User-specific risk management rules
3. **performance_analytics**: Daily aggregated performance metrics

### Security Architecture

#### Row Level Security (RLS) Policies
```sql
-- Users can only access their own data
CREATE POLICY "users_own_data" ON users 
  FOR ALL USING (auth.uid() = id);

-- Public read access to trading pairs
CREATE POLICY "public_trading_pairs" ON trading_pairs 
  FOR SELECT TO authenticated USING (true);

-- Investors can only see their portfolio
CREATE POLICY "portfolio_access" ON portfolios 
  FOR ALL USING (user_id = auth.uid());

-- Only owners can manage system settings
CREATE POLICY "owner_only_management" ON trading_pairs 
  FOR ALL USING (
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'owner')
  );
```

## Component Architecture

### Frontend Component Hierarchy
```
App
├── AuthProvider (Context)
├── ThemeProvider (Context)
├── Router
    ├── AuthPage
    ├── OwnerDashboard
    │   ├── TradingChart
    │   ├── LiveSignals
    │   ├── TradeHistory
    │   ├── PairStrategies
    │   ├── RiskManagement
    │   └── PerformanceAnalytics
    └── InvestorDashboard
        ├── TradingChart
        ├── Portfolio Overview
        └── Trade History
```

### State Management Strategy
```typescript
// Global State (React Context)
- Authentication State
- Theme Preferences
- User Role & Permissions

// Server State (React Query)
- Trading Data
- Market Data
- Portfolio Information
- Trade History

// Component State (useState/useReducer)
- UI State (modals, forms)
- Local Preferences
- Temporary Data
```

## AI Strategy Architecture

### Strategy Pattern Implementation
```typescript
interface TradingStrategy {
  analyze(marketData: MarketData): Signal;
  calculateRisk(signal: Signal): RiskLevels;
  validateEntry(signal: Signal): boolean;
}

class BreakoutStrategy implements TradingStrategy {
  analyze(data: MarketData): Signal {
    // Breakout logic for trending markets
  }
}

class MeanReversionStrategy implements TradingStrategy {
  analyze(data: MarketData): Signal {
    // Mean reversion logic for ranging markets
  }
}
```

### Decision Engine Flow
```
1. Market Data Input
   ├── OHLC Prices
   ├── Volume Data
   ├── Technical Indicators (RSI, MACD, Bollinger Bands)
   └── Support/Resistance Levels

2. Market Condition Analysis
   ├── Trend Detection
   ├── Volatility Calculation
   ├── Range Identification
   └── Momentum Assessment

3. Strategy Selection
   ├── Condition → Strategy Mapping
   ├── Historical Performance
   ├── Current Market State
   └── Risk Assessment

4. Signal Generation
   ├── Entry Point Calculation
   ├── Stop Loss Determination
   ├── Take Profit Targets
   └── Confidence Scoring

5. Risk Validation
   ├── Position Size Check
   ├── Portfolio Exposure
   ├── Daily Loss Limits
   └── Correlation Analysis

6. Execution Decision
   ├── Signal Strength Threshold
   ├── Market Conditions
   ├── Risk Compliance
   └── Portfolio Balance
```

## Performance Architecture

### Frontend Performance
- **Code Splitting**: Lazy loading of dashboard components
- **Memoization**: React.memo for expensive components
- **Virtual Scrolling**: For large trade history lists
- **Debounced Updates**: Smooth real-time chart updates
- **Optimistic Updates**: Instant UI feedback

### Backend Performance
- **Database Indexing**: Optimized queries for trading data
- **Connection Pooling**: Efficient database connections
- **Real-time Subscriptions**: WebSocket connections for live data
- **Caching Strategy**: Supabase built-in caching
- **Query Optimization**: Selective field fetching

### Trading Performance
- **Sub-second Execution**: Optimized signal processing
- **Parallel Processing**: Concurrent pair analysis
- **Memory Efficiency**: Streaming data processing
- **Event-driven Updates**: Real-time portfolio updates

## Scalability Architecture

### Horizontal Scaling
- **Supabase Auto-scaling**: Database scales with load
- **CDN Distribution**: Static assets via CDN
- **Load Balancing**: Built-in Supabase load balancing
- **Geographic Distribution**: Multi-region deployment

### Vertical Scaling
- **Database Performance**: Optimized indexes and queries
- **Connection Pooling**: Efficient resource utilization
- **Memory Management**: Optimized data structures
- **CPU Optimization**: Efficient algorithms

## Security Architecture

### Authentication & Authorization
```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────┬───────────────────┬───────────────────┤
│   Application       │   Database        │   Network         │
│                     │                   │                   │
│ • Role-based Access │ • Row Level Sec   │ • HTTPS/TLS       │
│ • JWT Validation    │ • Encrypted Data  │ • CORS Policy     │
│ • Session Mgmt      │ • Audit Logging   │ • Rate Limiting   │
│ • Input Validation  │ • Backup/Recovery │ • DDoS Protection │
└─────────────────────┴───────────────────┴───────────────────┘
```

### Data Security
- **Encryption at Rest**: All sensitive data encrypted
- **Encryption in Transit**: HTTPS/TLS for all communications
- **Access Control**: Granular permissions per user role
- **Audit Trail**: Complete logging of all trading activities

## Monitoring & Observability

### System Monitoring
- **Performance Metrics**: Response times, throughput
- **Error Tracking**: Real-time error monitoring
- **User Analytics**: Dashboard usage patterns
- **Trading Analytics**: Signal performance, execution stats

### Health Checks
- **Database Health**: Connection status, query performance
- **Authentication Status**: Auth service availability
- **Real-time Connections**: WebSocket health
- **Trading Engine**: Signal generation status

This architecture ensures the Waves Quant Engine is robust, scalable, and secure while maintaining the flexibility to adapt to changing market conditions and user requirements.


# Waves Quant Engine - Complete Documentation

Welcome to the comprehensive documentation for the Waves Quant Engine, a sophisticated High-Frequency Trading (HFT) system powered by AI that automatically trades cryptocurrency with unique strategies per trading pair.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Database Design](#database-design)
6. [AI Strategy Engine](#ai-strategy-engine)
7. [User Roles & Dashboards](#user-roles--dashboards)
8. [Setup & Installation](#setup--installation)
9. [API Reference](#api-reference)
10. [Security](#security)

## Overview

The Waves Quant Engine is a full-stack cryptocurrency trading application that combines artificial intelligence with high-frequency trading principles. It automatically analyzes market conditions and executes trades in real-time, with each trading pair receiving a unique strategy tailored to its market behavior.

### Key Characteristics

- **AI-Driven**: Each trading pair has its own AI strategy (breakout, mean reversion, momentum, scalping, grid)
- **Real-Time**: Sub-second execution with live market data processing
- **Dual Interface**: Separate dashboards for owners and investors
- **Risk-Managed**: Comprehensive risk controls and position management
- **Scalable**: Built for production use with proper authentication and security

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Supabase      │    │   AI Engine     │
│   (React/Vite)  │◄──►│   (Database)    │◄──►│   (Strategies)  │
│                 │    │                 │    │                 │
│ - Owner Dash    │    │ - Auth          │    │ - Market Anal.  │
│ - Investor Dash │    │ - Real-time     │    │ - Signal Gen.   │
│ - Trading UI    │    │ - RLS Policies  │    │ - Risk Mgmt     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Structure

```
src/
├── components/
│   ├── trading/           # Trading-specific components
│   │   ├── TradingChart.tsx
│   │   ├── LiveSignals.tsx
│   │   ├── TradeHistory.tsx
│   │   ├── PairStrategies.tsx
│   │   ├── RiskManagement.tsx
│   │   └── PerformanceAnalytics.tsx
│   ├── theme/             # Theme management
│   └── ui/                # Reusable UI components
├── contexts/
│   └── AuthContext.tsx    # Authentication state
├── pages/
│   ├── OwnerDashboard.tsx
│   ├── InvestorDashboard.tsx
│   └── AuthPage.tsx
└── integrations/
    └── supabase/          # Database integration
```

## Features

### 🤖 AI Strategy Engine

- **Unique Strategies Per Pair**: Each cryptocurrency pair gets its own AI strategy
- **Market Condition Detection**: Automatically identifies trending, ranging, and volatile markets
- **Strategy Adaptation**: 
  - **Trending Markets**: Breakout strategy
  - **Ranging Markets**: Mean reversion strategy
  - **Volatile Markets**: Scalping strategy
  - **Momentum Markets**: Momentum following strategy

### 📊 Real-Time Trading

- **Live Market Data**: Real-time price feeds with technical indicators
- **Instant Execution**: Sub-second trade execution
- **Risk Controls**: Automated stop-loss and take-profit orders
- **Position Management**: Maximum position limits and exposure controls

### 👥 Dual Dashboard System

#### Owner Dashboard
- Complete system oversight
- AI strategy configuration
- Risk management controls
- Performance analytics
- Trade execution management

#### Investor Dashboard
- Portfolio overview
- Trade history
- Performance metrics
- Real-time charts

### 🛡️ Risk Management

- **Position Sizing**: Automatic position size calculation
- **Stop Loss**: Configurable stop-loss percentages
- **Daily Limits**: Maximum daily loss protection
- **Exposure Limits**: Maximum open positions
- **Risk per Trade**: Percentage-based risk allocation

## Technology Stack

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality component library
- **Recharts**: Data visualization for charts
- **React Query**: Data fetching and caching

### Backend & Database
- **Supabase**: Backend-as-a-Service
- **PostgreSQL**: Relational database
- **Row Level Security**: Fine-grained access control
- **Real-time subscriptions**: Live data updates
- **Edge Functions**: Serverless functions

### Authentication & Security
- **Supabase Auth**: Secure authentication
- **Row Level Security**: Database-level security
- **Role-based Access**: Owner/Investor role system
- **JWT Tokens**: Secure API access

## Database Design

### Core Tables

#### Users Table
```sql
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    role user_role NOT NULL DEFAULT 'investor',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Trading Pairs Table
```sql
CREATE TABLE public.trading_pairs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol TEXT UNIQUE NOT NULL,
    base_currency TEXT NOT NULL,
    quote_currency TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true
);
```

#### Market Data Table
```sql
CREATE TABLE public.market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pair_id UUID REFERENCES trading_pairs(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    open_price DECIMAL(20,8) NOT NULL,
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    close_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    market_condition market_condition,
    rsi DECIMAL(5,2),
    macd DECIMAL(10,6),
    bollinger_upper DECIMAL(20,8),
    bollinger_lower DECIMAL(20,8)
);
```

#### AI Signals Table
```sql
CREATE TABLE public.ai_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pair_id UUID REFERENCES trading_pairs(id),
    signal signal_type NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    strategy_used strategy_type NOT NULL,
    entry_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    take_profit DECIMAL(20,8),
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Security Policies

All tables implement Row Level Security (RLS):

- **Users**: Can only view/update their own data
- **Portfolios**: Users can only access their own portfolio
- **Trading Pairs**: Public read, owner-only write
- **Market Data**: Public read, system-only write
- **Trades**: Public read (authenticated users)

## AI Strategy Engine

### Strategy Selection Logic

```typescript
const selectStrategy = (marketCondition: string) => {
  switch (marketCondition) {
    case 'trending_up':
    case 'trending_down':
      return 'breakout';
    case 'ranging':
      return 'mean_reversion';
    case 'volatile':
      return 'scalping';
    default:
      return 'momentum';
  }
};
```

### Strategy Implementations

#### 1. Breakout Strategy
- **Use Case**: Trending markets
- **Logic**: Trade in direction of breakouts from key levels
- **Risk**: Tight stops below/above breakout levels
- **Targets**: Extended moves in trend direction

#### 2. Mean Reversion Strategy
- **Use Case**: Ranging/sideways markets
- **Logic**: Buy at support, sell at resistance
- **Risk**: Stop outside of range
- **Targets**: Opposite side of range

#### 3. Momentum Strategy
- **Use Case**: Strong directional moves
- **Logic**: Follow momentum with technical confirmations
- **Risk**: Momentum-based stops
- **Targets**: Momentum exhaustion levels

#### 4. Scalping Strategy
- **Use Case**: High volatility environments
- **Logic**: Quick in-and-out trades on small moves
- **Risk**: Very tight stops
- **Targets**: Small, frequent profits

### Signal Generation Process

1. **Market Analysis**: Analyze OHLC data, volume, technical indicators
2. **Condition Detection**: Identify market condition (trending, ranging, volatile)
3. **Strategy Selection**: Choose appropriate strategy for detected condition
4. **Signal Generation**: Generate buy/sell/hold signal with confidence score
5. **Risk Calculation**: Calculate entry, stop-loss, and take-profit levels
6. **Execution**: Execute trade if confidence threshold is met

## User Roles & Dashboards

### Owner Role
**Capabilities:**
- Full system access and control
- AI strategy configuration per pair
- Risk management parameter setting
- Complete trade and performance analytics
- System-wide oversight

**Dashboard Sections:**
- Live trading charts with all pairs
- AI signal management and generation
- Complete trade history with filtering
- Strategy configuration per trading pair
- Risk management controls
- Comprehensive performance analytics

### Investor Role
**Capabilities:**
- Portfolio view and tracking
- Trade history for their account
- Performance metrics
- Live chart viewing

**Dashboard Sections:**
- Portfolio overview (balance, P&L, win rate)
- Personal trade history
- Live trading charts
- Performance summaries

## Setup & Installation

### Prerequisites
- Node.js 18+ installed
- Supabase account and project
- Git for version control

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd waves-quant-engine
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure Supabase**
   - Update `src/integrations/supabase/client.ts` with your Supabase URL and key
   - Run the provided SQL migrations in your Supabase SQL editor

4. **Start development server**
```bash
npm run dev
```

### Environment Configuration

The app uses Supabase configuration in `supabase/config.toml`:
```toml
project_id = "your-project-id"
```

### Database Setup

Execute the migration SQL provided in the setup to create:
- All required tables with proper relationships
- Row Level Security policies
- Default trading pairs
- Indexes for performance
- Real-time subscriptions

## API Reference

### Authentication Endpoints

The app uses Supabase Auth for authentication:

- **Sign Up**: `POST /auth/v1/signup`
- **Sign In**: `POST /auth/v1/token?grant_type=password`
- **Sign Out**: `POST /auth/v1/logout`

### Database Operations

All database operations go through Supabase client:

```typescript
// Fetch trading pairs
const { data, error } = await supabase
  .from('trading_pairs')
  .select('*')
  .eq('is_active', true);

// Insert AI signal
const { error } = await supabase
  .from('ai_signals')
  .insert({
    pair_id: 'uuid',
    signal: 'buy',
    confidence: 0.85,
    strategy_used: 'breakout'
  });
```

### Real-time Subscriptions

```typescript
// Subscribe to new signals
const subscription = supabase
  .channel('ai_signals_changes')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'ai_signals' },
    (payload) => {
      // Handle new signal
    }
  )
  .subscribe();
```

## Security

### Authentication Security
- JWT-based authentication via Supabase
- Secure session management
- Email verification for sign-ups
- Password reset functionality

### Database Security
- Row Level Security (RLS) on all tables
- Role-based access control
- Encrypted data at rest
- Secure API endpoints

### Application Security
- TypeScript for type safety
- Input validation and sanitization
- CORS protection
- Environment variable protection

### Trading Security
- Risk management controls
- Position size limits
- Stop-loss automation
- Daily loss limits

## Performance Optimizations

### Frontend Optimizations
- React Query for data caching
- Lazy loading of components
- Optimized re-renders with useMemo/useCallback
- Efficient state management

### Database Optimizations
- Proper indexing on frequently queried columns
- Optimized queries with selective fields
- Real-time subscriptions for live data
- Connection pooling via Supabase

### Trading Optimizations
- Sub-second signal generation
- Efficient market data processing
- Optimized strategy calculations
- Real-time execution monitoring

---

This documentation provides a complete overview of the Waves Quant Engine. For specific implementation details, refer to the individual component files and database schema.

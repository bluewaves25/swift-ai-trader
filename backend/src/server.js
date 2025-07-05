import express from 'express';
import { PythonShell } from 'python-shell';
import ccxt from 'ccxt';
import dotenv from 'dotenv';
import axios from 'axios';
import cors from 'cors';

dotenv.config();

const app = express();
app.use(express.json());

// Enable CORS for frontend
app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:3000'],
  credentials: true
}));

// Asset class configuration
const assetClasses = {
  forex: {
    symbols: ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD', 'EURGBP'],
    multiplier: 1
  },
  crypto: {
    symbols: ['BTCUSD', 'ETHUSD', 'ADAUSD', 'XRPUSD', 'DOTUSD', 'LINKUSD', 'BNBUSD', 'SOLUSD'],
    multiplier: 1
  },
  stocks: {
    symbols: ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'],
    multiplier: 1
  },
  commodities: {
    symbols: ['XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'NATGAS', 'COPPER', 'WHEAT', 'CORN'],
    multiplier: 1
  },
  indices: {
    symbols: ['SPX500', 'NAS100', 'DOW30', 'UK100', 'GER40', 'FRA40', 'JPN225', 'AUS200'],
    multiplier: 1
  }
};

// Enhanced broker configuration
const brokers = {
  exness: {
    async getBalance(accountNumber, password, server) {
      let options = {
        mode: 'text',
        pythonOptions: ['-u'],
        scriptPath: './scripts',
        args: [accountNumber, password, server],
      };
      try {
        const { results } = await PythonShell.run('exness_balance.py', options);
        return JSON.parse(results[0]);
      } catch (error) {
        console.error('Exness balance error:', error);
        return { balance: 0, error: error.message };
      }
    },
    async executeTrade(accountNumber, password, server, trade) {
      let options = {
        mode: 'text',
        pythonOptions: ['-u'],
        scriptPath: './scripts',
        args: [accountNumber, password, server, JSON.stringify(trade)],
      };
      try {
        const { results } = await PythonShell.run('exness_trade.py', options);
        return JSON.parse(results[0]);
      } catch (error) {
        console.error('Exness trade error:', error);
        return { status: 'error', message: error.message };
      }
    },
    async getMarketData(symbol) {
      let options = {
        mode: 'text',
        pythonOptions: ['-u'],
        scriptPath: './scripts',
        args: [symbol],
      };
      try {
        const { results } = await PythonShell.run('exness_market_data.py', options);
        return JSON.parse(results[0]);
      } catch (error) {
        console.error('Exness market data error:', error);
        return { error: error.message };
      }
    },
    async deposit(accountNumber, password, server, amount) {
      return { status: 'pending', message: `Deposit of ${amount} requested for Exness account ${accountNumber}` };
    },
    async withdraw(accountNumber, password, server, amount) {
      return { status: 'pending', message: `Withdrawal of ${amount} requested for Exness account ${accountNumber}` };
    },
  },
  binance: {
    client: new ccxt.binance({
      apiKey: process.env.BINANCE_API_KEY,
      secret: process.env.BINANCE_SECRET,
      enableRateLimit: true,
    }),
    async getBalance() {
      try {
        const balance = await this.client.fetchBalance();
        return balance.total;
      } catch (error) {
        console.error('Binance balance error:', error);
        return { error: error.message };
      }
    },
    async executeTrade(trade) {
      try {
        const { symbol, type, side, amount, price } = trade;
        return await this.client.createOrder(symbol, type, side, amount, price);
      } catch (error) {
        console.error('Binance trade error:', error);
        return { status: 'error', message: error.message };
      }
    },
    async getMarketData(symbol) {
      try {
        const ticker = await this.client.fetchTicker(symbol);
        return {
          symbol,
          price: ticker.last,
          high: ticker.high,
          low: ticker.low,
          volume: ticker.baseVolume,
          change: ticker.change,
          timestamp: ticker.timestamp
        };
      } catch (error) {
        console.error('Binance market data error:', error);
        return { error: error.message };
      }
    },
    async deposit(currency, amount) {
      try {
        return await this.client.deposit(currency, amount);
      } catch (error) {
        console.error('Binance deposit error:', error);
        return { status: 'error', message: error.message };
      }
    },
    async withdraw(currency, amount, address) {
      try {
        return await this.client.withdraw(currency, amount, address);
      } catch (error) {
        console.error('Binance withdraw error:', error);
        return { status: 'error', message: error.message };
      }
    },
  },
};

// Trading engine state
let tradingEngineState = {
  isRunning: false,
  lastUpdate: null,
  activeStrategies: [],
  totalTrades: 0,
  profitLoss: 0
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    engine: tradingEngineState
  });
});

// Market data endpoints
app.get('/market-data/:symbol', async (req, res) => {
  const { symbol } = req.params;
  try {
    // Try to get data from Exness first
    const data = await brokers.exness.getMarketData(symbol);
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/historical-data/:symbol/:timeframe', async (req, res) => {
  const { symbol, timeframe } = req.params;
  const { limit = 100 } = req.query;
  
  try {
    // Mock historical data for now
    const data = [];
    const now = new Date();
    
    for (let i = limit; i > 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60000); // 1 minute intervals
      const basePrice = 1.1000 + Math.random() * 0.01;
      
      data.push({
        timestamp,
        open: basePrice,
        high: basePrice * (1 + Math.random() * 0.001),
        low: basePrice * (1 - Math.random() * 0.001),
        close: basePrice * (1 + (Math.random() - 0.5) * 0.001),
        volume: Math.random() * 1000000
      });
    }
    
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Balance endpoint
app.get('/balance/:broker/:account', async (req, res) => {
  const { broker, account } = req.params;
  try {
    if (broker === 'exness') {
      const { password, server } = req.query;
      const balance = await brokers.exness.getBalance(account, password || process.env.EXNESS_PASSWORD, server || process.env.EXNESS_SERVER);
      res.json(balance);
    } else if (broker === 'binance') {
      const balance = await brokers.binance.getBalance();
      res.json(balance);
    } else {
      res.status(400).json({ error: 'Unsupported broker' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Trade execution endpoint
app.post('/trade/:broker/:account', async (req, res) => {
  const { broker, account } = req.params;
  const trade = req.body;
  try {
    if (broker === 'exness') {
      const { password, server } = req.query;
      const result = await brokers.exness.executeTrade(account, password || process.env.EXNESS_PASSWORD, server || process.env.EXNESS_SERVER, trade);
      res.json(result);
    } else if (broker === 'binance') {
      const result = await brokers.binance.executeTrade(trade);
      res.json(result);
    } else {
      res.status(400).json({ error: 'Unsupported broker' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Deposit endpoint
app.post('/deposit/:broker/:account', async (req, res) => {
  const { broker, account } = req.params;
  const { amount, currency } = req.body;
  try {
    if (broker === 'exness') {
      const { password, server } = req.query;
      const result = await brokers.exness.deposit(account, password || process.env.EXNESS_PASSWORD, server || process.env.EXNESS_SERVER, amount);
      res.json(result);
    } else if (broker === 'binance') {
      const result = await brokers.binance.deposit(currency, amount);
      res.json(result);
    } else {
      res.status(400).json({ error: 'Unsupported broker' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Withdrawal endpoint
app.post('/withdraw/:broker/:account', async (req, res) => {
  const { broker, account } = req.params;
  const { amount, currency, address } = req.body;
  try {
    if (broker === 'exness') {
      const { password, server } = req.query;
      const result = await brokers.exness.withdraw(account, password || process.env.EXNESS_PASSWORD, server || process.env.EXNESS_SERVER, amount);
      res.json(result);
    } else if (broker === 'binance') {
      const result = await brokers.binance.withdraw(currency, amount, address);
      res.json(result);
    } else {
      res.status(400).json({ error: 'Unsupported broker' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// AI Signals endpoint
app.get('/ai-signals', async (req, res) => {
  const { symbol } = req.query;
  try {
    // Mock AI signals
    const signals = [];
    const symbols = symbol ? [symbol] : ['EURUSD', 'BTCUSD', 'XAUUSD', 'SPX500'];
    
    for (const s of symbols) {
      const signal = {
        symbol: s,
        signal: ['buy', 'sell', 'hold'][Math.floor(Math.random() * 3)],
        confidence: 0.7 + Math.random() * 0.25,
        strategy: ['breakout', 'mean_reversion', 'momentum', 'scalping'][Math.floor(Math.random() * 4)],
        timestamp: new Date().toISOString(),
        entry_price: 1.1000 + Math.random() * 0.01,
        stop_loss: 1.0950 + Math.random() * 0.01,
        take_profit: 1.1050 + Math.random() * 0.01
      };
      signals.push(signal);
    }
    
    res.json(signals);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Sentiment analysis endpoint
app.get('/sentiment/:symbol', async (req, res) => {
  const { symbol } = req.params;
  try {
    if (process.env.OPENROUTER_API_KEY) {
      const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: 'mistralai/mixtral-8x7b-instruct',
          messages: [{ role: 'user', content: `Analyze sentiment for ${symbol} based on recent financial news. Provide a brief analysis.` }],
          max_tokens: 100,
        },
        {
          headers: {
            Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json',
          },
        }
      );
      res.json({ sentiment: response.data.choices[0].message.content.trim() });
    } else {
      // Mock sentiment
      const sentiments = ['bullish', 'bearish', 'neutral'];
      const sentiment = sentiments[Math.floor(Math.random() * sentiments.length)];
      res.json({ 
        sentiment: `${sentiment.charAt(0).toUpperCase() + sentiment.slice(1)} sentiment detected for ${symbol}. Market shows ${sentiment} indicators.`
      });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Trading engine control endpoints
app.post('/engine/start', (req, res) => {
  tradingEngineState.isRunning = true;
  tradingEngineState.lastUpdate = new Date().toISOString();
  res.json({ status: 'started', message: 'Trading engine started successfully' });
});

app.post('/engine/stop', (req, res) => {
  tradingEngineState.isRunning = false;
  tradingEngineState.lastUpdate = new Date().toISOString();
  res.json({ status: 'stopped', message: 'Trading engine stopped successfully' });
});

app.post('/engine/emergency-stop', (req, res) => {
  tradingEngineState.isRunning = false;
  tradingEngineState.lastUpdate = new Date().toISOString();
  res.json({ status: 'emergency_stopped', message: 'Emergency stop activated - all trading halted' });
});

app.post('/engine/close-all', async (req, res) => {
  try {
    // Mock closing all positions
    const result = {
      closed_positions: 5,
      total_pnl: Math.random() * 1000 - 500,
      message: 'All positions closed successfully'
    };
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Portfolio stats endpoint
app.get('/portfolio/:userId', async (req, res) => {
  const { userId } = req.params;
  try {
    // Mock portfolio stats
    const stats = {
      totalBalance: 10000 + Math.random() * 5000,
      availableBalance: 5000 + Math.random() * 2000,
      unrealizedPnL: Math.random() * 1000 - 500,
      realizedPnL: Math.random() * 2000 - 1000,
      totalTrades: Math.floor(Math.random() * 100),
      winningTrades: Math.floor(Math.random() * 60),
      openPositions: Math.floor(Math.random() * 10),
      dailyPnL: Math.random() * 200 - 100
    };
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Risk settings endpoint
app.put('/risk-settings/:userId', (req, res) => {
  const { userId } = req.params;
  const settings = req.body;
  
  // Mock saving risk settings
  res.json({ 
    status: 'success', 
    message: 'Risk settings updated successfully',
    settings 
  });
});

// Strategy management endpoints
app.get('/strategies', (req, res) => {
  const strategies = [
    {
      id: 'breakout',
      name: 'Breakout Strategy',
      description: 'Trades breakouts from key levels',
      active: true,
      performance: { winRate: 0.65, totalTrades: 156, profit: 2450.50 }
    },
    {
      id: 'mean_reversion',
      name: 'Mean Reversion',
      description: 'Trades mean reversion in ranging markets',
      active: true,
      performance: { winRate: 0.58, totalTrades: 89, profit: 1200.25 }
    },
    {
      id: 'momentum',
      name: 'Momentum Strategy',
      description: 'Follows strong momentum moves',
      active: false,
      performance: { winRate: 0.62, totalTrades: 45, profit: 800.75 }
    }
  ];
  
  res.json(strategies);
});

app.put('/strategies/:strategyId', (req, res) => {
  const { strategyId } = req.params;
  const params = req.body;
  
  res.json({ 
    status: 'success', 
    message: `Strategy ${strategyId} updated successfully`,
    params 
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Waves Quant Engine Backend running on port ${PORT}`);
  console.log(`📊 Multi-Asset Trading API Ready`);
  console.log(`🔗 Frontend connection: http://localhost:5173`);
  console.log(`❤️  Health check: http://localhost:${PORT}/health`);
});

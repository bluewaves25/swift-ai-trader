import express from 'express';
import { PythonShell } from 'python-shell';
import ccxt from 'ccxt';
import dotenv from 'dotenv';
import axios from 'axios';

dotenv.config();

const app = express();
app.use(express.json());

const brokers = {
  exness: {
    async getBalance(accountNumber, password, server) {
      let options = {
        mode: 'text',
        pythonOptions: ['-u'],
        scriptPath: './scripts',
        args: [accountNumber, password, server],
      };
      const { results } = await PythonShell.run('exness_balance.py', options);
      return JSON.parse(results[0]);
    },
    async executeTrade(accountNumber, password, server, trade) {
      let options = {
        mode: 'text',
        pythonOptions: ['-u'],
        scriptPath: './scripts',
        args: [accountNumber, password, server, JSON.stringify(trade)],
      };
      const { results } = await PythonShell.run('exness_trade.py', options);
      return JSON.parse(results[0]);
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
      const balance = await this.client.fetchBalance();
      return balance.total;
    },
    async executeTrade(trade) {
      const { symbol, type, side, amount, price } = trade;
      return await this.client.createOrder(symbol, type, side, amount, price);
    },
    async deposit(currency, amount) {
      return await this.client.deposit(currency, amount);
    },
    async withdraw(currency, amount, address) {
      return await this.client.withdraw(currency, amount, address);
    },
  },
};

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

app.get('/sentiment/:symbol', async (req, res) => {
  const { symbol } = req.params;
  try {
    const response = await axios.post(
      'https://openrouter.ai/api/v1/chat/completions',
      {
        model: 'mistralai/mixtral-8x7b-instruct',
        messages: [{ role: 'user', content: `Analyze sentiment for ${symbol} based on recent financial news.` }],
        max_tokens: 50,
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
          'Content-Type': 'application/json',
        },
      }
    );
    res.json({ sentiment: response.data.choices[0].message.content.trim() });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));
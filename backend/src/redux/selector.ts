import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Wallet {
  broker: string;
  accountNumber: string;
  balance: number;
  currency: string;
}

interface Trade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  volume: number;
  price: number;
  stopLoss?: number;
  takeProfit?: number;
  timestamp: string;
}

interface Strategy {
  symbol: string;
  strategyName: 'breakout' | 'scalping' | 'mean_reversion';
  performance: number;
}

interface TradingState {
  selectedBroker: string;
  wallets: Wallet[];
  activeTrades: Trade[];
  strategies: Strategy[];
  riskParams: {
    stopLoss: number;
    takeProfit: number;
    positionSize: number;
  };
}

const initialState: TradingState = {
  selectedBroker: 'exness',
  wallets: [],
  activeTrades: [],
  strategies: [],
  riskParams: { stopLoss: 0.5, takeProfit: 1.0, positionSize: 1.0 },
};

const tradingSlice = createSlice({
  name: 'trading',
  initialState,
  reducers: {
    setBroker(state, action: PayloadAction<string>) {
      state.selectedBroker = action.payload;
    },
    addWallet(state, action: PayloadAction<Wallet>) {
      state.wallets.push(action.payload);
    },
    updateBalance(state, action: PayloadAction<{ broker: string; accountNumber: string; balance: number }>) {
      const wallet = state.wallets.find(
        (w) => w.broker === action.payload.broker && w.accountNumber === action.payload.accountNumber
      );
      if (wallet) {
        wallet.balance = action.payload.balance;
      }
    },
    addTrade(state, action: PayloadAction<Trade>) {
      state.activeTrades.push(action.payload);
    },
    setStrategy(state, action: PayloadAction<Strategy>) {
      const index = state.strategies.findIndex((s) => s.symbol === action.payload.symbol);
      if (index >= 0) {
        state.strategies[index] = action.payload;
      } else {
        state.strategies.push(action.payload);
      }
    },
    updateRiskParams(state, action: PayloadAction<{ stopLoss: number; takeProfit: number; positionSize: number }>) {
      state.riskParams = action.payload;
    },
  },
});

export const { setBroker, addWallet, updateBalance, addTrade, setStrategy, updateRiskParams } = tradingSlice.actions;
export default tradingSlice.reducer;
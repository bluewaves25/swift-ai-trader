
import { configureStore } from '@reduxjs/toolkit';
import tradingReducer from './tradingSlice';

export const store = configureStore({
  reducer: {
    trading: tradingReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

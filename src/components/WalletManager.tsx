import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { setBroker, addWallet, updateBalance, addTrade } from '../../backend/src/redux/selector';
import axios from 'axios';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

const WalletManager: React.FC = () => {
  const dispatch = useAppDispatch();
  const { selectedBroker, wallets, activeTrades } = useAppSelector((state) => state.trading);
  const [accountNumber, setAccountNumber] = useState('');
  const [password, setPassword] = useState('');
  const [server, setServer] = useState('Exness-MT5Real');
  const [trade, setTrade] = useState({ symbol: 'EURUSD', side: 'buy', volume: 0.1, price: 0 });

  useEffect(() => {
    const fetchWallets = async () => {
      const { data, error } = await supabase.from('wallets').select('*');
      if (error) console.error('Supabase error:', error);
      else data.forEach((wallet: any) => dispatch(addWallet(wallet)));
    };
    fetchWallets();
  }, [dispatch]);

  const handleAddWallet = async () => {
    const newWallet = { broker: selectedBroker, accountNumber, balance: 0, currency: 'USD' };
    const { error } = await supabase.from('wallets').insert([newWallet]);
    if (!error) {
      dispatch(addWallet(newWallet));
      setAccountNumber('');
      setPassword('');
    } else {
      console.error('Supabase insert error:', error);
    }
  };

  const handleFetchBalance = async (broker: string, account: string) => {
    try {
      const response = await axios.get<{ balance: number }>(`http://localhost:3000/balance/${broker}/${account}`, {
        params: { password, server },
      });
      dispatch(updateBalance({ broker, accountNumber: account, balance: response.data.balance }));
      await supabase
        .from('wallets')
        .update({ balance: response.data.balance })
        .eq('broker', broker)
        .eq('accountNumber', account);
    } catch (error) {
      console.error('Balance fetch error:', error);
    }
  };

  const handleTrade = async () => {
    try {
      const response = await axios.post(`http://localhost:3000/trade/${selectedBroker}/${accountNumber}`, trade, {
        params: { password, server },
      });
      dispatch(addTrade({ id: Date.now().toString(), ...trade, side: trade.side as 'buy' | 'sell', timestamp: new Date().toISOString() }));
      await supabase.from('trades').insert([{ ...trade, broker: selectedBroker, accountNumber, timestamp: new Date().toISOString() }]);
    } catch (error) {
      console.error('Trade error:', error);
    }
  };

  return (
    <div>
      <h2>Wallet Manager</h2>
      <select value={selectedBroker} onChange={(e) => dispatch(setBroker(e.target.value))}>
        <option value="exness">Exness</option>
        <option value="binance">Binance</option>
      </select>
      <input
        type="text"
        placeholder="Account Number"
        value={accountNumber}
        onChange={(e) => setAccountNumber(e.target.value)}
      />
      {selectedBroker === 'exness' && (
        <>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            type="text"
            placeholder="Server"
            value={server}
            onChange={(e) => setServer(e.target.value)}
          />
        </>
      )}
      <button onClick={handleAddWallet}>Add Wallet</button>
      <div>
        <h3>Wallets</h3>
        {wallets.map((wallet) => (
          <div key={`${wallet.broker}-${wallet.accountNumber}`}>
            <p>{wallet.broker} - {wallet.accountNumber}: {wallet.balance} {wallet.currency}</p>
            <button onClick={() => handleFetchBalance(wallet.broker, wallet.accountNumber)}>Refresh Balance</button>
          </div>
        ))}
      </div>
      <div>
        <h3>Place Trade</h3>
        <input
          type="text"
          placeholder="Symbol"
          value={trade.symbol}
          onChange={(e) => setTrade({ ...trade, symbol: e.target.value })}
        />
        <select value={trade.side} onChange={(e) => setTrade({ ...trade, side: e.target.value as 'buy' | 'sell' })}>
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
        </select>
        <input
          type="number"
          placeholder="Volume"
          value={trade.volume}
          onChange={(e) => setTrade({ ...trade, volume: parseFloat(e.target.value) })}
        />
        <input
          type="number"
          placeholder="Price"
          value={trade.price}
          onChange={(e) => setTrade({ ...trade, price: parseFloat(e.target.value) })}
        />
        <button onClick={handleTrade}>Execute Trade</button>
      </div>
      <div>
        <h3>Active Trades</h3>
        {activeTrades.map((trade) => (
          <p key={trade.id}>{trade.symbol} - {trade.side} - {trade.volume} @ {trade.price}</p>
        ))}
      </div>
    </div>
  );
};

export default WalletManager;
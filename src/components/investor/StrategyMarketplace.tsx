import { useEffect, useState } from 'react';
import apiService from '@/services/api';
import { Button } from '@/components/ui/button';
import { Star, ShoppingCart, UploadCloud } from 'lucide-react';

export default function StrategyMarketplace({ isPremium }: { isPremium: boolean }) {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [myStrategies, setMyStrategies] = useState<any>({ purchased: [], created: [] });
  const [loading, setLoading] = useState(false);
  const [newStrategy, setNewStrategy] = useState({ name: '', price: '' });
  const [rating, setRating] = useState<{ [id: string]: number }>({});
  const [userId] = useState('me');

  useEffect(() => {
    fetchMarketplace();
    fetchMyStrategies();
  }, []);

  const fetchMarketplace = async () => {
    setLoading(true);
    const res = await apiService.get('/api/v1/marketplace/strategies');
    setStrategies(res.data.strategies);
    setLoading(false);
  };

  const fetchMyStrategies = async () => {
    const res = await apiService.get('/api/v1/marketplace/my', { params: { user_id: userId } });
    setMyStrategies(res.data);
  };

  const handleBuy = async (id: string) => {
    if (!isPremium) return;
    setLoading(true);
    await apiService.post('/api/v1/marketplace/buy', null, { params: { user_id: userId, strategy_id: id } });
    fetchMyStrategies();
    setLoading(false);
  };

  const handleSell = async () => {
    if (!isPremium || !newStrategy.name || !newStrategy.price) return;
    setLoading(true);
    await apiService.post('/api/v1/marketplace/sell', null, { params: { user_id: userId, name: newStrategy.name, price: parseInt(newStrategy.price) } });
    setNewStrategy({ name: '', price: '' });
    fetchMarketplace();
    fetchMyStrategies();
    setLoading(false);
  };

  const handleRate = async (id: string, value: number) => {
    if (!isPremium) return;
    setLoading(true);
    await apiService.post('/api/v1/marketplace/rate', null, { params: { user_id: userId, strategy_id: id, rating: value } });
    setRating(r => ({ ...r, [id]: value }));
    fetchMarketplace();
    setLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-8">
      <h2 className="text-2xl font-bold mb-4">AI Strategy Marketplace</h2>
      {!isPremium && <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">Upgrade to a premium plan to buy, sell, or rate strategies.</div>}
      <div className="mb-8">
        <h3 className="font-semibold mb-2">List a New Strategy</h3>
        <div className="flex gap-2 mb-2">
          <input className="border px-2 py-1 rounded w-1/2" placeholder="Strategy Name" value={newStrategy.name} onChange={e => setNewStrategy(s => ({ ...s, name: e.target.value }))} />
          <input className="border px-2 py-1 rounded w-1/3" placeholder="Price (₦)" type="number" value={newStrategy.price} onChange={e => setNewStrategy(s => ({ ...s, price: e.target.value }))} />
          <Button onClick={handleSell} disabled={!isPremium || !newStrategy.name || !newStrategy.price || loading} className="flex gap-1 items-center"><UploadCloud className="h-4 w-4" /> List</Button>
        </div>
      </div>
      <div className="mb-8">
        <h3 className="font-semibold mb-2">Available Strategies</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {strategies.map(s => (
            <div key={s.id} className="border rounded p-4 bg-white/80 shadow flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <div className="font-bold text-lg">{s.name}</div>
                <div className="text-xs text-muted-foreground">by {s.creator}</div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-yellow-600 font-bold">₦{(s.price / 100).toLocaleString()}</span>
                <span className="text-xs text-muted-foreground">{s.purchased} purchased</span>
              </div>
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 text-yellow-500" />
                <span className="font-semibold">{s.rating?.toFixed(2) || 'N/A'}</span>
                <input type="number" min={1} max={5} className="ml-2 border rounded px-1 w-12" value={rating[s.id] || ''} onChange={e => setRating(r => ({ ...r, [s.id]: parseInt(e.target.value) }))} disabled={!isPremium} />
                <Button size="sm" variant="outline" onClick={() => handleRate(s.id, rating[s.id] || 5)} disabled={!isPremium || !rating[s.id] || loading}>Rate</Button>
              </div>
              <Button onClick={() => handleBuy(s.id)} disabled={!isPremium || myStrategies.purchased.some((p: any) => p.id === s.id) || loading} className="flex gap-1 items-center">
                <ShoppingCart className="h-4 w-4" />
                {myStrategies.purchased.some((p: any) => p.id === s.id) ? 'Purchased' : 'Buy'}
              </Button>
            </div>
          ))}
        </div>
      </div>
      <div className="mb-8">
        <h3 className="font-semibold mb-2">My Strategies</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {myStrategies.purchased.length === 0 && myStrategies.created.length === 0 && <div className="col-span-2 text-muted-foreground">No strategies yet.</div>}
          {myStrategies.purchased.map((s: any) => (
            <div key={s.id} className="border rounded p-4 bg-green-50 shadow">
              <div className="font-bold">{s.name}</div>
              <div className="text-xs text-muted-foreground">Purchased</div>
            </div>
          ))}
          {myStrategies.created.map((s: any) => (
            <div key={s.id} className="border rounded p-4 bg-blue-50 shadow">
              <div className="font-bold">{s.name}</div>
              <div className="text-xs text-muted-foreground">Created</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 
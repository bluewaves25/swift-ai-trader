import { useEffect, useState } from 'react';
import apiService from '@/services/api';
import { Button } from '@/components/ui/button';
import { Copy, Users, DollarSign, Gift } from 'lucide-react';

export default function AffiliateDashboard() {
  const [referral, setReferral] = useState('');
  const [stats, setStats] = useState<any>({ referrals: 0, earnings: 0, pending: 0, history: [] });
  const [userId] = useState('me');
  const [payoutAmount, setPayoutAmount] = useState('');
  const [payoutStatus, setPayoutStatus] = useState<string | null>(null);

  useEffect(() => {
    apiService.get('/api/v1/affiliate/referral', { params: { user_id: userId } }).then(res => setReferral(res.data.referral_code));
    apiService.get('/api/v1/affiliate/stats', { params: { user_id: userId } }).then(res => setStats(res.data));
  }, [userId]);

  const handleCopy = () => {
    navigator.clipboard.writeText(`${window.location.origin}/auth?ref=${referral}`);
  };

  const handlePayout = async () => {
    if (!payoutAmount) return;
    const res = await apiService.post('/api/v1/affiliate/payout', null, { params: { user_id: userId, amount: parseInt(payoutAmount) } });
    setPayoutStatus(res.data.status);
    setPayoutAmount('');
    apiService.get('/api/v1/affiliate/stats', { params: { user_id: userId } }).then(res => setStats(res.data));
  };

  return (
    <div className="max-w-xl mx-auto p-6 space-y-8">
      <h2 className="text-2xl font-bold mb-4">Affiliate Dashboard</h2>
      <div className="p-4 border rounded bg-gray-50 mb-4">
        <div className="flex items-center gap-2 mb-2">
          <Gift className="h-5 w-5 text-yellow-500" />
          <span className="font-semibold">Your Referral Link:</span>
        </div>
        <div className="flex items-center gap-2">
          <input className="border px-2 py-1 rounded w-full" value={`${window.location.origin}/auth?ref=${referral}`} readOnly />
          <Button size="sm" variant="outline" onClick={handleCopy}><Copy className="h-4 w-4" /></Button>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="p-4 border rounded bg-white/80 flex flex-col items-center">
          <Users className="h-6 w-6 text-blue-600 mb-1" />
          <div className="font-bold text-lg">{stats.referrals}</div>
          <div className="text-xs text-muted-foreground">Referrals</div>
        </div>
        <div className="p-4 border rounded bg-white/80 flex flex-col items-center">
          <DollarSign className="h-6 w-6 text-green-600 mb-1" />
          <div className="font-bold text-lg">₦{(stats.earnings / 100).toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">Total Earnings</div>
        </div>
      </div>
      <div className="mb-8">
        <h3 className="font-semibold mb-2">Request Payout</h3>
        <div className="flex gap-2 mb-2">
          <input className="border px-2 py-1 rounded w-1/2" placeholder="Amount (₦)" type="number" value={payoutAmount} onChange={e => setPayoutAmount(e.target.value)} />
          <Button onClick={handlePayout} disabled={!payoutAmount || parseInt(payoutAmount) > stats.pending} className="flex gap-1 items-center">Request</Button>
        </div>
        <div className="text-xs text-muted-foreground">Pending: ₦{(stats.pending / 100).toLocaleString()}</div>
        {payoutStatus && <div className="mt-2 text-green-600">Payout status: {payoutStatus}</div>}
      </div>
      <div className="mb-8">
        <h3 className="font-semibold mb-2">Payout History</h3>
        {stats.history.length === 0 ? <div>No payouts yet.</div> : (
          <ul className="space-y-2">
            {stats.history.map((item: any, idx: number) => (
              <li key={idx} className="border rounded p-2 bg-white shadow">
                <div>Date: {item.date}</div>
                <div>Amount: ₦{(item.amount / 100).toLocaleString()}</div>
                <div>Status: {item.status}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
} 
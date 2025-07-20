import { useEffect, useState } from 'react';
import apiService from '@/services/api';
import { Button } from '@/components/ui/button';

export default function PerformanceFees() {
  const [feeInfo, setFeeInfo] = useState<any>(null);
  const [feeHistory, setFeeHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState('me');
  const [chargeStatus, setChargeStatus] = useState<string | null>(null);

  useEffect(() => {
    apiService.get(`/api/v1/fees/performance`, { params: { user_id: userId } }).then(res => setFeeInfo(res.data));
    apiService.get(`/api/v1/fees/history`, { params: { user_id: userId } }).then(res => setFeeHistory(res.data.history));
  }, [userId]);

  const handleCharge = async () => {
    setLoading(true);
    const res = await apiService.post(`/api/v1/fees/charge`, null, { params: { user_id: userId } });
    setChargeStatus(res.data.status);
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6">
      <h2 className="text-2xl font-bold">Performance Fees</h2>
      <div className="mb-4">
        <label className="block mb-1 font-semibold">User ID</label>
        <input className="border px-2 py-1 rounded w-full" value={userId} onChange={e => setUserId(e.target.value)} placeholder="User ID" />
      </div>
      {feeInfo ? (
        <div className="p-4 border rounded bg-gray-50 mb-4">
          <div>Total Profit: <b>₦{(feeInfo.total_profit / 100).toLocaleString()}</b></div>
          <div>Performance Fee: <b>{(feeInfo.fee_percent * 100).toFixed(1)}%</b></div>
          <div>Fee Due: <b>₦{(feeInfo.fee_due / 100).toLocaleString()}</b></div>
          <div>Last Billed: <b>{feeInfo.last_billed}</b></div>
          <div>Next Billing: <b>{feeInfo.next_billing}</b></div>
        </div>
      ) : <div>Loading fee info...</div>}
      <Button onClick={handleCharge} disabled={loading} className="w-full">{loading ? 'Processing...' : 'Charge Performance Fee'}</Button>
      {chargeStatus && <div className="mt-2 text-green-600">Fee charge status: {chargeStatus}</div>}
      <div className="mt-8">
        <h3 className="font-bold mb-2">Fee Payment History</h3>
        {feeHistory.length === 0 ? <div>No performance fee payments yet.</div> : (
          <ul className="space-y-2">
            {feeHistory.map((item, idx) => (
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
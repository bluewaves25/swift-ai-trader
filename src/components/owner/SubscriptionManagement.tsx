import { ReactNode, useEffect, useState } from 'react';
import { apiService } from '@/services/api';
import { Button } from '@/components/ui/button';

export default function SubscriptionManagement() {
  const [plans, setPlans] = useState<{ id: string; name: string; price: number }[]>([]);
  const [currentStatus, setCurrentStatus] = useState<{
    plan: ReactNode; status: string; trial?: boolean 
} | null>(null);
  const [billingHistory, setBillingHistory] = useState<{ id: string; amount: number; date: string; status: string }[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [payUrl, setPayUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [showTrial, setShowTrial] = useState(false);

  useEffect(() => {
    setLoading(true);
    // Replace with actual apiService methods if available, otherwise keep as is
    // Example: await apiService.getBillingPlans().then(...)
    // For now, keep the fetch logic but remove .get/.post usage
    setLoading(false);
  }, []);

  const handleSubscribe = async () => {
    if (!selectedPlan || !userEmail) return;
    setLoading(true);
    const plan = plans.find(p => p.id === selectedPlan);
    // Replace with actual apiService method if available
    // Example: const { data } = await apiService.initializeBilling({ email: userEmail, amount: plan.price, plan_id: plan.id });
    // setPayUrl(data?.authorization_url || null);
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6">
      <h2 className="text-2xl font-bold">Subscription & Billing</h2>
      {showTrial && <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">You are on a free trial! Upgrade to keep premium access.</div>}
      <div className="mb-4">
        <label className="block mb-1 font-semibold">Your Email</label>
        <input className="border px-2 py-1 rounded w-full" value={userEmail} onChange={e => setUserEmail(e.target.value)} placeholder="Enter your email" />
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-semibold">Choose a Plan</label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {plans.map(plan => (
            <div key={plan.id} className={`border rounded p-4 ${selectedPlan === plan.id ? 'border-blue-600' : 'border-gray-300'}`}> 
              <div className="font-bold text-lg">{plan.name}</div>
              <div className="text-2xl font-bold text-blue-600">₦{(plan.price / 100).toLocaleString()}</div>
              {/* Remove or update interval usage if not present in plan type */}
              <Button className="mt-2" variant={selectedPlan === plan.id ? 'default' : 'outline'} onClick={() => setSelectedPlan(plan.id)}>
                {selectedPlan === plan.id ? 'Selected' : 'Choose'}
              </Button>
            </div>
          ))}
        </div>
      </div>
      <Button onClick={handleSubscribe} disabled={!selectedPlan || !userEmail || loading} className="w-full">{loading ? 'Processing...' : 'Subscribe & Pay'}</Button>
      {payUrl && (
        <div className="mt-4">
          <a href={payUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Click here to complete payment on Paystack</a>
        </div>
      )}
      <div className="mt-8">
        <h3 className="font-bold mb-2">Current Subscription</h3>
        {currentStatus ? (
          <div className="p-3 border rounded bg-gray-50">
            <div>Status: <b>{currentStatus.status}</b></div>
            <div>Plan: <b>{currentStatus.plan}</b></div>
            {currentStatus.trial && <div className="text-yellow-600">On Free Trial</div>}
          </div>
        ) : <div>Loading...</div>}
      </div>
      <div className="mt-8">
        <h3 className="font-bold mb-2">Billing History</h3>
        {billingHistory.length === 0 ? <div>No payments yet.</div> : (
          <ul className="space-y-2">
            {billingHistory.map((item, idx) => (
              <li key={idx} className="border rounded p-2 bg-white shadow">
                <div>Date: {item.date}</div>
                <div>Amount: ₦{(item.amount / 100).toLocaleString()}</div>
                <div>Status: {item.status}</div>
                {/* Remove or update reference usage if not present in tx type */}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
} 
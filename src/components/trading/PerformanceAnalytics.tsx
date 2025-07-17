
import { useEffect, useState } from 'react';
import { apiService } from '@/services/api';
import { toast } from 'sonner';

export default function PerformanceAnalytics() {
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPerformance = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiService.getPortfolioPerformance();
        setPerformance(data);
      } catch (err) {
        setError('Failed to fetch performance analytics');
        toast.error('Failed to fetch performance analytics');
      } finally {
        setLoading(false);
      }
    };
    fetchPerformance();
  }, []);

  if (loading) return <div className="p-6">Loading performance analytics...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;
  if (!performance) return <div className="p-6">No performance data found.</div>;

  // Render performance data here
  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-2">Performance Analytics</h2>
      <pre>{JSON.stringify(performance, null, 2)}</pre>
    </div>
  );
}

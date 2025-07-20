import { Tooltip, TooltipProvider, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { Dialog, DialogTrigger, DialogContent, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Play, Pause, Brain, TrendingUp, Activity, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import apiService from "@/services/api";
import { toast } from 'sonner';
import { LineChart, Line, XAxis, YAxis, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts';
import ReactDiffViewer from 'react-diff-viewer-continued';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useAuth } from '@/contexts/AuthContext';

interface Strategy {
  id: string;
  name: string;
  description?: string;
  status: string;
  performance: number;
  last_retrained: string;
}

const configPresets = [
  { label: 'Default', value: '{}' },
  { label: 'Mean Reversion', value: '{"window": 20, "z_threshold": 1.5}' },
  { label: 'Momentum', value: '{"lookback": 14, "threshold": 0.7}' },
];

export function StrategiesManagement() {
  const { user } = useAuth();
  const [userRole, setUserRole] = useState<string | null>(null);
  const [auditLog, setAuditLog] = useState<any[]>([]);
  const [strategies, setStrategies] = useState<string[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null);
  const [strategyConfig, setStrategyConfig] = useState<any>({});
  const [validationResult, setValidationResult] = useState<any>(null);
  const [backtestResult, setBacktestResult] = useState<any>(null);
  const [explainLog, setExplainLog] = useState<any[]>([]);
  const [newStrategy, setNewStrategy] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [live, setLive] = useState(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const [showDiff, setShowDiff] = useState(false);
  const [originalConfig, setOriginalConfig] = useState<string>('{}');
  const [validationHistory, setValidationHistory] = useState<any[]>([]);
  const [backtestEquity, setBacktestEquity] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [compare, setCompare] = useState<string[]>([]);

  const fetchStrategies = async () => {
    try {
      setLive(true);
      const res = await apiService.get("/api/v1/strategies");
      setStrategies(res.data.strategies);
      setLive(false);
    } catch (err) {
      setError('Failed to fetch strategies');
      setLive(false);
    }
  };

  useEffect(() => {
    fetchStrategies();
    pollingRef.current = setInterval(fetchStrategies, 5000);
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  useEffect(() => {
    // Fetch user role from Supabase users table if user is logged in
    const fetchRole = async () => {
      if (user) {
        const { data, error } = await window.supabase
          .from('users')
          .select('role')
          .eq('id', user.id)
          .single();
        setUserRole(data?.role || null);
      }
    };
    fetchRole();
  }, [user]);

  const handleAdd = async () => {
    if (!newStrategy) return;
    setLoading(true);
    await apiService.post("/api/v1/strategies/add", null, { params: { strategy_name: newStrategy } });
    setNewStrategy("");
    fetchStrategies();
    setLoading(false);
    logAction('add', { strategy: newStrategy });
    toast.success('Strategy added');
  };

  const handleRemove = async (name: string) => {
    setLoading(true);
    await apiService.post("/api/v1/strategies/remove", null, { params: { strategy_name: name } });
    fetchStrategies();
    setLoading(false);
    logAction('remove', { strategy: name });
    toast.success('Strategy removed');
  };

  const handleEditConfig = (name: string) => {
    setSelectedStrategy(name);
    // Fetch current config from backend if available, else use empty
    setOriginalConfig(JSON.stringify(strategyConfig, null, 2));
    setStrategyConfig({});
    setShowDiff(false);
  };

  const handlePreset = (preset: string) => {
    setStrategyConfig(JSON.parse(preset));
  };

  const handleUpdate = async () => {
    if (!selectedStrategy) return;
    setShowDiff(true);
  };

  const confirmUpdate = async () => {
    setLoading(true);
    await apiService.post("/api/v1/strategies/update", { strategy_name: selectedStrategy, config: strategyConfig });
    fetchStrategies();
    setShowDiff(false);
    setLoading(false);
    logAction('update', { strategy: selectedStrategy, config: strategyConfig });
    toast.success('Strategy config updated');
  };

  const handleValidate = async (name: string) => {
    setLoading(true);
    const res = await apiService.get(`/api/v1/strategies/validate/${name}`);
    setValidationResult(res.data);
    setValidationHistory((prev) => [{ strategy: name, ...res.data, date: new Date().toLocaleString() }, ...prev]);
    setLoading(false);
  };

  const handleBacktest = async (name: string, data: any[]) => {
    setLoading(true);
    const res = await apiService.post(`/api/v1/strategies/backtest`, { strategy_name: name, data });
    setBacktestResult(res.data);
    // Demo: generate fake equity curve
    setBacktestEquity(Array.from({ length: 20 }, (_, i) => ({ time: i, equity: 10000 + i * 100 + Math.random() * 200 })));
    setLoading(false);
  };

  const handleExplainLog = async () => {
    setLoading(true);
    const res = await apiService.get(`/api/v1/engine/explainability`);
    setExplainLog(res.data);
    setLoading(false);
  };

  // Demo performance data for chart (replace with real data if available)
  const demoPerfData = Array.from({ length: 10 }, (_, i) => ({ time: i, winRate: 50 + Math.random() * 50 }));

  const filteredStrategies = strategies.filter(name => name.toLowerCase().includes(search.toLowerCase()));

  // Audit log helper
  const logAction = (action: string, details: any) => {
    setAuditLog(prev => [{ action, details, date: new Date().toLocaleString() }, ...prev]);
  };

  if (userRole !== 'owner') {
    return <div className="text-red-500">You do not have access to strategy management.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <h2 className="text-2xl font-bold">Strategy Management</h2>
        {live ? <span className="text-green-600 animate-pulse">● live</span> : <span className="text-gray-400">●</span>}
      </div>
      {error && <div className="text-red-500">{error}</div>}
      <div className="flex gap-2 items-center mb-4">
        <input
          className="border px-2 py-1 rounded"
          placeholder="Strategy name to add"
          value={newStrategy}
          onChange={e => setNewStrategy(e.target.value)}
        />
        <Button onClick={handleAdd} disabled={loading || !newStrategy}>Add Strategy</Button>
        <input
          className="border px-2 py-1 rounded"
          placeholder="Search strategies..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <Button onClick={() => setCompare(filteredStrategies)}>Compare All</Button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {filteredStrategies.map((name) => (
          <Card key={name} className="relative">
            <CardHeader className="pb-4 flex flex-row items-center justify-between">
              <CardTitle className="text-lg">{name}</CardTitle>
              <Button variant="destructive" size="sm" onClick={() => handleRemove(name)} disabled={loading}>Remove</Button>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button size="sm" onClick={() => handleEditConfig(name)}>Edit Config</Button>
              <Button size="sm" onClick={() => handleValidate(name)}>Validate</Button>
              <Button size="sm" onClick={() => handleBacktest(name, [])}>Backtest (empty data)</Button>
              <Button size="sm" onClick={() => setCompare(prev => prev.includes(name) ? prev.filter(n => n !== name) : [...prev, name])}>
                {compare.includes(name) ? 'Remove from Compare' : 'Compare'}
              </Button>
              <div className="mt-2">
                <h4 className="font-semibold text-xs mb-1">Performance (Win Rate)</h4>
                <ResponsiveContainer width="100%" height={80}>
                  <LineChart data={demoPerfData} margin={{ left: -20, right: 10, top: 5, bottom: 5 }}>
                    <XAxis dataKey="time" hide />
                    <YAxis domain={[0, 100]} hide />
                    <ChartTooltip />
                    <Line type="monotone" dataKey="winRate" stroke="#2563eb" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      {selectedStrategy && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h3 className="font-bold">Edit Config for {selectedStrategy}</h3>
          <div className="flex gap-2 mb-2">
            <select onChange={e => handlePreset(e.target.value)} className="border rounded px-2 py-1">
              <option value="">Preset...</option>
              {configPresets.map(p => <option key={p.label} value={p.value}>{p.label}</option>)}
            </select>
            <span className="text-xs text-muted-foreground">Choose a preset or edit below</span>
          </div>
          <textarea
            className="w-full border rounded p-2 mt-2"
            rows={6}
            placeholder="JSON config"
            value={JSON.stringify(strategyConfig, null, 2)}
            onChange={e => {
              try {
                setStrategyConfig(JSON.parse(e.target.value));
                setError(null);
              } catch {
                setError('Invalid JSON');
              }
            }}
          />
          {error && <div className="text-red-500">{error}</div>}
          <Button className="mt-2" onClick={handleUpdate} disabled={loading || !!error}>Show Diff & Update</Button>
          {showDiff && (
            <div className="mt-4">
              <h4 className="font-bold">Config Diff</h4>
              <ReactDiffViewer
                oldValue={originalConfig}
                newValue={JSON.stringify(strategyConfig, null, 2)}
                splitView={true}
              />
              <Button className="mt-2" onClick={confirmUpdate} disabled={loading}>Confirm Update</Button>
              <Button className="mt-2 ml-2" variant="outline" onClick={() => setShowDiff(false)}>Cancel</Button>
            </div>
          )}
        </div>
      )}
      {validationResult && (
        <div className="mt-6 p-4 border rounded bg-green-50">
          <h3 className="font-bold">Validation Result</h3>
          <pre>{JSON.stringify(validationResult, null, 2)}</pre>
        </div>
      )}
      {backtestResult && (
        <div className="mt-6 p-4 border rounded bg-blue-50">
          <h3 className="font-bold">Backtest Result</h3>
          <pre>{JSON.stringify(backtestResult, null, 2)}</pre>
          <h4 className="font-semibold mt-2">Equity Curve</h4>
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={backtestEquity} margin={{ left: -20, right: 10, top: 5, bottom: 5 }}>
              <XAxis dataKey="time" />
              <YAxis />
              <ChartTooltip />
              <Line type="monotone" dataKey="equity" stroke="#16a34a" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
      {/* Strategy Comparison View */}
      {compare.length > 1 && (
        <div className="mt-6 p-4 border rounded bg-purple-50">
          <h3 className="font-bold">Strategy Comparison</h3>
          <ul className="flex flex-wrap gap-4">
            {compare.map(name => (
              <li key={name} className="border rounded p-2 bg-white shadow">
                <div className="font-semibold">{name}</div>
                {/* Add more analytics here as needed */}
                <ResponsiveContainer width={180} height={60}>
                  <LineChart data={demoPerfData} margin={{ left: -20, right: 10, top: 5, bottom: 5 }}>
                    <XAxis dataKey="time" hide />
                    <YAxis domain={[0, 100]} hide />
                    <ChartTooltip />
                    <Line type="monotone" dataKey="winRate" stroke="#2563eb" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="mt-6">
        <Button onClick={handleExplainLog}>Show Explainability Log</Button>
        {explainLog.length > 0 && (
          <div className="mt-2 p-4 border rounded bg-yellow-50">
            <h3 className="font-bold">Explainability Log</h3>
            <ul>
              {explainLog.map((log, idx) => (
                <li key={idx}><pre>{JSON.stringify(log, null, 2)}</pre></li>
              ))}
            </ul>
          </div>
        )}
      </div>
      {/* Validation History Table */}
      {validationHistory.length > 0 && (
        <div className="mt-6">
          <h3 className="font-bold">Validation History</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Strategy</TableHead>
                <TableHead>Result</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {validationHistory.map((v, idx) => (
                <TableRow key={idx}>
                  <TableCell>{v.strategy}</TableCell>
                  <TableCell>{JSON.stringify(v.validation)}</TableCell>
                  <TableCell>{v.date}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
      {/* Audit Log */}
      {auditLog.length > 0 && (
        <div className="mt-6 p-4 border rounded bg-gray-100">
          <h3 className="font-bold">Audit Log</h3>
          <ul>
            {auditLog.map((log, idx) => (
              <li key={idx} className="text-xs mb-1">
                <b>{log.date}</b> — <span className="text-blue-700">{log.action}</span> {JSON.stringify(log.details)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
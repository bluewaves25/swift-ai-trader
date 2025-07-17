import { Tooltip, TooltipProvider, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { Dialog, DialogTrigger, DialogContent, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Play, Pause, Brain, TrendingUp, Activity, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { apiService } from '@/services/api';
import { toast } from 'sonner';

interface Strategy {
  id: string;
  name: string;
  description?: string;
  status: string;
  performance: number;
  last_retrained: string;
}

export function StrategiesManagement() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [retrainingId, setRetrainingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirmAction, setConfirmAction] = useState<{type: string, id: string} | null>(null);

  const fetchStrategies = async () => {
    try {
      const data = await apiService.getStrategies();
      setStrategies(data as Strategy[]);
    } catch (err) {
      setError('Failed to fetch strategies');
    }
  };

  useEffect(() => {
    fetchStrategies();
    const interval = setInterval(fetchStrategies, 5000); // Poll for retrain progress
    return () => clearInterval(interval);
  }, []);

  const handleDisable = async (id: string) => {
    setLoadingId(id);
    try {
      await apiService.disableStrategy(id);
      toast.success('Strategy disabled');
      fetchStrategies();
    } catch (err) {
      toast.error('Failed to disable strategy');
    } finally {
      setLoadingId(null);
    }
  };

  const handleRetrain = async (id: string) => {
    setRetrainingId(id);
    try {
      await apiService.retrainStrategy(id);
      toast.success('Retrain started');
      fetchStrategies();
    } catch (err) {
      toast.error('Failed to retrain strategy');
    } finally {
      setRetrainingId(null);
    }
  };

  const handleDelete = async (id: string) => {
    setLoadingId(id);
    try {
      await apiService.deleteStrategy(id);
      toast.success('Strategy deleted');
      fetchStrategies();
    } catch (err) {
      toast.error('Failed to delete strategy');
    } finally {
      setLoadingId(null);
    }
  };

  const getPerformanceColor = (winRate: number) => {
    if (winRate >= 70) return "text-green-600";
    if (winRate >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <TooltipProvider>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Strategy Management</h2>
          <Badge variant="outline" className="px-3 py-1">
            {strategies.filter(s => s.status === 'active').length} Active
          </Badge>
        </div>
        {error && <div className="text-red-500">{error}</div>}
        <div className="grid gap-6 md:grid-cols-2">
          {strategies.length === 0 ? (
            <div className="col-span-2 flex justify-center items-center h-32">
              <div className="w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full animate-spin" />
              <span className="ml-2 text-muted-foreground">Loading strategies...</span>
            </div>
          ) : strategies.map((strategy) => {
            const isLoading = loadingId === strategy.id;
            const isRetraining = retrainingId === strategy.id || strategy.status === 'retraining';
            const statusIcon = strategy.status === 'active' ? <Play className="h-4 w-4 text-green-600" /> : strategy.status === 'retraining' ? <Activity className="h-4 w-4 text-yellow-600 animate-spin" /> : <Pause className="h-4 w-4 text-gray-400" />;
            return (
              <Card key={strategy.id} className="relative overflow-hidden transition-all duration-300 hover:shadow-lg">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {statusIcon}
                      <div>
                        <CardTitle className="text-lg">{strategy.name}</CardTitle>
                        <CardDescription className="text-sm">{strategy.description}</CardDescription>
                      </div>
                    </div>
                    <Badge variant={strategy.status === 'active' ? 'default' : strategy.status === 'retraining' ? 'secondary' : 'destructive'}>{strategy.status}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <div className="text-xl font-bold text-blue-600">{strategy.performance.toFixed(2)}</div>
                      <div className="text-xs text-muted-foreground">Performance</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Last Retrained</div>
                      <div className="text-sm">{new Date(strategy.last_retrained).toLocaleString()}</div>
                    </div>
                  </div>
                  <div className="flex gap-2 pt-2">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="outline" size="sm" className="flex-1" onClick={() => setConfirmAction({type: 'disable', id: strategy.id})} disabled={isLoading || isRetraining}>
                          Disable
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Disable this strategy</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="outline" size="sm" className="flex-1" onClick={() => setConfirmAction({type: 'retrain', id: strategy.id})} disabled={isRetraining}>
                          {isRetraining ? 'Retraining...' : 'Retrain'}
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Retrain this strategy</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="destructive" size="sm" className="flex-1" onClick={() => setConfirmAction({type: 'delete', id: strategy.id})} disabled={isLoading}>
                          Delete
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Delete this strategy</TooltipContent>
                    </Tooltip>
                  </div>
                  {isRetraining && (
                    <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                        Retraining...
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
        {/* Confirmation Dialog */}
        <Dialog open={!!confirmAction} onOpenChange={open => !open && setConfirmAction(null)}>
          <DialogContent>
            <DialogTitle>Confirm {confirmAction?.type?.charAt(0).toUpperCase() + confirmAction?.type?.slice(1)}</DialogTitle>
            <DialogDescription>
              Are you sure you want to {confirmAction?.type} this strategy?
            </DialogDescription>
            <DialogFooter>
              <Button variant="outline" onClick={() => setConfirmAction(null)}>Cancel</Button>
              <Button variant={confirmAction?.type === 'delete' ? 'destructive' : 'default'}
                onClick={async () => {
                  if (!confirmAction) return;
                  if (confirmAction.type === 'disable') await handleDisable(confirmAction.id);
                  if (confirmAction.type === 'retrain') await handleRetrain(confirmAction.id);
                  if (confirmAction.type === 'delete') await handleDelete(confirmAction.id);
                  setConfirmAction(null);
                }}>
                Confirm
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </TooltipProvider>
  );
}
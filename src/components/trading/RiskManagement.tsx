
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { Shield, AlertTriangle, TrendingDown, Target } from "lucide-react";

interface RiskSettings {
  id: string;
  user_id: string;
  max_loss: number;
  max_position_size: number;
  max_daily_loss: number;
  stop_loss_percentage: number;
  take_profit_percentage: number;
  max_open_positions: number;
  risk_per_trade: number;
}

export default function RiskManagement() {
  const { user } = useAuth();
  const [riskSettings, setRiskSettings] = useState<RiskSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    maxDailyLoss: 5,
    stopLossPercentage: 2,
    takeProfitPercentage: 4,
    maxOpenPositions: 5,
    riskPerTrade: 1
  });

  useEffect(() => {
    if (user) {
      fetchRiskSettings();
    }
  }, [user]);

  const fetchRiskSettings = async () => {
    try {
      const { data, error } = await supabase
        .from('risk_settings')
        .select('*')
        .eq('user_id', user?.id)
        .single();

      if (error && error.code !== 'PGRST116') {
        throw error;
      }

      if (data) {
        const settings: RiskSettings = {
          id: data.id,
          user_id: data.user_id || '',
          max_loss: data.max_loss || 0,
          max_position_size: data.max_position_size || 0,
          max_daily_loss: 5,
          stop_loss_percentage: 2,
          take_profit_percentage: 4,
          max_open_positions: 5,
          risk_per_trade: 1
        };
        setRiskSettings(settings);
        setFormData({
          maxDailyLoss: settings.max_daily_loss,
          stopLossPercentage: settings.stop_loss_percentage,
          takeProfitPercentage: settings.take_profit_percentage,
          maxOpenPositions: settings.max_open_positions,
          riskPerTrade: settings.risk_per_trade
        });
      }
    } catch (error) {
      console.error('Error fetching risk settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const { error } = await supabase
        .from('risk_settings')
        .upsert({
          user_id: user?.id,
          max_loss: formData.maxDailyLoss,
          max_position_size: formData.maxOpenPositions
        });

      if (error) throw error;

      toast.success('Risk settings updated successfully');
      fetchRiskSettings();
    } catch (error) {
      console.error('Error updating risk settings:', error);
      toast.error('Failed to update risk settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-6">Loading risk management...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Risk Management</h2>
        <Shield className="h-8 w-8 text-blue-500" />
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              <span>Daily Risk Limits</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Maximum Daily Loss (%)</Label>
              <Slider
                value={[formData.maxDailyLoss]}
                onValueChange={(value) => setFormData({ ...formData, maxDailyLoss: value[0] })}
                max={20}
                min={1}
                step={0.5}
                className="w-full"
              />
              <p className="text-sm text-muted-foreground">
                Current: {formData.maxDailyLoss}%
              </p>
            </div>

            <div className="space-y-2">
              <Label>Maximum Open Positions</Label>
              <Slider
                value={[formData.maxOpenPositions]}
                onValueChange={(value) => setFormData({ ...formData, maxOpenPositions: value[0] })}
                max={20}
                min={1}
                step={1}
                className="w-full"
              />
              <p className="text-sm text-muted-foreground">
                Current: {formData.maxOpenPositions} positions
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingDown className="h-5 w-5 text-red-500" />
              <span>Position Management</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Stop Loss Percentage (%)</Label>
              <Slider
                value={[formData.stopLossPercentage]}
                onValueChange={(value) => setFormData({ ...formData, stopLossPercentage: value[0] })}
                max={10}
                min={0.5}
                step={0.1}
                className="w-full"
              />
              <p className="text-sm text-muted-foreground">
                Current: {formData.stopLossPercentage}%
              </p>
            </div>

            <div className="space-y-2">
              <Label>Take Profit Percentage (%)</Label>
              <Slider
                value={[formData.takeProfitPercentage]}
                onValueChange={(value) => setFormData({ ...formData, takeProfitPercentage: value[0] })}
                max={20}
                min={1}
                step={0.1}
                className="w-full"
              />
              <p className="text-sm text-muted-foreground">
                Current: {formData.takeProfitPercentage}%
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-green-500" />
              <span>Trade Size Management</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Risk Per Trade (%)</Label>
              <Slider
                value={[formData.riskPerTrade]}
                onValueChange={(value) => setFormData({ ...formData, riskPerTrade: value[0] })}
                max={5}
                min={0.1}
                step={0.1}
                className="w-full"
              />
              <p className="text-sm text-muted-foreground">
                Current: {formData.riskPerTrade}% of account balance
              </p>
            </div>
          </CardContent>
        </Card>

        <Button onClick={handleSave} disabled={saving} className="w-full">
          {saving ? 'Saving...' : 'Save Risk Settings'}
        </Button>
      </div>
    </div>
  );
}

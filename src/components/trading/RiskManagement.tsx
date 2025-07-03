
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { Shield, AlertTriangle, Save } from "lucide-react";
import { toast } from "sonner";

interface RiskSettings {
  id?: string;
  max_daily_loss: number;
  max_position_size: number;
  stop_loss_percentage: number;
  take_profit_percentage: number;
  max_open_positions: number;
  risk_per_trade: number;
}

const RiskManagement = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState<RiskSettings>({
    max_daily_loss: 100,
    max_position_size: 0.05,
    stop_loss_percentage: 0.02,
    take_profit_percentage: 0.04,
    max_open_positions: 5,
    risk_per_trade: 0.01
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      fetchRiskSettings();
    }
  }, [user]);

  const fetchRiskSettings = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('risk_settings')
        .select('*')
        .eq('user_id', user.id)
        .single();

      if (error && error.code !== 'PGRST116') {
        console.error('Error fetching risk settings:', error);
        return;
      }

      if (data) {
        setSettings(data);
      }
    } catch (error) {
      console.error('Error in fetchRiskSettings:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveRiskSettings = async () => {
    if (!user) return;

    setSaving(true);
    try {
      const { error } = await supabase
        .from('risk_settings')
        .upsert({
          ...settings,
          user_id: user.id
        });

      if (error) throw error;

      toast.success('Risk settings saved successfully');
    } catch (error) {
      console.error('Error saving risk settings:', error);
      toast.error('Failed to save risk settings');
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (key: keyof RiskSettings, value: number) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">Loading risk settings...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Shield className="h-5 w-5" />
          <span>Risk Management</span>
        </CardTitle>
        <CardDescription>
          Configure automated risk controls to protect your capital
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div>
              <Label htmlFor="maxDailyLoss">Maximum Daily Loss ($)</Label>
              <Input
                id="maxDailyLoss"
                type="number"
                value={settings.max_daily_loss}
                onChange={(e) => updateSetting('max_daily_loss', parseFloat(e.target.value) || 0)}
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Trading will stop if daily losses exceed this amount
              </p>
            </div>

            <div>
              <Label>Maximum Position Size ({(settings.max_position_size * 100).toFixed(1)}%)</Label>
              <Slider
                value={[settings.max_position_size * 100]}
                onValueChange={([value]) => updateSetting('max_position_size', value / 100)}
                max={20}
                min={1}
                step={0.5}
                className="mt-3"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Maximum percentage of portfolio per single trade
              </p>
            </div>

            <div>
              <Label>Stop Loss ({(settings.stop_loss_percentage * 100).toFixed(1)}%)</Label>
              <Slider
                value={[settings.stop_loss_percentage * 100]}
                onValueChange={([value]) => updateSetting('stop_loss_percentage', value / 100)}
                max={10}
                min={0.5}
                step={0.1}
                className="mt-3"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Automatic stop loss percentage for all trades
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <Label>Take Profit ({(settings.take_profit_percentage * 100).toFixed(1)}%)</Label>
              <Slider
                value={[settings.take_profit_percentage * 100]}
                onValueChange={([value]) => updateSetting('take_profit_percentage', value / 100)}
                max={20}
                min={1}
                step={0.1}
                className="mt-3"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Automatic take profit percentage for all trades
              </p>
            </div>

            <div>
              <Label htmlFor="maxPositions">Maximum Open Positions</Label>
              <Input
                id="maxPositions"
                type="number"
                value={settings.max_open_positions}
                onChange={(e) => updateSetting('max_open_positions', parseInt(e.target.value) || 0)}
                className="mt-2"
                min="1"
                max="20"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Maximum number of concurrent open positions
              </p>
            </div>

            <div>
              <Label>Risk Per Trade ({(settings.risk_per_trade * 100).toFixed(2)}%)</Label>
              <Slider
                value={[settings.risk_per_trade * 100]}
                onValueChange={([value]) => updateSetting('risk_per_trade', value / 100)}
                max={5}
                min={0.1}
                step={0.1}
                className="mt-3"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Percentage of portfolio to risk per individual trade
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2 p-4 border rounded-lg bg-yellow-50 dark:bg-yellow-950/20">
          <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            These settings apply to all automated trades. Changes take effect immediately.
          </p>
        </div>

        <Button onClick={saveRiskSettings} disabled={saving} className="w-full">
          <Save className="h-4 w-4 mr-2" />
          {saving ? 'Saving...' : 'Save Risk Settings'}
        </Button>
      </CardContent>
    </Card>
  );
};

export default RiskManagement;

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Shield, AlertTriangle, TrendingDown, Settings, Save } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

export function RiskManagement() {
  const [riskSettings, setRiskSettings] = useState({
    maxRiskPerTrade: 2.5,
    maxRiskPerDay: 10.0,
    maxRiskPerWeek: 25.0,
    maxPositionSize: 7.0,
    stopLossPercentage: 2.0,
    takeProfitPercentage: 4.0,
    maxConcurrentTrades: 5,
    riskLevel: "moderate"
  });
  
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSliderChange = (field: string) => (value: number[]) => {
    setRiskSettings(prev => ({
      ...prev,
      [field]: value[0]
    }));
  };

  const handleInputChange = (field: string, value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      setRiskSettings(prev => ({
        ...prev,
        [field]: numValue
      }));
    }
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast({
        title: "Risk Settings Updated",
        description: "Your risk management settings have been saved successfully",
        className: "bg-gradient-to-r from-green-50 to-emerald-50 border-green-200"
      });
    } catch (error) {
      toast({
        title: "Update Failed",
        description: "Failed to update risk settings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case "conservative": return "text-green-600 bg-green-100 border-green-200";
      case "moderate": return "text-yellow-600 bg-yellow-100 border-yellow-200";
      case "aggressive": return "text-red-600 bg-red-100 border-red-200";
      default: return "text-gray-600 bg-gray-100 border-gray-200";
    }
  };

  const getRiskLevel = () => {
    const avgRisk = (riskSettings.maxRiskPerTrade + riskSettings.maxRiskPerDay/4 + riskSettings.maxRiskPerWeek/10) / 3;
    if (avgRisk <= 3) return "conservative";
    if (avgRisk <= 6) return "moderate";
    return "aggressive";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Risk Management</h2>
        <Badge className={cn("px-3 py-1", getRiskLevelColor(getRiskLevel()))}>
          <Shield className="h-3 w-3 mr-1" />
          {getRiskLevel().charAt(0).toUpperCase() + getRiskLevel().slice(1)} Risk
        </Badge>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Risk Per Trade */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-indigo-50/50" />
          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-blue-600" />
              Risk Per Trade
            </CardTitle>
            <CardDescription>
              Maximum risk percentage per individual trade
            </CardDescription>
          </CardHeader>
          <CardContent className="relative space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Risk Percentage</Label>
                <span className="text-sm font-medium text-blue-600">
                  {riskSettings.maxRiskPerTrade}%
                </span>
              </div>
              <Slider
                value={[riskSettings.maxRiskPerTrade]}
                onValueChange={handleSliderChange('maxRiskPerTrade')}
                max={10}
                min={0.5}
                step={0.1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>0.5%</span>
                <span>10%</span>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="stopLoss">Stop Loss %</Label>
                <Input
                  id="stopLoss"
                  type="number"
                  value={riskSettings.stopLossPercentage}
                  onChange={(e) => handleInputChange('stopLossPercentage', e.target.value)}
                  step="0.1"
                  min="0.5"
                  max="10"
                />
              </div>
              <div>
                <Label htmlFor="takeProfit">Take Profit %</Label>
                <Input
                  id="takeProfit"
                  type="number"
                  value={riskSettings.takeProfitPercentage}
                  onChange={(e) => handleInputChange('takeProfitPercentage', e.target.value)}
                  step="0.1"
                  min="1"
                  max="20"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Risk Per Time Period */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-orange-50/50 to-red-50/50" />
          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Time-Based Risk Limits
            </CardTitle>
            <CardDescription>
              Maximum risk exposure over time periods
            </CardDescription>
          </CardHeader>
          <CardContent className="relative space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Daily Risk Limit</Label>
                <span className="text-sm font-medium text-orange-600">
                  {riskSettings.maxRiskPerDay}%
                </span>
              </div>
              <Slider
                value={[riskSettings.maxRiskPerDay]}
                onValueChange={handleSliderChange('maxRiskPerDay')}
                max={25}
                min={2}
                step={0.5}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Weekly Risk Limit</Label>
                <span className="text-sm font-medium text-red-600">
                  {riskSettings.maxRiskPerWeek}%
                </span>
              </div>
              <Slider
                value={[riskSettings.maxRiskPerWeek]}
                onValueChange={handleSliderChange('maxRiskPerWeek')}
                max={50}
                min={5}
                step={1}
                className="w-full"
              />
            </div>
          </CardContent>
        </Card>

        {/* Position Management */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-50/50 to-pink-50/50" />
          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-purple-600" />
              Position Management
            </CardTitle>
            <CardDescription>
              Control position sizing and concurrent trades
            </CardDescription>
          </CardHeader>
          <CardContent className="relative space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Max Position Size</Label>
                <span className="text-sm font-medium text-purple-600">
                  {riskSettings.maxPositionSize}%
                </span>
              </div>
              <Slider
                value={[riskSettings.maxPositionSize]}
                onValueChange={handleSliderChange('maxPositionSize')}
                max={20}
                min={1}
                step={0.5}
                className="w-full"
              />
            </div>

            <div>
              <Label htmlFor="maxTrades">Max Concurrent Trades</Label>
              <Input
                id="maxTrades"
                type="number"
                value={riskSettings.maxConcurrentTrades}
                onChange={(e) => handleInputChange('maxConcurrentTrades', e.target.value)}
                min="1"
                max="20"
              />
            </div>
          </CardContent>
        </Card>

        {/* Risk Profile */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-green-50/50 to-teal-50/50" />
          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-green-600" />
              Risk Profile
            </CardTitle>
            <CardDescription>
              Overall risk management strategy
            </CardDescription>
          </CardHeader>
          <CardContent className="relative space-y-4">
            <div>
              <Label htmlFor="riskLevel">Risk Level</Label>
              <Select
                value={riskSettings.riskLevel}
                onValueChange={(value) => setRiskSettings(prev => ({ ...prev, riskLevel: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="conservative">Conservative</SelectItem>
                  <SelectItem value="moderate">Moderate</SelectItem>
                  <SelectItem value="aggressive">Aggressive</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium">Current Risk Assessment</div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>Daily Risk Used</span>
                  <span className="text-orange-600">3.2% of {riskSettings.maxRiskPerDay}%</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Weekly Risk Used</span>
                  <span className="text-red-600">8.7% of {riskSettings.maxRiskPerWeek}%</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Active Positions</span>
                  <span className="text-blue-600">2 of {riskSettings.maxConcurrentTrades}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Save Button */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium">Save Risk Settings</h3>
              <p className="text-sm text-muted-foreground">
                Apply these settings to the trading engine
              </p>
            </div>
            <Button
              onClick={handleSaveSettings}
              disabled={loading}
              className="transition-all duration-300 transform hover:scale-105"
              size="lg"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Settings
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
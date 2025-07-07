
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { Settings, Bell, Shield, Globe } from "lucide-react";

interface UserSettings {
  id: string;
  notifications: boolean;
  user_id: string;
}

export default function InvestorSettings() {
  const { user } = useAuth();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    emailNotifications: true,
    smsNotifications: false,
    tradeAlerts: true,
    darkMode: false,
    language: 'en',
    timezone: 'UTC'
  });

  useEffect(() => {
    if (user) {
      fetchSettings();
    }
  }, [user]);

  const fetchSettings = async () => {
    try {
      const { data, error } = await supabase
        .from('user_settings')
        .select('*')
        .eq('user_id', user?.id)
        .single();

      if (error && error.code !== 'PGRST116') {
        throw error;
      }

      if (data) {
        setSettings(data);
        setFormData({
          emailNotifications: data.notifications || false,
          smsNotifications: false,
          tradeAlerts: true,
          darkMode: false,
          language: 'en',
          timezone: 'UTC'
        });
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const { error } = await supabase
        .from('user_settings')
        .upsert({
          user_id: user?.id,
          notifications: formData.emailNotifications
        });

      if (error) throw error;

      toast.success('Settings updated successfully');
      fetchSettings();
    } catch (error) {
      console.error('Error updating settings:', error);
      toast.error('Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-6">Loading settings...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Settings</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bell className="h-5 w-5" />
            <span>Notifications</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="email-notifications">Email Notifications</Label>
            <Switch
              id="email-notifications"
              checked={formData.emailNotifications}
              onCheckedChange={(checked) => 
                setFormData({ ...formData, emailNotifications: checked })
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="trade-alerts">Trade Alerts</Label>
            <Switch
              id="trade-alerts"
              checked={formData.tradeAlerts}
              onCheckedChange={(checked) => 
                setFormData({ ...formData, tradeAlerts: checked })
              }
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Preferences</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="dark-mode">Dark Mode</Label>
            <Switch
              id="dark-mode"
              checked={formData.darkMode}
              onCheckedChange={(checked) => 
                setFormData({ ...formData, darkMode: checked })
              }
            />
          </div>
        </CardContent>
      </Card>

      <Button onClick={handleSave} disabled={saving} className="w-full">
        {saving ? 'Saving...' : 'Save Settings'}
      </Button>
    </div>
  );
}

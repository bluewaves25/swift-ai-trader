
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";

const WalletManager = () => {
  const { user } = useAuth();
  const [wallets, setWallets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchWallets();
    }
  }, [user]);

  const fetchWallets = async () => {
    try {
      const { data, error } = await supabase
        .from('wallets')
        .select('*')
        .eq('user_id', user?.id);

      if (error) throw error;
      setWallets(data || []);
    } catch (error) {
      console.error('Error fetching wallets:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading wallets...</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Wallet Manager</CardTitle>
      </CardHeader>
      <CardContent>
        {wallets.length === 0 ? (
          <p>No wallets found.</p>
        ) : (
          <div className="space-y-4">
            {wallets.map((wallet: any) => (
              <div key={wallet.id} className="p-4 border rounded-lg">
                <p><strong>Currency:</strong> {wallet.currency}</p>
                <p><strong>Balance:</strong> {wallet.balance}</p>
                <p><strong>Broker:</strong> {wallet.broker}</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default WalletManager;

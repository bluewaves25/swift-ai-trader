
import { Loader2 } from "lucide-react";

const LoadingScreen = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin mx-auto text-primary" />
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-foreground">Waves Quant Engine</h2>
          <p className="text-muted-foreground">Loading your trading dashboard...</p>
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;

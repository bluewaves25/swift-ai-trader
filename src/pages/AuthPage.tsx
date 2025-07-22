import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/hooks/useAuth";
import { X, Brain } from "lucide-react";
import { useNavigate, Link } from "react-router-dom";

const AuthPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formLoading, setFormLoading] = useState(false);
  const [showReset, setShowReset] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [resetLoading, setResetLoading] = useState(false);
  const { signIn, signUp, resetPassword, user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && user) {
      const role = (user as any)?.role || (user as any)?.user_metadata?.role;
      if (role === 'owner') {
        navigate('/owner-dashboard', { replace: true });
      } else {
        navigate('/investor-dashboard', { replace: true });
      }
    }
  }, [user, loading, navigate]);

  const handleAuthAction = async (action: 'signIn' | 'signUp') => {
    setFormLoading(true);
    try {
      if (action === 'signIn') {
        await signIn(email, password);
      } else {
        await signUp(email, password);
      }
    } finally {
      setFormLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setResetLoading(true);
    try {
      await resetPassword(resetEmail);
      setShowReset(false);
      setResetEmail("");
    } finally {
      setResetLoading(false);
    }
  };
  
  return (
    <div 
      className="min-h-screen w-full flex items-center justify-center p-4 bg-cover bg-center"
      style={{ backgroundImage: "url('/landing_background_1.png')" }}
    >
      <div className="absolute inset-0 bg-black/50 z-0"></div>
      <Link to="/" className="absolute top-4 right-4 z-20">
        <Button variant="ghost" size="icon" className="h-8 w-8 text-white hover:bg-white/20">
          <X className="h-4 w-4" />
        </Button>
      </Link>
      
      <Card className="w-full max-w-md bg-white/10 dark:bg-black/30 backdrop-blur-lg border-white/20 text-white rounded-2xl z-10">
        <CardHeader className="text-center">
          <div className="flex justify-center items-center gap-2 mb-2">
            <Brain className="h-7 w-7" />
            <CardTitle className="text-2xl font-bold">Waves Quant</CardTitle>
          </div>
          <CardDescription className="text-gray-300">
            Enter your credentials to access your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="signin" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-white/10 dark:bg-black/20">
              <TabsTrigger value="signin" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">Sign In</TabsTrigger>
              <TabsTrigger value="signup" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">Sign Up</TabsTrigger>
            </TabsList>
            
            <TabsContent value="signin" className="mt-4">
              <form onSubmit={(e) => { e.preventDefault(); handleAuthAction('signIn'); }} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="m@example.com" required value={email} onChange={(e) => setEmail(e.target.value)} className="bg-transparent" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <Label htmlFor="password">Password</Label>
                    <Link to="#" onClick={(e) => { e.preventDefault(); setShowReset(true); }} className="ml-auto inline-block text-sm text-blue-400 hover:underline">
                      Forgot your password?
                    </Link>
                  </div>
                  <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="bg-transparent" />
                </div>
                <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700" disabled={formLoading}>
                  {formLoading ? "Signing In..." : "Sign In"}
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="signup" className="mt-4">
              <form onSubmit={(e) => { e.preventDefault(); handleAuthAction('signUp'); }} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="signup-email">Email</Label>
                  <Input id="signup-email" type="email" placeholder="m@example.com" required value={email} onChange={(e) => setEmail(e.target.value)} className="bg-transparent" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="signup-password">Password</Label>
                  <Input id="signup-password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="bg-transparent" />
                </div>
                <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700" disabled={formLoading}>
                  {formLoading ? "Creating Account..." : "Create Account"}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
          
          {showReset && (
            <div className="mt-4 p-4 border border-white/20 rounded-lg bg-black/20">
              <form onSubmit={handleResetPassword} className="space-y-3">
                <p className="text-sm font-medium">Reset Password</p>
                <Input id="reset-email" type="email" placeholder="Enter your email" value={resetEmail} onChange={(e) => setResetEmail(e.target.value)} required className="bg-transparent" />
                <div className="flex gap-2">
                  <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700" disabled={resetLoading}>
                    {resetLoading ? "Sending..." : "Send Reset Link"}
                  </Button>
                  <Button type="button" variant="ghost" className="w-full hover:bg-white/20" onClick={() => setShowReset(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </div>
          )}

          <div className="mt-4 text-center text-xs text-gray-400">
            By signing up, you agree to our{" "}
            <Link to="/terms" className="underline hover:text-white">
              Terms of Service
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthPage;

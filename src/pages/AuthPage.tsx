import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/hooks/useAuth";
import { TrendingUp, Shield, X, Brain } from "lucide-react"; // <-- import Brain
import { useNavigate } from "react-router-dom";

const AuthPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formLoading, setFormLoading] = useState(false);
  const [showReset, setShowReset] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [resetLoading, setResetLoading] = useState(false);
  const { signIn, signUp, resetPassword, user, loading } = useAuth();
  const navigate = useNavigate();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    // Only redirect if loading is false and user is present
    if (!loading && user) {
      // Try to get role from user metadata if available
      const role = (user as any)?.role || (user as any)?.user_metadata?.role;
      if (role === 'owner') {
        navigate('/owner-dashboard', { replace: true });
      } else {
        navigate('/investor-dashboard', { replace: true });
      }
    }
    // Do NOT redirect if user is null (just signed out)
  }, [user, loading, navigate]);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    try {
      await signIn(email, password);
    } catch (error) {
      // Error is already handled in AuthContext
    } finally {
      setFormLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    try {
      await signUp(email, password);
    } catch (error) {
      // Error is already handled in AuthContext
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
    } catch (error) {
      // Error is already handled in AuthContext
    } finally {
      setResetLoading(false);
    }
  };

  const handleClose = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="absolute top-4 right-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleClose}
          className="h-8 w-8 text-white hover:bg-white/10"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="w-full max-w-md space-y-8">
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-2">
            <Brain className="h-8 w-8 text-blue-400" /> {/* Changed to Brain icon */}
            <h1 className="text-3xl font-bold text-white">Waves Quant Engine</h1>
          </div>
          <p className="text-gray-300">
            AI-Powered High Frequency Trading Platform
          </p>
        </div>

        <Card className="w-full bg-white/10 border-white/20 backdrop-blur-lg">
          <CardHeader>
            <CardTitle className="text-white">Welcome Back</CardTitle>
            <CardDescription className="text-gray-300">
              Sign in to your account or create an investor account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="signin" className="w-full">
              <TabsList className="grid w-full grid-cols-2 bg-white/5">
                <TabsTrigger value="signin" className="text-white data-[state=active]:bg-white/20">Sign In</TabsTrigger>
                <TabsTrigger value="signup" className="text-white data-[state=active]:bg-white/20">Investor Sign Up</TabsTrigger>
              </TabsList>
              
              <TabsContent value="signin">
                <form onSubmit={handleSignIn} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-white">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-white">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    />
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="button"
                      className="text-xs text-blue-300 hover:underline"
                      onClick={() => setShowReset(true)}
                    >
                      Forgot password?
                    </button>
                  </div>
                  <Button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700" disabled={formLoading}>
                    {formLoading ? "Signing in..." : "Sign In"}
                  </Button>
                </form>
                {showReset && (
                  <form onSubmit={handleResetPassword} className="mt-4 space-y-3 bg-black/40 p-4 rounded-lg">
                    <Label htmlFor="reset-email" className="text-white">Enter your email to reset password</Label>
                    <Input
                      id="reset-email"
                      type="email"
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      required
                      className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    />
                    <div className="flex gap-2">
                      <Button type="submit" className="w-full bg-blue-600" disabled={resetLoading}>
                        {resetLoading ? "Sending..." : "Send Reset Email"}
                      </Button>
                      <Button type="button" variant="outline" className="w-full" onClick={() => setShowReset(false)}>
                        Cancel
                      </Button>
                    </div>
                  </form>
                )}
              </TabsContent>
              
              <TabsContent value="signup">
                <form onSubmit={handleSignUp} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="signup-email" className="text-white">Email</Label>
                    <Input
                      id="signup-email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password" className="text-white">Password</Label>
                    <Input
                      id="signup-password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    />
                  </div>
                  <div className="p-3 bg-purple-600/20 border border-purple-500/20 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Shield className="h-4 w-4 text-purple-300" />
                      <span className="text-sm font-medium text-white">Investor Account</span>
                    </div>
                    <p className="text-xs text-gray-300 mt-1">
                      Track performance, manage deposits/withdrawals
                    </p>
                  </div>
                  <Button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700" disabled={formLoading}>
                    {formLoading ? "Creating account..." : "Create Investor Account"}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <div className="text-center text-sm text-gray-300">
          <p>Automated AI trading with professional oversight</p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;

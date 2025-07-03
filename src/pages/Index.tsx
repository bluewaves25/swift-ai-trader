
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Link } from "react-router-dom";
import { 
  TrendingUp, 
  Brain, 
  Zap, 
  Shield, 
  Activity, 
  Target,
  ArrowRight,
  CheckCircle,
  BarChart3,
  Cpu,
  X
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();

  const handleClose = () => {
    // You can customize this behavior - for now it just stays on the same page
    console.log('Close button clicked');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-8 w-8 text-primary" />
              <h1 className="text-2xl font-bold">Waves Quant Engine</h1>
            </div>
            <div className="flex items-center space-x-4">
              <ThemeToggle />
              <Button
                variant="ghost"
                size="icon"
                onClick={handleClose}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="space-y-4">
            <Badge variant="outline" className="px-4 py-2">
              <Cpu className="h-4 w-4 mr-2" />
              AI-Powered High Frequency Trading
            </Badge>
            <h2 className="text-4xl md:text-6xl font-bold tracking-tight">
              Professional Trading
              <span className="text-primary"> Automation</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Advanced AI-driven trading engine with real-time market analysis, 
              automated execution, and professional risk management for cryptocurrency markets.
            </p>
          </div>
          
          <div className="flex items-center justify-center space-x-4">
            <Link to="/auth">
              <Button size="lg" className="px-8">
                Start Investing
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h3 className="text-3xl font-bold mb-4">Advanced Trading Features</h3>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Built with institutional-grade technology and AI-powered decision making
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="border-2 hover:border-primary/20 transition-colors">
            <CardHeader>
              <Brain className="h-12 w-12 text-primary mb-4" />
              <CardTitle>AI Trading Signals</CardTitle>
              <CardDescription>
                Advanced machine learning algorithms analyze market patterns and generate 
                high-probability trading signals in real-time.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Pattern Recognition
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Market Sentiment Analysis
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Risk-Adjusted Signals
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/20 transition-colors">
            <CardHeader>
              <Zap className="h-12 w-12 text-primary mb-4" />
              <CardTitle>Automated Execution</CardTitle>
              <CardDescription>
                Lightning-fast trade execution with millisecond precision and 
                automated position management across multiple trading pairs.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  High-Frequency Trading
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Multi-Pair Monitoring
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  24/7 Operation
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/20 transition-colors">
            <CardHeader>
              <Shield className="h-12 w-12 text-primary mb-4" />
              <CardTitle>Risk Management</CardTitle>
              <CardDescription>
                Professional-grade risk controls with dynamic position sizing, 
                stop-loss automation, and portfolio protection mechanisms.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Dynamic Stop-Loss
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Position Sizing
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Portfolio Protection
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/20 transition-colors">
            <CardHeader>
              <Activity className="h-12 w-12 text-primary mb-4" />
              <CardTitle>Real-Time Analytics</CardTitle>
              <CardDescription>
                Comprehensive performance tracking with live charts, trade history, 
                and detailed analytics for informed decision making.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Live Performance Metrics
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Trade History Tracking
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Profit/Loss Analysis
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/20 transition-colors">
            <CardHeader>
              <Target className="h-12 w-12 text-primary mb-4" />
              <CardTitle>Strategy Optimization</CardTitle>
              <CardDescription>
                Adaptive trading strategies that automatically adjust to market conditions 
                and optimize performance based on historical data.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Adaptive Algorithms
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Backtesting Integration
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Performance Optimization
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/20 transition-colors">
            <CardHeader>
              <BarChart3 className="h-12 w-12 text-primary mb-4" />
              <CardTitle>Portfolio Management</CardTitle>
              <CardDescription>
                Professional portfolio management with deposit/withdrawal controls, 
                investment tracking, and transparent performance reporting.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Secure Fund Management
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Transparent Reporting
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Investment Tracking
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="text-center py-12">
            <h3 className="text-3xl font-bold mb-4">Ready to Start Trading?</h3>
            <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join our automated trading platform and let AI handle your cryptocurrency trading 
              with professional oversight and risk management.
            </p>
            <div className="flex items-center justify-center space-x-4">
              <Link to="/auth">
                <Button size="lg" className="px-8">
                  Create Investor Account
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-sm text-muted-foreground">
            <p>© 2024 Waves Quant Engine. Professional AI-powered trading automation.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;


import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import { 
  TrendingUp, 
  Brain, 
  Zap, 
  Shield, 
  BarChart3, 
  Activity,
  Users,
  Target
} from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">Waves Quant Engine</h1>
                <p className="text-sm text-muted-foreground">AI-Powered High Frequency Trading</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <ThemeToggle />
              <Button asChild>
                <Link to="/auth">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center space-y-6 max-w-4xl mx-auto">
          <Badge variant="outline" className="px-4 py-2">
            <Zap className="h-4 w-4 mr-2" />
            Next-Generation Trading Technology
          </Badge>
          
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
            AI-Powered Trading
            <span className="block text-primary">Made Simple</span>
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Experience automated cryptocurrency trading with advanced AI strategies that adapt to market conditions in real-time. Built for speed, precision, and reliability.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link to="/auth">
                <TrendingUp className="h-5 w-5 mr-2" />
                Start Trading Now
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/auth">
                <Users className="h-5 w-5 mr-2" />
                View Performance
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Why Choose Waves Quant Engine?</h2>
          <p className="text-muted-foreground">Advanced features designed for professional traders</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5 text-blue-500" />
                <span>AI-Driven Strategies</span>
              </CardTitle>
              <CardDescription>
                Unique AI strategies for each trading pair based on market conditions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Breakout strategy for trending markets</li>
                <li>• Mean reversion for ranging conditions</li>
                <li>• Scalping for high volatility</li>
                <li>• Dynamic strategy switching</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                <span>Lightning Fast Execution</span>
              </CardTitle>
              <CardDescription>
                Sub-second trade execution with real-time market data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Real-time signal generation</li>
                <li>• Automated trade execution</li>
                <li>• Live market data integration</li>
                <li>• Millisecond-level precision</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-green-500" />
                <span>Advanced Risk Management</span>
              </CardTitle>
              <CardDescription>
                Comprehensive risk controls to protect your capital
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Customizable stop-loss levels</li>
                <li>• Position size management</li>
                <li>• Daily loss limits</li>
                <li>• Portfolio diversification</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-purple-500" />
                <span>Real-Time Analytics</span>
              </CardTitle>
              <CardDescription>
                Comprehensive performance tracking and insights
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Live trading charts</li>
                <li>• Performance metrics</li>
                <li>• Trade history analysis</li>
                <li>• Profit/loss tracking</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-orange-500" />
                <span>Live Market Signals</span>
              </CardTitle>
              <CardDescription>
                Real-time buy/sell/hold signals with confidence scores
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• AI-generated signals</li>
                <li>• Confidence scoring</li>
                <li>• Signal reasoning</li>
                <li>• Historical accuracy</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5 text-red-500" />
                <span>Dual Dashboard Access</span>
              </CardTitle>
              <CardDescription>
                Separate interfaces for owners and investors
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Owner: Full control & configuration</li>
                <li>• Investor: Performance monitoring</li>
                <li>• Role-based access control</li>
                <li>• Customizable views</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-muted/30 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Trading?</h2>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join the future of automated trading with AI-powered strategies that work around the clock
          </p>
          <Button size="lg" asChild>
            <Link to="/auth">
              <TrendingUp className="h-5 w-5 mr-2" />
              Get Started Today
            </Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-6 w-6 text-primary" />
              <span className="font-semibold">Waves Quant Engine</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 Waves Quant Engine. Advanced AI Trading Technology.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;

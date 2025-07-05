
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { 
  TrendingUp, 
  Shield, 
  Users, 
  Globe, 
  Zap, 
  BarChart3,
  ArrowLeft,
  CheckCircle,
  Menu
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ThemeToggle } from "@/components/theme/theme-toggle";

export default function About() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <TrendingUp className="h-6 w-6" />,
      title: "AI-Powered Algorithms",
      description: "Our sophisticated machine learning models analyze market patterns 24/7 to identify profitable trading opportunities across all asset classes."
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Advanced Risk Management", 
      description: "Multi-layer risk controls including stop-loss automation, position sizing, and exposure limits protect your investment at all times."
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: "High-Frequency Execution",
      description: "Lightning-fast trade execution captures micro-movements in the market, maximizing profit potential while minimizing slippage."
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: "Multi-Asset Trading",
      description: "Trade across forex, cryptocurrencies, stocks, commodities, and indices from a single, unified platform."
    }
  ];

  const stats = [
    { label: "Assets Supported", value: "500+" },
    { label: "Trading Strategies", value: "12" },
    { label: "Average Win Rate", value: "84.3%" },
    { label: "Uptime", value: "99.9%" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur p-4">
        <div className="container mx-auto flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">Waves Quant Engine</span>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-4">
              <Button variant="ghost" onClick={() => navigate('/contact')}>
                Contact
              </Button>
              <Button variant="ghost" onClick={() => navigate('/terms')}>
                Terms
              </Button>
              <Button variant="ghost" onClick={() => navigate('/auth')}>
                Sign In
              </Button>
            </div>
            
            {/* Mobile Navigation */}
            <div className="md:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <Menu className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => navigate('/contact')}>
                    Contact
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/terms')}>
                    Terms
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/auth')}>
                    Sign In
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
            
            <ThemeToggle />
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <Badge variant="outline" className="mb-4">
            Professional Trading Platform
          </Badge>
          <h1 className="text-4xl lg:text-5xl font-bold mb-6">
            About Waves Quant Engine
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            We are pioneering the future of automated trading by combining institutional-grade 
            algorithms with cutting-edge technology to democratize professional trading for everyone.
          </p>
        </div>

        {/* Mission Statement */}
        <Card className="mb-16">
          <CardContent className="p-8 lg:p-12">
            <div className="grid lg:grid-cols-2 gap-8 items-center">
              <div>
                <h2 className="text-3xl font-bold mb-4">Our Mission</h2>
                <p className="text-lg text-muted-foreground mb-6">
                  To democratize institutional-grade trading technology and make sophisticated 
                  algorithmic trading accessible to individual investors worldwide.
                </p>
                <div className="space-y-3">
                  {[
                    "Transparent and automated trading",
                    "Advanced risk management",
                    "24/7 market monitoring",
                    "Professional-grade execution"
                  ].map((item, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="bg-gradient-to-br from-primary/10 to-primary/5 rounded-2xl p-8">
                <div className="grid grid-cols-2 gap-6">
                  {stats.map((stat, index) => (
                    <div key={index} className="text-center">
                      <div className="text-2xl font-bold text-primary mb-1">
                        {stat.value}
                      </div>
                      <p className="text-sm text-muted-foreground">{stat.label}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Features */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">What Sets Us Apart</h2>
            <p className="text-xl text-muted-foreground">
              Advanced technology meets professional trading expertise
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-lg text-primary">
                      {feature.icon}
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Technology Stack */}
        <Card className="mb-16">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Our Technology</CardTitle>
            <CardDescription>
              Built with cutting-edge technology for maximum performance and reliability
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 text-primary mx-auto mb-4" />
                <h3 className="font-semibold mb-2">Machine Learning</h3>
                <p className="text-muted-foreground text-sm">
                  Advanced AI algorithms that adapt and learn from market conditions
                </p>
              </div>
              <div className="text-center">
                <Zap className="h-12 w-12 text-primary mx-auto mb-4" />
                <h3 className="font-semibold mb-2">High-Performance Computing</h3>
                <p className="text-muted-foreground text-sm">
                  Ultra-low latency execution with institutional-grade infrastructure
                </p>
              </div>
              <div className="text-center">
                <Shield className="h-12 w-12 text-primary mx-auto mb-4" />
                <h3 className="font-semibold mb-2">Security First</h3>
                <p className="text-muted-foreground text-sm">
                  Bank-level security with encrypted data and secure API connections
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Call to Action */}
        <Card className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground">
          <CardContent className="p-8 lg:p-12 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Start Trading?</h2>
            <p className="text-lg mb-8 opacity-90 max-w-2xl mx-auto">
              Join thousands of investors who trust our AI-powered platform to grow their wealth 
              through professional automated trading.
            </p>
            <Button 
              size="lg" 
              variant="secondary" 
              onClick={() => navigate('/auth')}
              className="bg-background text-foreground hover:bg-background/90"
            >
              Get Started Today
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

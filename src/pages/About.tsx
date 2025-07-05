
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-lg p-4">
        <div className="container mx-auto flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate('/')} className="text-white hover:bg-white/10">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-6 w-6 text-blue-400" />
            <span className="text-xl font-bold text-white">Waves Quant Engine</span>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-4">
              <Button variant="ghost" onClick={() => navigate('/contact')} className="text-white hover:bg-white/10">
                Contact
              </Button>
              <Button variant="ghost" onClick={() => navigate('/terms')} className="text-white hover:bg-white/10">
                Terms
              </Button>
              <Button variant="ghost" onClick={() => navigate('/auth')} className="text-white hover:bg-white/10">
                Sign In
              </Button>
            </div>
            
            {/* Mobile Navigation */}
            <div className="md:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="text-white hover:bg-white/10">
                    <Menu className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="bg-slate-900/95 border-white/20">
                  <DropdownMenuItem onClick={() => navigate('/contact')} className="text-white hover:bg-white/10">
                    Contact
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/terms')} className="text-white hover:bg-white/10">
                    Terms
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/auth')} className="text-white hover:bg-white/10">
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
          <Badge variant="outline" className="mb-4 border-purple-500/20 bg-purple-600/20 text-purple-300">
            Professional Trading Platform
          </Badge>
          <h1 className="text-4xl lg:text-5xl font-bold mb-6 text-white">
            About Waves Quant Engine
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            We are pioneering the future of automated trading by combining institutional-grade 
            algorithms with cutting-edge technology to democratize professional trading for everyone.
          </p>
        </div>

        {/* Mission Statement */}
        <Card className="mb-16 bg-white/5 border-white/10 backdrop-blur-lg">
          <CardContent className="p-8 lg:p-12">
            <div className="grid lg:grid-cols-2 gap-8 items-center">
              <div>
                <h2 className="text-3xl font-bold mb-4 text-white">Our Mission</h2>
                <p className="text-lg text-gray-300 mb-6">
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
                      <CheckCircle className="h-5 w-5 text-green-400" />
                      <span className="text-white">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-2xl p-8">
                <div className="grid grid-cols-2 gap-6">
                  {stats.map((stat, index) => (
                    <div key={index} className="text-center">
                      <div className="text-2xl font-bold text-blue-400 mb-1">
                        {stat.value}
                      </div>
                      <p className="text-sm text-gray-300">{stat.label}</p>
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
            <h2 className="text-3xl font-bold mb-4 text-white">What Sets Us Apart</h2>
            <p className="text-xl text-gray-300">
              Advanced technology meets professional trading expertise
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="bg-white/5 border-white/10 backdrop-blur-lg">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-600/20 rounded-lg text-blue-400">
                      {feature.icon}
                    </div>
                    <CardTitle className="text-xl text-white">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base text-gray-300">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Technology Stack */}
        <Card className="mb-16 bg-white/5 border-white/10 backdrop-blur-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-white">Our Technology</CardTitle>
            <CardDescription className="text-gray-300">
              Built with cutting-edge technology for maximum performance and reliability
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 text-blue-400 mx-auto mb-4" />
                <h3 className="font-semibold mb-2 text-white">Machine Learning</h3>
                <p className="text-gray-300 text-sm">
                  Advanced AI algorithms that adapt and learn from market conditions
                </p>
              </div>
              <div className="text-center">
                <Zap className="h-12 w-12 text-blue-400 mx-auto mb-4" />
                <h3 className="font-semibold mb-2 text-white">High-Performance Computing</h3>
                <p className="text-gray-300 text-sm">
                  Ultra-low latency execution with institutional-grade infrastructure
                </p>
              </div>
              <div className="text-center">
                <Shield className="h-12 w-12 text-blue-400 mx-auto mb-4" />
                <h3 className="font-semibold mb-2 text-white">Security First</h3>
                <p className="text-gray-300 text-sm">
                  Bank-level security with encrypted data and secure API connections
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Call to Action */}
        <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
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
              className="bg-white text-slate-900 hover:bg-gray-100"
            >
              Get Started Today
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  BarChart3, 
  TrendingUp, 
  Shield, 
  Zap, 
  Brain, 
  Target,
  ArrowRight,
  CheckCircle,
  Star,
  Users,
  DollarSign,
  Activity
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

const Index = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalUsers: 2847,
    totalTrades: 156429,
    successRate: 87.3,
    totalProfit: 2847592
  });

  useEffect(() => {
    // Simulate real-time stats updates
    const interval = setInterval(() => {
      setStats(prev => ({
        totalUsers: prev.totalUsers + Math.floor(Math.random() * 3),
        totalTrades: prev.totalTrades + Math.floor(Math.random() * 50),
        successRate: Math.max(85, Math.min(90, prev.successRate + (Math.random() - 0.5) * 0.5)),
        totalProfit: prev.totalProfit + Math.floor(Math.random() * 1000)
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen">
      {/* Hero Section with Background Image */}
      <div 
        className="relative min-h-screen bg-gradient-to-br from-blue-600 via-purple-700 to-indigo-800 overflow-hidden"
        style={{
          backgroundImage: `url('/assets/landing_background/landing_background_1.png'), linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #4F46E5 100%)`,
          backgroundSize: 'cover, cover',
          backgroundPosition: 'center, center',
          backgroundBlendMode: 'overlay, normal'
        }}
      >
        {/* Animated background elements */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-400/20 rounded-full blur-3xl animate-pulse delay-500"></div>
        </div>

        {/* Header */}
        <div className="relative z-10 border-b border-white/10 bg-white/5 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-white" />
                <span className="text-2xl font-bold text-white">Waves Quant Engine</span>
              </div>
              <div className="flex items-center space-x-6">
                <div className="hidden md:flex items-center space-x-6">
                  <Link to="/about" className="text-white/80 hover:text-white transition-colors">About</Link>
                  <Link to="/contact" className="text-white/80 hover:text-white transition-colors">Contact</Link>
                  <Link to="/terms" className="text-white/80 hover:text-white transition-colors">Terms</Link>
                </div>
                {user ? (
                  <Button onClick={() => navigate('/investor')}>
                    Go to Dashboard
                  </Button>
                ) : (
                  <Button onClick={() => navigate('/auth')} variant="secondary">
                    Sign In
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 flex items-center min-h-[calc(100vh-80px)]">
          <div className="container mx-auto px-4 py-20">
            <div className="text-center text-white">
              <Badge variant="secondary" className="mb-6 bg-white/10 text-white border-white/20">
                <Zap className="h-4 w-4 mr-2" />
                AI-Powered Trading Platform
              </Badge>
              
              <h1 className="text-5xl md:text-7xl font-bold mb-8 leading-tight">
                Trade Smarter with
                <span className="block bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                  AI Precision
                </span>
              </h1>
              
              <p className="text-xl md:text-2xl mb-12 text-white/90 max-w-3xl mx-auto leading-relaxed">
                Experience the future of trading with our advanced AI algorithms that analyze market patterns, 
                execute precise trades, and maximize your investment potential 24/7.
              </p>

              {/* Live Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12 max-w-4xl mx-auto">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                  <div className="flex items-center justify-center mb-2">
                    <Users className="h-5 w-5 text-blue-300" />
                  </div>
                  <div className="text-2xl font-bold">{stats.totalUsers.toLocaleString()}</div>
                  <div className="text-sm text-white/70">Active Traders</div>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                  <div className="flex items-center justify-center mb-2">
                    <Activity className="h-5 w-5 text-green-300" />
                  </div>
                  <div className="text-2xl font-bold">{stats.totalTrades.toLocaleString()}</div>
                  <div className="text-sm text-white/70">Trades Executed</div>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                  <div className="flex items-center justify-center mb-2">
                    <Target className="h-5 w-5 text-purple-300" />
                  </div>
                  <div className="text-2xl font-bold">{stats.successRate.toFixed(1)}%</div>
                  <div className="text-sm text-white/70">Success Rate</div>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                  <div className="flex items-center justify-center mb-2">
                    <DollarSign className="h-5 w-5 text-yellow-300" />
                  </div>
                  <div className="text-2xl font-bold">${(stats.totalProfit / 1000000).toFixed(1)}M</div>
                  <div className="text-sm text-white/70">Total Profits</div>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-6 justify-center">
                <Button 
                  size="lg" 
                  onClick={() => navigate('/auth')}
                  className="bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                >
                  Start Trading Now
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button 
                  size="lg" 
                  variant="outline"
                  onClick={() => navigate('/about')}
                  className="border-white/20 text-white hover:bg-white/10 backdrop-blur-sm"
                >
                  Learn More
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge variant="outline" className="mb-4">
              Why Choose Waves Quant Engine
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Advanced Trading Features
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Our AI-powered platform combines cutting-edge technology with sophisticated trading strategies
              to deliver consistent results in any market condition.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Brain,
                title: "AI-Powered Analysis",
                description: "Advanced machine learning algorithms analyze thousands of market indicators in real-time.",
                color: "blue"
              },
              {
                icon: TrendingUp,
                title: "Consistent Performance",
                description: "Proven track record of delivering superior risk-adjusted returns across market cycles.",
                color: "green"
              },
              {
                icon: Shield,
                title: "Risk Management",
                description: "Sophisticated risk controls and portfolio protection mechanisms safeguard your investments.",
                color: "red"
              },
              {
                icon: Zap,
                title: "Lightning Fast",
                description: "Ultra-low latency execution ensures you never miss profitable market opportunities.",
                color: "yellow"
              },
              {
                icon: BarChart3,
                title: "Real-Time Analytics",
                description: "Comprehensive dashboards and detailed performance analytics at your fingertips.",
                color: "purple"
              },
              {
                icon: Target,
                title: "Multi-Asset Trading",
                description: "Trade across forex, commodities, indices, and cryptocurrencies from one platform.",
                color: "indigo"
              }
            ].map((feature, index) => (
              <Card key={index} className="group hover:shadow-lg transition-all duration-300 border-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <div className={`p-3 rounded-lg w-fit bg-${feature.color}-100 dark:bg-${feature.color}-900/20 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className={`h-6 w-6 text-${feature.color}-600`} />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
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
      </div>

      {/* Testimonials Section */}
      <div className="py-20 bg-gradient-to-r from-blue-600 to-purple-700">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-6">
              What Our Traders Say
            </h2>
            <p className="text-xl text-white/90 max-w-2xl mx-auto">
              Join thousands of successful traders who trust Waves Quant Engine with their investments.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                name: "Sarah Johnson",
                role: "Professional Trader",
                content: "The AI algorithms have consistently outperformed my manual trading strategies. I've seen a 340% increase in my portfolio value.",
                rating: 5
              },
              {
                name: "Michael Chen",
                role: "Investment Manager",
                content: "Waves Quant Engine has revolutionized how I approach trading. The risk management features give me peace of mind.",
                rating: 5
              },
              {
                name: "Emma Rodriguez",
                role: "Retail Investor",
                content: "As a beginner, this platform made sophisticated trading strategies accessible to me. The results speak for themselves.",
                rating: 5
              }
            ].map((testimonial, index) => (
              <Card key={index} className="bg-white/10 backdrop-blur-sm border-white/20 text-white">
                <CardContent className="p-6">
                  <div className="flex mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="mb-6 text-white/90 italic">"{testimonial.content}"</p>
                  <div>
                    <div className="font-semibold">{testimonial.name}</div>
                    <div className="text-sm text-white/70">{testimonial.role}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-gradient-to-br from-gray-900 to-black text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-8">
            Ready to Transform Your Trading?
          </h2>
          <p className="text-xl mb-12 text-gray-300 max-w-2xl mx-auto">
            Join the revolution in AI-powered trading and start maximizing your investment potential today.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
            <Button 
              size="lg" 
              onClick={() => navigate('/auth')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              Get Started Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={() => navigate('/contact')}
              className="border-white/20 text-white hover:bg-white/10"
            >
              Contact Sales
            </Button>
          </div>

          <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <span>No Hidden Fees</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <span>24/7 Support</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <span>Secure & Regulated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t bg-gray-50 dark:bg-gray-900 py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Brain className="h-6 w-6 text-primary" />
              <span className="font-bold">Waves Quant Engine</span>
            </div>
            <div className="flex items-center space-x-6 text-sm text-muted-foreground">
              <Link to="/about" className="hover:text-primary transition-colors">About</Link>
              <Link to="/contact" className="hover:text-primary transition-colors">Contact</Link>
              <Link to="/terms" className="hover:text-primary transition-colors">Terms</Link>
              <span>© 2024 Waves Quant Engine. All rights reserved.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;

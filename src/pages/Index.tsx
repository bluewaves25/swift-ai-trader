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
  Activity,
  MessageCircle,
  Send
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { SupportChat } from "@/components/support/SupportChat";

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
    <div className="min-h-screen dark">
      {/* Hero Section with Background Image */}
      <div 
        className="relative min-h-screen overflow-hidden"
        style={{
          backgroundImage: `linear-gradient(135deg, rgba(59, 130, 246, 0.85) 0%, rgba(139, 92, 246, 0.85) 50%, rgba(79, 70, 229, 0.85) 100%), url('/landing_background_1.png')`,
          backgroundSize: 'cover, cover',
          backgroundPosition: 'center, center',
          backgroundBlendMode: 'overlay, normal'
        }}
      >
        {/* Dark overlay for text clarity */}
        <div className="absolute inset-0 z-0 pointer-events-none">
          <div
            className="w-full h-full"
            style={{
              background: 'rgba(20, 20, 30, 0.45)'
            }}
          />
        </div>

        {/* Animated background elements */}
        <div className="absolute inset-0 z-10 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-400/20 rounded-full blur-3xl animate-pulse delay-500"></div>
        </div>

        {/* Header - Sticky with glassmorphism */}
        <div className="sticky top-0 z-20 border-b border-white/10 bg-white/10 backdrop-blur-xl supports-[backdrop-filter]:bg-white/5">
          <div className="container mx-auto px-2 md:px-4 py-2 md:py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Brain className="h-6 w-6 md:h-8 md:w-8 text-white" />
                <span className="text-lg md:text-2xl font-bold text-white drop-shadow-[0_2px_8px_rgba(0,0,0,0.8)]">Waves Quant Engine</span>
              </div>
              <div className="flex items-center space-x-2 md:space-x-6">
                <div className="hidden md:flex items-center space-x-6">
                  <Link to="/about" className="text-white/90 hover:text-white transition-colors font-medium text-sm">About</Link>
                  <Link to="/contact" className="text-white/90 hover:text-white transition-colors font-medium text-sm">Contact</Link>
                  <Link to="/terms" className="text-white/90 hover:text-white transition-colors font-medium text-sm">Terms</Link>
                </div>
                <Button 
                  onClick={() => navigate('/auth')} 
                  size="sm"
                  className="bg-white/90 text-blue-600 hover:bg-white font-semibold text-xs md:text-sm"
                >
                  Sign In
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Hero Content */}
        <div className="relative z-20 flex items-center min-h-[calc(100vh-80px)]">
          <div className="container mx-auto px-2 md:px-4 py-8 md:py-20">
            <div className="text-center text-white">
              <Badge variant="secondary" className="mb-3 md:mb-6 bg-white/20 text-white border-white/30 backdrop-blur-sm drop-shadow-lg text-xs md:text-sm">
                <Zap className="h-3 w-3 md:h-4 md:w-4 mr-1 md:mr-2" />
                AI-Powered Trading Platform
              </Badge>
              
              <h1 className="text-3xl md:text-5xl lg:text-7xl font-bold mb-4 md:mb-8 leading-tight text-white drop-shadow-[0_4px_16px_rgba(0,0,0,0.9)]">
                <span className="text-white drop-shadow-[0_4px_16px_rgba(0,0,0,0.9)]">Trade Smarter with</span>
                <span className="block bg-gradient-to-r from-yellow-300 via-orange-400 to-red-400 bg-clip-text text-transparent drop-shadow-[0_4px_16px_rgba(0,0,0,0.9)]">
                  AI Precision
                </span>
              </h1>
              
              <p className="text-sm md:text-xl lg:text-2xl mb-6 md:mb-12 text-white/95 max-w-3xl mx-auto leading-relaxed font-semibold drop-shadow-[0_2px_8px_rgba(0,0,0,0.8)]">
                Experience the future of trading with our advanced AI algorithms that analyze market patterns, 
                execute precise trades, and maximize your investment potential 24/7.
              </p>

              {/* Live Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-6 mb-6 md:mb-12 max-w-4xl mx-auto">
                <div className="bg-white/15 backdrop-blur-md rounded-xl p-2 md:p-4 border border-white/20">
                  <div className="flex items-center justify-center mb-1 md:mb-2">
                    <Users className="h-3 w-3 md:h-5 md:w-5 text-blue-300" />
                  </div>
                  <div className="text-lg md:text-2xl font-bold text-white">{stats.totalUsers.toLocaleString()}</div>
                  <div className="text-xs md:text-sm text-white/80 font-medium">Active Traders</div>
                </div>
                <div className="bg-white/15 backdrop-blur-md rounded-xl p-2 md:p-4 border border-white/20">
                  <div className="flex items-center justify-center mb-1 md:mb-2">
                    <Activity className="h-3 w-3 md:h-5 md:w-5 text-green-300" />
                  </div>
                  <div className="text-lg md:text-2xl font-bold text-white">{stats.totalTrades.toLocaleString()}</div>
                  <div className="text-xs md:text-sm text-white/80 font-medium">Trades Executed</div>
                </div>
                <div className="bg-white/15 backdrop-blur-md rounded-xl p-2 md:p-4 border border-white/20">
                  <div className="flex items-center justify-center mb-1 md:mb-2">
                    <Target className="h-3 w-3 md:h-5 md:w-5 text-purple-300" />
                  </div>
                  <div className="text-lg md:text-2xl font-bold text-white">{stats.successRate.toFixed(1)}%</div>
                  <div className="text-xs md:text-sm text-white/80 font-medium">Success Rate</div>
                </div>
                <div className="bg-white/15 backdrop-blur-md rounded-xl p-2 md:p-4 border border-white/20">
                  <div className="flex items-center justify-center mb-1 md:mb-2">
                    <DollarSign className="h-3 w-3 md:h-5 md:w-5 text-yellow-300" />
                  </div>
                  <div className="text-lg md:text-2xl font-bold text-white">${(stats.totalProfit / 1000000).toFixed(1)}M</div>
                  <div className="text-xs md:text-sm text-white/80 font-medium">Total Profits</div>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-3 md:gap-6 justify-center">
                <Button 
                  size="lg" 
                  onClick={() => navigate('/auth')}
                  className="bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 font-semibold text-sm md:text-base"
                >
                  Start Trading Now
                  <ArrowRight className="ml-1 md:ml-2 h-3 w-3 md:h-5 md:w-5" />
                </Button>
                <Button 
                  size="lg" 
                  variant="outline"
                  onClick={() => navigate('/about')}
                  className="border-white/40 text-white hover:bg-white/15 backdrop-blur-sm bg-white/10 font-semibold text-sm md:text-base"
                >
                  Learn More
                </Button>
                <Button 
                  size="lg" 
                  variant="secondary"
                  onClick={() => navigate('/investor-dashboard?section=subscription')}
                  className="bg-white/80 text-blue-700 border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 font-semibold text-sm md:text-base"
                >
                  View Plans & Start Free Trial
                  <Star className="ml-1 md:ml-2 h-3 w-3 md:h-5 md:w-5 text-yellow-500" />
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
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold"
            >
              Get Started Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={() => navigate('/contact')}
              className="border-white/30 text-white hover:bg-white/10 font-semibold"
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

      {/* Revenue Features Section */}
      <div className="py-20 bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge variant="outline" className="mb-4">
              Unlock More with Premium
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Revenue Features for Every Investor
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Waves Quant Engine offers a full suite of revenue-generating features for both individual and institutional investors.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="group hover:shadow-lg transition-all duration-300 border-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <div className="p-3 rounded-lg w-fit bg-yellow-100 dark:bg-yellow-900/20 group-hover:scale-110 transition-transform duration-300">
                  <Star className="h-6 w-6 text-yellow-600" />
                </div>
                <CardTitle className="text-xl">Subscription Plans</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Flexible monthly and annual plans for every trader. Start with a free trial and unlock premium analytics, signals, and more.
                </CardDescription>
                <Button size="sm" className="mt-3" onClick={() => navigate('/investor-dashboard?section=subscription')}>See Plans</Button>
              </CardContent>
            </Card>
            <Card className="group hover:shadow-lg transition-all duration-300 border-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <div className="p-3 rounded-lg w-fit bg-green-100 dark:bg-green-900/20 group-hover:scale-110 transition-transform duration-300">
                  <DollarSign className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle className="text-xl">Performance Fees</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Only pay when you profit. Our transparent performance fee model aligns our success with yours.
                </CardDescription>
                <Button size="sm" className="mt-3" onClick={() => navigate('/investor-dashboard?section=fees')}>Learn More</Button>
              </CardContent>
            </Card>
            <Card className="group hover:shadow-lg transition-all duration-300 border-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <div className="p-3 rounded-lg w-fit bg-indigo-100 dark:bg-indigo-900/20 group-hover:scale-110 transition-transform duration-300">
                  <Brain className="h-6 w-6 text-indigo-600" />
                </div>
                <CardTitle className="text-xl">AI Strategy Marketplace</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Buy, sell, and rate trading strategies. Earn revenue as a creator or discover top-performing AI strategies.
                </CardDescription>
                <Button size="sm" className="mt-3" onClick={() => navigate('/investor-dashboard?section=marketplace')}>Explore Marketplace</Button>
              </CardContent>
            </Card>
            <Card className="group hover:shadow-lg transition-all duration-300 border-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <div className="p-3 rounded-lg w-fit bg-pink-100 dark:bg-pink-900/20 group-hover:scale-110 transition-transform duration-300">
                  <Users className="h-6 w-6 text-pink-600" />
                </div>
                <CardTitle className="text-xl">Affiliate Program</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Share your referral link, grow the community, and earn commissions for every new subscriber you bring.
                </CardDescription>
                <Button size="sm" className="mt-3" onClick={() => navigate('/investor-dashboard?section=affiliate')}>Affiliate Dashboard</Button>
              </CardContent>
            </Card>
            <Card className="group hover:shadow-lg transition-all duration-300 border-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <div className="p-3 rounded-lg w-fit bg-purple-100 dark:bg-purple-900/20 group-hover:scale-110 transition-transform duration-300">
                  <BarChart3 className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle className="text-xl">Premium Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Access real-time analytics, advanced dashboards, and actionable insights to maximize your trading performance.
                </CardDescription>
                <Button size="sm" className="mt-3" onClick={() => navigate('/investor-dashboard?section=overview')}>See Analytics</Button>
              </CardContent>
            </Card>
            <Card className="group hover:shadow-lg transition-all duration-300 border-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <div className="p-3 rounded-lg w-fit bg-gray-100 dark:bg-gray-900/20 group-hover:scale-110 transition-transform duration-300">
                  <Target className="h-6 w-6 text-gray-600" />
                </div>
                <CardTitle className="text-xl">B2B & White-Label</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Financial advisors, trading groups, and fintechs can license our platform or request custom integrations.
                </CardDescription>
                <Button size="sm" className="mt-3" onClick={() => navigate('/contact')}>Contact Sales</Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t bg-gray-50 dark:bg-gray-900 py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Brain className="h-6 w-6 text-primary" />
              <span className="font-bold text-gray-200">Waves Quant Engine</span>
            </div>
            <div className="flex items-center space-x-6 text-sm text-muted-foreground mb-4 md:mb-0">
              <Link to="/about" className="hover:text-primary transition-colors">About</Link>
              <Link to="/contact" className="hover:text-primary transition-colors">Contact</Link>
              <Link to="/terms" className="hover:text-primary transition-colors">Terms</Link>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">Join Community:</span>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <svg className="h-4 w-4 text-gray-200" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MessageCircle className="h-4 w-4 text-gray-200" />
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <Send className="h-4 w-4 text-gray-200" />
              </Button>
            </div>
          </div>
          <div className="text-center text-xs text-muted-foreground mt-4">
            © 2025 Waves Quant Engine. All rights reserved.
          </div>
        </div>
      </div>
      <SupportChat />
    </div>
  );
};

export default Index;

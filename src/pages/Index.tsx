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
    <div className="dark min-h-screen bg-white dark:bg-gray-900">
      {/* New Header */}
      <header className="sticky top-0 z-30 w-full flex justify-center items-center pt-6">
        <nav className="flex items-center justify-between p-2 space-x-8 bg-white/80 dark:bg-gray-800/60 backdrop-blur-md rounded-full border border-gray-200 dark:border-gray-700 shadow-sm">
          <Link to="/" className="flex items-center space-x-2 pl-4">
            <Brain className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              Waves Quant
            </span>
          </Link>
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/about" className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary">About</Link>
            <Link to="/contact" className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary">Contact</Link>
            <Link to="/terms" className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary">Terms</Link>
          </div>
          <Button 
            onClick={() => navigate('/auth')} 
            className="rounded-full bg-gray-900 text-white dark:bg-black dark:text-white hover:bg-gray-800 dark:hover:bg-gray-700 px-5 py-2 text-sm font-semibold"
          >
            Sign In
          </Button>
        </nav>
      </header>
      
      {/* Hero Section */}
      <div 
        className="relative -mt-20 pt-20 min-h-screen overflow-hidden flex items-center justify-center text-center bg-cover bg-center"
        style={{ backgroundImage: "url('/landing_background_1.png')" }}
      >
        <div className="absolute inset-0 bg-white/70 dark:bg-gray-900/80 z-0"></div>

        <div className="relative z-10 px-4">
          <Badge variant="outline" className="mb-6 rounded-full border-gray-300 dark:border-gray-600 bg-white/50 dark:bg-gray-800/50">
            <Zap className="h-4 w-4 mr-2" />
            AI-POWERED TRADING PLATFORM
          </Badge>
          
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white tracking-tighter mb-4">
            Empower Your Trades with
            <br />
            <span className="text-primary">Next-Gen AI Engine</span>
          </h1>
          
          <p className="max-w-2xl text-lg text-gray-600 dark:text-gray-400 mb-8 mx-auto">
            Unlock seamless trading and streamline your portfolio with our innovative AI-driven solution. 
            Experience the future of automated, intelligent investing.
          </p>
          
          {/* Live Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 max-w-2xl mx-auto">
            {[
              { icon: Users, label: "Active Traders", value: stats.totalUsers.toLocaleString(), color: "text-blue-500" },
              { icon: Activity, label: "Trades Executed", value: stats.totalTrades.toLocaleString(), color: "text-green-500" },
              { icon: Target, label: "Success Rate", value: `${stats.successRate.toFixed(1)}%`, color: "text-purple-500" },
              { icon: DollarSign, label: "Total Profits", value: `$${(stats.totalProfit / 1000000).toFixed(1)}M`, color: "text-yellow-500" },
            ].map((stat, index) => (
              <div key={index} className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
                <stat.icon className={`h-6 w-6 mb-2 mx-auto ${stat.color}`} />
                <div className="text-xl font-bold text-gray-900 dark:text-white">{stat.value}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => navigate('/auth')} className="rounded-full px-8 py-6 text-base font-bold">
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate('/about')} className="rounded-full px-8 py-6 text-base font-bold">
              Learn More
            </Button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge variant="outline" className="mb-4 rounded-full border-gray-300 dark:border-gray-600">
              Why Choose Our Engine
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Advanced Trading Features
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Our AI-powered platform combines cutting-edge technology with sophisticated trading strategies
              to deliver consistent results in any market condition.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: Brain, title: "AI-Powered Analysis", description: "Advanced machine learning algorithms analyze thousands of market indicators in real-time.", color: "blue" },
              { icon: TrendingUp, title: "Consistent Performance", description: "Proven track record of delivering superior risk-adjusted returns across market cycles.", color: "green" },
              { icon: Shield, title: "Risk Management", description: "Sophisticated risk controls and portfolio protection mechanisms safeguard your investments.", color: "red" },
              { icon: Zap, title: "Lightning Fast", description: "Ultra-low latency execution ensures you never miss profitable market opportunities.", color: "yellow" },
              { icon: BarChart3, title: "Real-Time Analytics", description: "Comprehensive dashboards and detailed performance analytics at your fingertips.", color: "purple" },
              { icon: Target, title: "Multi-Asset Trading", description: "Trade across forex, commodities, indices, and cryptocurrencies from one platform.", color: "indigo" }
            ].map((feature, index) => (
              <Card key={index} className="bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className={`p-3 rounded-lg w-fit bg-${feature.color}-100 dark:bg-${feature.color}-900/30 mb-4`}>
                    <feature.icon className={`h-6 w-6 text-${feature.color}-600 dark:text-${feature.color}-400`} />
                  </div>
                  <CardTitle className="text-xl font-bold text-gray-900 dark:text-white">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base text-gray-600 dark:text-gray-400">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div className="py-20 bg-gray-50 dark:bg-gray-800/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              What Our Traders Say
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Join thousands of successful traders who trust our engine with their investments.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { name: "Sarah Johnson", role: "Professional Trader", content: "The AI algorithms have consistently outperformed my manual trading strategies. I've seen a 340% increase in my portfolio value.", rating: 5 },
              { name: "Michael Chen", role: "Investment Manager", content: "This engine has revolutionized how I approach trading. The risk management features give me peace of mind.", rating: 5 },
              { name: "Emma Rodriguez", role: "Retail Investor", content: "As a beginner, this platform made sophisticated trading strategies accessible to me. The results speak for themselves.", rating: 5 }
            ].map((testimonial, index) => (
              <Card key={index} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm">
                <CardContent className="p-6">
                  <div className="flex mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="mb-6 text-gray-700 dark:text-gray-300 italic">"{testimonial.content}"</p>
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">{testimonial.name}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{testimonial.role}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Ready to Transform Your Trading?
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-8">
            Join the revolution in AI-powered trading and start maximizing your investment potential today.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Button size="lg" onClick={() => navigate('/auth')} className="rounded-full px-8 py-6 text-base font-bold">
              Get Started Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate('/contact')} className="rounded-full px-8 py-6 text-base font-bold">
              Contact Sales
            </Button>
          </div>

          <div className="flex flex-wrap justify-center items-center gap-6 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>No Hidden Fees</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>24/7 Support</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Secure & Regulated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Partners/Social Proof Section */}
      <div className="w-full py-12 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <p className="text-center text-sm font-semibold text-gray-500 dark:text-gray-400 mb-6">
            TRUSTED BY INDUSTRY LEADERS
          </p>
          <div className="flex justify-center items-center space-x-8 md:space-x-12 opacity-70">
              <p className="text-2xl font-bold text-gray-500">Amazon</p>
              <p className="text-2xl font-bold text-gray-500">Atlassian</p>
              <p className="text-2xl font-bold text-gray-500">GitHub</p>
              <p className="text-2xl font-bold text-gray-500">Netflix</p>
              <p className="text-2xl font-bold text-gray-500">Medium</p>
          </div>
        </div>
      </div>
      
      {/* Revenue Features Section */}
      <div className="py-20 bg-gray-50 dark:bg-gray-800/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge variant="outline" className="mb-4 rounded-full border-gray-300 dark:border-gray-600">
              Unlock More with Premium
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Revenue Features for Every Investor
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Our platform offers a full suite of revenue-generating features for both individual and institutional investors.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: Star, title: "Subscription Plans", description: "Flexible monthly and annual plans for every trader. Start with a free trial and unlock premium analytics, signals, and more.", link: "/investor-dashboard?section=subscription", cta: "See Plans", color: "yellow" },
              { icon: DollarSign, title: "Performance Fees", description: "Only pay when you profit. Our transparent performance fee model aligns our success with yours.", link: "/investor-dashboard?section=fees", cta: "Learn More", color: "green" },
              { icon: Brain, title: "AI Strategy Marketplace", description: "Buy, sell, and rate trading strategies. Earn revenue as a creator or discover top-performing AI strategies.", link: "/investor-dashboard?section=marketplace", cta: "Explore Marketplace", color: "indigo" },
              { icon: Users, title: "Affiliate Program", description: "Share your referral link, grow the community, and earn commissions for every new subscriber you bring.", link: "/investor-dashboard?section=affiliate", cta: "Affiliate Dashboard", color: "pink" },
              { icon: BarChart3, title: "Premium Analytics", description: "Access real-time analytics, advanced dashboards, and actionable insights to maximize your trading performance.", link: "/investor-dashboard?section=overview", cta: "See Analytics", color: "purple" },
              { icon: Target, title: "B2B & White-Label", description: "Financial advisors, trading groups, and fintechs can license our platform or request custom integrations.", link: "/contact", cta: "Contact Sales", color: "gray" },
            ].map((feature, index) => (
              <Card key={index} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm hover:shadow-lg transition-shadow flex flex-col">
                <CardHeader>
                  <div className={`p-3 rounded-lg w-fit bg-${feature.color}-100 dark:bg-${feature.color}-900/30 mb-4`}>
                    <feature.icon className={`h-6 w-6 text-${feature.color}-600 dark:text-${feature.color}-400`} />
                  </div>
                  <CardTitle className="text-xl font-bold text-gray-900 dark:text-white">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent className="flex-grow">
                  <CardDescription className="text-base text-gray-600 dark:text-gray-400">
                    {feature.description}
                  </CardDescription>
                </CardContent>
                <div className="p-6 pt-0">
                  <Button variant="outline" size="sm" className="w-full" onClick={() => navigate(feature.link)}>{feature.cta}</Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t bg-white dark:bg-gray-900 py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center text-center md:text-left">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Brain className="h-6 w-6 text-primary" />
              <span className="font-bold text-gray-800 dark:text-gray-200">Waves Quant Engine</span>
            </div>
            <div className="flex items-center space-x-6 text-sm text-gray-600 dark:text-gray-400 mb-4 md:mb-0">
              <Link to="/about" className="hover:text-primary transition-colors">About</Link>
              <Link to="/contact" className="hover:text-primary transition-colors">Contact</Link>
              <Link to="/terms" className="hover:text-primary transition-colors">Terms</Link>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <svg className="h-4 w-4 text-gray-600 dark:text-gray-400" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MessageCircle className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Send className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              </Button>
            </div>
          </div>
          <div className="text-center text-xs text-gray-500 dark:text-gray-400 mt-6">
            © 2025 Waves Quant Engine. All rights reserved.
          </div>
        </div>
      </footer>
      <SupportChat />
    </div>
  );
};

export default Index;

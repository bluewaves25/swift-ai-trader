
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { 
  TrendingUp, 
  Shield, 
  Zap, 
  Globe, 
  BarChart3, 
  Users,
  ChevronRight,
  Star,
  CheckCircle,
  ArrowRight
} from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";

const Index = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeFeature, setActiveFeature] = useState(0);

  const features = [
    {
      icon: <TrendingUp className="h-6 w-6" />,
      title: "AI-Powered Trading",
      description: "Advanced algorithms analyze market conditions 24/7 to execute profitable trades across all asset classes."
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Risk Management",
      description: "Sophisticated risk controls protect your investment with stop-loss, position sizing, and exposure limits."
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: "High-Frequency Trading",
      description: "Lightning-fast execution captures micro-movements in forex, crypto, stocks, and commodities markets."
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: "Multi-Asset Support",
      description: "Trade across forex, cryptocurrencies, stocks, commodities, and indices from a single platform."
    }
  ];

  const stats = [
    { label: "Assets Supported", value: "500+", icon: <Globe className="h-5 w-5" /> },
    { label: "Active Strategies", value: "12", icon: <BarChart3 className="h-5 w-5" /> },
    { label: "Avg Monthly Return", value: "8.5%", icon: <TrendingUp className="h-5 w-5" /> },
    { label: "Investor Protection", value: "100%", icon: <Shield className="h-5 w-5" /> }
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Portfolio Manager",
      content: "Waves Quant Engine has revolutionized my trading approach. The AI strategies consistently outperform the market.",
      rating: 5
    },
    {
      name: "Michael Rodriguez",
      role: "Retail Investor", 
      content: "Finally, institutional-grade trading technology accessible to individual investors. Incredible results!",
      rating: 5
    },
    {
      name: "Dr. James Liu",
      role: "Hedge Fund Manager",
      content: "The risk management and multi-asset capabilities are outstanding. This is the future of automated trading.",
      rating: 5
    }
  ];

  const handleGetStarted = () => {
    if (user) {
      navigate(user.user_metadata?.role === 'owner' ? '/owner-dashboard' : '/investor-dashboard');
    } else {
      navigate('/auth');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">Waves Quant Engine</span>
          </div>
          
          <nav className="hidden md:flex items-center space-x-6">
            <a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">How It Works</a>
            <a href="#testimonials" className="text-muted-foreground hover:text-foreground transition-colors">Testimonials</a>
            <a href="#contact" className="text-muted-foreground hover:text-foreground transition-colors">Contact</a>
          </nav>

          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <Button onClick={handleGetStarted} className="bg-primary hover:bg-primary/90">
              {user ? 'Dashboard' : 'Get Started'}
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="outline" className="mb-4">
              <Star className="h-3 w-3 mr-1" />
              AI-Powered Trading Platform
            </Badge>
            
            <h1 className="text-4xl lg:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              Professional Trading.
              <br />
              Automated Excellence.
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Harness the power of institutional-grade AI trading algorithms. Trade forex, crypto, stocks, and commodities with advanced risk management and 24/7 automation.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button size="lg" onClick={handleGetStarted} className="bg-primary hover:bg-primary/90">
                Start Trading Now
                <ChevronRight className="h-5 w-5 ml-2" />
              </Button>
              <Button size="lg" variant="outline" onClick={() => document.getElementById('features')?.scrollIntoView()}>
                Learn More
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
              {stats.map((stat, index) => (
                <Card key={index} className="text-center">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-center mb-2 text-primary">
                      {stat.icon}
                    </div>
                    <div className="text-2xl font-bold mb-1">{stat.value}</div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
        
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-3xl"></div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need for professional automated trading
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              {features.map((feature, index) => (
                <Card 
                  key={index}
                  className={`cursor-pointer transition-all duration-300 ${
                    activeFeature === index ? 'border-primary shadow-lg' : 'hover:shadow-md'
                  }`}
                  onClick={() => setActiveFeature(index)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      <div className={`p-2 rounded-lg ${
                        activeFeature === index ? 'bg-primary text-primary-foreground' : 'bg-muted'
                      }`}>
                        {feature.icon}
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                        <p className="text-muted-foreground">{feature.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="bg-gradient-to-br from-primary/10 to-primary/5 rounded-2xl p-8 lg:p-12">
              <div className="space-y-6">
                <h3 className="text-2xl font-bold">Real-Time Performance</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Win Rate</span>
                    <span className="font-semibold">84.3%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-primary rounded-full h-2" style={{width: '84.3%'}}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Profit Factor</span>
                    <span className="font-semibold">2.34</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-green-500 rounded-full h-2" style={{width: '70%'}}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Max Drawdown</span>
                    <span className="font-semibold">3.2%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-orange-500 rounded-full h-2" style={{width: '15%'}}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-xl text-muted-foreground">Simple steps to start automated trading</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Create Account",
                description: "Sign up and complete your investor profile to get started with automated trading."
              },
              {
                step: "02", 
                title: "Deposit Funds",
                description: "Securely deposit funds directly to your Exness trading account through our platform."
              },
              {
                step: "03",
                title: "Watch & Profit",
                description: "Our AI algorithms trade 24/7 while you monitor performance and withdraw profits."
              }
            ].map((item, index) => (
              <Card key={index} className="text-center relative">
                <CardContent className="p-8">
                  <div className="text-4xl font-bold text-primary mb-4">{item.step}</div>
                  <h3 className="text-xl font-semibold mb-4">{item.title}</h3>
                  <p className="text-muted-foreground">{item.description}</p>
                </CardContent>
                {index < 2 && (
                  <ChevronRight className="hidden md:block absolute -right-4 top-1/2 -translate-y-1/2 h-8 w-8 text-muted-foreground" />
                )}
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">What Our Investors Say</h2>
            <p className="text-xl text-muted-foreground">Trusted by professionals worldwide</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index}>
                <CardContent className="p-6">
                  <div className="flex mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 fill-primary text-primary" />
                    ))}
                  </div>
                  <p className="text-muted-foreground mb-4">"{testimonial.content}"</p>
                  <div>
                    <div className="font-semibold">{testimonial.name}</div>
                    <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <Card className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground">
            <CardContent className="p-12 text-center">
              <h2 className="text-3xl lg:text-4xl font-bold mb-4">Ready to Start Trading?</h2>
              <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
                Join thousands of investors who trust our AI-powered trading platform to grow their wealth.
              </p>
              <Button size="lg" variant="secondary" onClick={handleGetStarted} className="bg-background text-foreground hover:bg-background/90">
                Get Started Today
                <ChevronRight className="h-5 w-5 ml-2" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-muted/30 py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-primary-foreground" />
                </div>
                <span className="text-lg font-bold">Waves Quant Engine</span>
              </div>
              <p className="text-muted-foreground">
                Professional AI-powered trading platform for modern investors.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li><a href="#features" className="hover:text-foreground transition-colors">Features</a></li>
                <li><a href="#how-it-works" className="hover:text-foreground transition-colors">How It Works</a></li>
                <li><a href="/auth" className="hover:text-foreground transition-colors">Sign Up</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li><a href="/about" className="hover:text-foreground transition-colors">About Us</a></li>
                <li><a href="/contact" className="hover:text-foreground transition-colors">Contact</a></li>
                <li><a href="/terms" className="hover:text-foreground transition-colors">Terms of Service</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Documentation</a></li>
                <li><a href="#contact" className="hover:text-foreground transition-colors">Contact Support</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t mt-8 pt-8 text-center text-muted-foreground">
            <p>&copy; 2024 Waves Quant Engine. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;

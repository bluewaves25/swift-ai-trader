
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, BarChart3, Shield, Zap, Users, Award, Target } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

const About = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20">
      {/* Header */}
      <div className="border-b bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Home</span>
              </Button>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                About Waves Quant Engine
              </h1>
            </div>
            <div className="hidden md:flex items-center space-x-6">
              <Link to="/about" className="text-foreground hover:text-primary transition-colors">About</Link>
              <Link to="/contact" className="text-foreground hover:text-primary transition-colors">Contact</Link>
              <Link to="/terms" className="text-foreground hover:text-primary transition-colors">Terms</Link>
              <Link to="/auth" className="text-foreground hover:text-primary transition-colors">Sign In</Link>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <Badge variant="outline" className="mb-4">
            Advanced AI Trading Platform
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Revolutionizing Trading with AI
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Waves Quant Engine combines cutting-edge artificial intelligence with sophisticated trading algorithms 
            to deliver superior investment performance for our clients.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <Card className="group hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                  <BarChart3 className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-lg">Advanced Analytics</h3>
              </div>
              <p className="text-muted-foreground">
                Real-time market analysis powered by machine learning algorithms that process thousands of data points per second.
              </p>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                  <Shield className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-lg">Risk Management</h3>
              </div>
              <p className="text-muted-foreground">
                Sophisticated risk controls and portfolio protection mechanisms to safeguard your investments.
              </p>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                  <Zap className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-lg">Lightning Fast</h3>
              </div>
              <p className="text-muted-foreground">
                Ultra-low latency execution ensures you never miss market opportunities with our optimized infrastructure.
              </p>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
                  <Users className="h-6 w-6 text-orange-600" />
                </div>
                <h3 className="font-semibold text-lg">Expert Team</h3>
              </div>
              <p className="text-muted-foreground">
                Led by seasoned quantitative analysts and AI researchers with decades of combined experience.
              </p>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
                  <Award className="h-6 w-6 text-red-600" />
                </div>
                <h3 className="font-semibold text-lg">Proven Results</h3>
              </div>
              <p className="text-muted-foreground">
                Consistent outperformance with a track record of delivering superior risk-adjusted returns.
              </p>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-teal-100 dark:bg-teal-900/20 rounded-lg">
                  <Target className="h-6 w-6 text-teal-600" />
                </div>
                <h3 className="font-semibold text-lg">Multi-Asset</h3>
              </div>
              <p className="text-muted-foreground">
                Trade across multiple asset classes including forex, commodities, indices, and cryptocurrencies.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Mission Statement */}
        <Card className="mb-12">
          <CardContent className="p-8 text-center">
            <h3 className="text-2xl font-bold mb-4">Our Mission</h3>
            <p className="text-lg text-muted-foreground max-w-4xl mx-auto">
              At Waves Quant Engine, we believe that advanced technology should be accessible to all investors. 
              Our mission is to democratize quantitative trading by providing institutional-grade AI trading systems 
              to individual investors, enabling them to participate in sophisticated investment strategies previously 
              available only to large hedge funds and financial institutions.
            </p>
          </CardContent>
        </Card>

        {/* Call to Action */}
        <div className="text-center">
          <h3 className="text-2xl font-bold mb-4">Ready to Start Trading?</h3>
          <p className="text-muted-foreground mb-6">
            Join thousands of investors who trust Waves Quant Engine with their trading strategies.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => navigate('/auth')}>
              Get Started Today
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate('/contact')}>
              Learn More
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;

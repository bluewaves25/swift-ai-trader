
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Brain, 
  TrendingUp, 
  Shield, 
  Zap, 
  Target,
  Users,
  Award,
  Globe,
  ArrowLeft
} from "lucide-react";
import { Link } from "react-router-dom";
import { ThemeToggle } from "@/components/theme/theme-toggle";

const About = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-2 md:px-4 py-2 md:py-4">
          <div className="flex items-center justify-between">
            <Link to="/">
              <Button variant="ghost" size="icon" className="hover:bg-muted">
                <ArrowLeft className="h-5 w-5" />
                <span className="sr-only">Back</span>
              </Button>
            </Link>
            <span className="text-lg md:text-2xl font-bold">About</span>
            <ThemeToggle />
          </div>
        </div>
      </div>

      <div className="container mx-auto px-2 md:px-4 py-4 md:py-12">
        {/* Hero Section */}
        <div className="text-center mb-8 md:mb-16">
          <Badge variant="secondary" className="mb-3 md:mb-6">
            <Zap className="h-3 w-3 md:h-4 md:w-4 mr-1 md:mr-2" />
            About Our Platform
          </Badge>
          <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold mb-4 md:mb-8 leading-tight">
            Revolutionizing Trading
            <span className="block bg-gradient-to-r from-yellow-300 via-orange-400 to-red-400 bg-clip-text text-transparent">
              with AI Precision
            </span>
          </h1>
          <p className="text-sm md:text-xl lg:text-2xl mb-6 md:mb-12 max-w-4xl mx-auto leading-relaxed font-medium text-muted-foreground">
            We combine cutting-edge artificial intelligence with sophisticated trading strategies to deliver 
            consistent results in volatile markets, making advanced trading accessible to everyone.
          </p>
        </div>

        {/* Mission Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-8 mb-8 md:mb-16">
          <Card className="bg-card border-border text-card-foreground">
            <CardHeader className="p-3 md:p-6">
              <div className="flex items-center space-x-2 mb-2 md:mb-4">
                <Target className="h-5 w-5 md:h-6 md:w-6 text-blue-300" />
                <CardTitle className="text-lg md:text-2xl">Our Mission</CardTitle>
              </div>
              <CardDescription className="text-sm md:text-base text-card-foreground">
                To democratize sophisticated trading strategies through AI-powered automation, making professional-grade 
                trading accessible to investors of all levels while maintaining the highest standards of risk management.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-card border-border text-card-foreground">
            <CardHeader className="p-3 md:p-6">
              <div className="flex items-center space-x-2 mb-2 md:mb-4">
                <Globe className="h-5 w-5 md:h-6 md:w-6 text-purple-300" />
                <CardTitle className="text-lg md:text-2xl">Our Vision</CardTitle>
              </div>
              <CardDescription className="text-sm md:text-base text-card-foreground">
                To become the world's leading AI-driven trading platform, setting new standards for performance, 
                transparency, and user experience in the financial technology industry.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Features Grid */}
        <div className="mb-8 md:mb-16">
          <div className="text-center mb-6 md:mb-12">
            <h2 className="text-2xl md:text-4xl lg:text-5xl font-bold mb-3 md:mb-6 text-white">
              What Sets Us Apart
            </h2>
            <p className="text-sm md:text-xl text-muted-foreground max-w-3xl mx-auto">
              Our platform combines advanced technology with proven trading methodologies to deliver exceptional results.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-8">
            {[
              {
                icon: Brain,
                title: "Advanced AI Algorithms",
                description: "Proprietary machine learning models that continuously adapt to market conditions and optimize trading strategies in real-time.",
                color: "blue"
              },
              {
                icon: TrendingUp,
                title: "Proven Performance",
                description: "Consistent track record of delivering superior risk-adjusted returns across various market cycles and economic conditions.",
                color: "green"
              },
              {
                icon: Shield,
                title: "Risk Management",
                description: "Sophisticated risk controls, portfolio protection mechanisms, and regulatory compliance to safeguard your investments.",
                color: "red"
              },
              {
                icon: Zap,
                title: "Ultra-Low Latency",
                description: "Lightning-fast execution infrastructure ensures you never miss profitable opportunities in fast-moving markets.",
                color: "yellow"
              },
              {
                icon: Users,
                title: "Expert Team",
                description: "Led by quantitative researchers, AI specialists, and trading professionals with decades of combined experience.",
                color: "purple"
              },
              {
                icon: Award,
                title: "Industry Recognition",
                description: "Award-winning platform recognized by leading financial institutions and technology organizations worldwide.",
                color: "indigo"
              }
            ].map((feature, index) => (
              <Card key={index} className="group hover:shadow-lg transition-all duration-300 bg-card border-border text-card-foreground">
                <CardHeader className="p-3 md:p-6">
                  <div className={`p-2 md:p-3 rounded-lg w-fit bg-${feature.color}-100/20 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className={`h-4 w-4 md:h-6 md:w-6 text-${feature.color}-300`} />
                  </div>
                  <CardTitle className="text-base md:text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent className="p-3 md:p-6 pt-0">
                  <CardDescription className="text-xs md:text-base text-card-foreground">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Stats Section */}
        <div className="mb-8 md:mb-16">
          <div className="text-center mb-6 md:mb-12">
            <h2 className="text-2xl md:text-4xl font-bold mb-3 md:mb-6 text-white">
              Platform Statistics
            </h2>
            <p className="text-sm md:text-xl text-muted-foreground max-w-3xl mx-auto">
              Real numbers that demonstrate our platform's success and growing community.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-8">
            {[
              { number: "2,847+", label: "Active Traders" },
              { number: "156K+", label: "Trades Executed" },
              { number: "87.3%", label: "Success Rate" },
              { number: "$2.8M+", label: "Total Profits" }
            ].map((stat, index) => (
              <Card key={index} className="bg-card border-border text-card-foreground text-center">
                <CardContent className="p-3 md:p-6">
                  <div className="text-xl md:text-3xl lg:text-4xl font-bold text-white mb-1 md:mb-2">{stat.number}</div>
                  <div className="text-xs md:text-sm text-muted-foreground">{stat.label}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <h2 className="text-2xl md:text-4xl font-bold mb-3 md:mb-6 text-white">
            Ready to Start Trading?
          </h2>
          <p className="text-sm md:text-xl mb-6 md:mb-8 text-muted-foreground max-w-2xl mx-auto">
            Join thousands of successful traders who trust Waves Quant Engine with their investments.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-3 md:gap-6 justify-center">
            <Link to="/auth">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold text-sm md:text-base">
                Get Started Today
              </Button>
            </Link>
            <Link to="/contact">
              <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10 font-semibold text-sm md:text-base">
                Contact Sales
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;


import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Shield, TrendingUp, Users, Zap, BarChart3, Globe, Lock } from "lucide-react";
import { Link } from "react-router-dom";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-white/10 bg-black/20 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">Waves Quant Engine</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <Link to="/about" className="text-gray-300 hover:text-white transition-colors">About</Link>
              <Link to="/contact" className="text-gray-300 hover:text-white transition-colors">Contact</Link>
              <Link to="/terms" className="text-gray-300 hover:text-white transition-colors">Terms</Link>
              <Link to="/auth">
                <Button variant="outline" className="text-white border-white/40 bg-white/10 hover:bg-white/20 backdrop-blur">
                  Login
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <Badge variant="secondary" className="mb-4 bg-purple-600/20 text-purple-300 border-purple-500/20">
              Professional HFT Platform
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Multi-Asset <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">Trading Engine</span>
            </h1>
            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Advanced algorithmic trading platform supporting Forex, Crypto, Stocks, Commodities, and Indices with AI-powered strategies and professional-grade risk management.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/auth">
                <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 shadow-lg">
                  Start Trading
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/about">
                <Button size="lg" variant="outline" className="border-white/40 text-white bg-white/10 hover:bg-white/20 backdrop-blur px-8 py-3">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 bg-black/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Professional Trading Features
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Everything you need for professional multi-asset trading
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="bg-white/5 border-white/10 backdrop-blur-lg">
              <CardHeader>
                <Globe className="h-8 w-8 text-blue-400 mb-2" />
                <CardTitle className="text-white">Multi-Asset Support</CardTitle>
                <CardDescription className="text-gray-300">
                  Trade Forex, Crypto, Stocks, Commodities, and Indices from one platform
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-white/5 border-white/10 backdrop-blur-lg">
              <CardHeader>
                <Zap className="h-8 w-8 text-purple-400 mb-2" />
                <CardTitle className="text-white">AI-Powered Strategies</CardTitle>
                <CardDescription className="text-gray-300">
                  Advanced algorithms with breakout, mean reversion, and momentum strategies
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-white/5 border-white/10 backdrop-blur-lg">
              <CardHeader>
                <BarChart3 className="h-8 w-8 text-green-400 mb-2" />
                <CardTitle className="text-white">Real-Time Analytics</CardTitle>
                <CardDescription className="text-gray-300">
                  Live market data, performance metrics, and risk analysis
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-white/5 border-white/10 backdrop-blur-lg">
              <CardHeader>
                <Shield className="h-8 w-8 text-red-400 mb-2" />
                <CardTitle className="text-white">Risk Management</CardTitle>
                <CardDescription className="text-gray-300">
                  Professional-grade risk controls and position sizing
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-white/5 border-white/10 backdrop-blur-lg">
              <CardHeader>
                <Lock className="h-8 w-8 text-yellow-400 mb-2" />
                <CardTitle className="text-white">Secure Payments</CardTitle>
                <CardDescription className="text-gray-300">
                  Deposit funds to your account through secure crypto transactions
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-white/5 border-white/10 backdrop-blur-lg">
              <CardHeader>
                <Users className="h-8 w-8 text-indigo-400 mb-2" />
                <CardTitle className="text-white">24/7 Support</CardTitle>
                <CardDescription className="text-gray-300">
                  Professional support team available around the clock
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Start Professional Trading?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join sophisticated traders using our advanced multi-asset platform
          </p>
          <Link to="/auth">
            <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-12 py-4 text-lg shadow-lg">
              Get Started Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-black/20 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white">Waves Quant Engine</span>
              </div>
              <p className="text-gray-400 text-sm max-w-md">
                Professional multi-asset trading platform with AI-powered strategies and institutional-grade risk management.
              </p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Platform</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
                <li><Link to="/terms" className="hover:text-white transition-colors">Terms</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Trading</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Forex</li>
                <li>Cryptocurrency</li>
                <li>Stocks</li>
                <li>Commodities</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 mt-8 pt-8 text-center">
            <p className="text-gray-400 text-sm">
              © 2024 Waves Quant Engine. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;

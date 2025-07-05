import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { TrendingUp, ArrowLeft, Menu } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ThemeToggle } from "@/components/theme/theme-toggle";

export default function Terms() {
  const navigate = useNavigate();

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
              <Button variant="ghost" onClick={() => navigate('/about')}>
                About
              </Button>
              <Button variant="ghost" onClick={() => navigate('/contact')}>
                Contact
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
                  <DropdownMenuItem onClick={() => navigate('/about')}>
                    About
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/contact')}>
                    Contact
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
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Terms of Service</h1>
            <p className="text-xl text-muted-foreground">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>

          <div className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>1. Acceptance of Terms</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p>
                  By accessing and using Waves Quant Engine ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>2. Service Description</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p>
                  Waves Quant Engine provides automated trading services using artificial intelligence and algorithmic trading strategies across multiple asset classes including forex, cryptocurrencies, stocks, commodities, and indices.
                </p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>AI-powered trading algorithms</li>
                  <li>Multi-asset trading capabilities</li>
                  <li>Risk management tools</li>
                  <li>Real-time portfolio monitoring</li>
                  <li>24/7 automated trading execution</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>3. Risk Disclosure</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                  <p className="font-semibold text-yellow-800 mb-2">⚠️ Important Risk Warning</p>
                  <p className="text-yellow-700">
                    Trading in financial instruments involves substantial risk and may result in the loss of your entire investment. Past performance is not indicative of future results.
                  </p>
                </div>
                <p>You acknowledge and understand that:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>All trading involves risk, and you may lose your entire investment</li>
                  <li>Past performance does not guarantee future results</li>
                  <li>Market conditions can change rapidly and unpredictably</li>
                  <li>Automated trading systems can fail or malfunction</li>
                  <li>You should only invest funds you can afford to lose</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>4. Account Terms</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p>To use our services, you must:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Be at least 18 years of age</li>
                  <li>Provide accurate and complete registration information</li>
                  <li>Maintain the confidentiality of your account credentials</li>
                  <li>Comply with all applicable laws and regulations</li>
                  <li>Not use the service for illegal activities</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>5. Deposits and Withdrawals</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <h4 className="font-semibold">Deposits:</h4>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Minimum deposit: $100</li>
                  <li>Funds are deposited directly to your account</li>
                  <li>Deposits are typically processed within 24 hours</li>
                </ul>
                
                <h4 className="font-semibold mt-4">Withdrawals:</h4>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Withdrawals are allowed after a minimum 2-week investment period</li>
                  <li>Withdrawal requests are processed within 24-48 hours</li>
                  <li>Minimum withdrawal: $50</li>
                  <li>All withdrawals are subject to verification and approval</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>6. Fees and Charges</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p>Our fee structure includes:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Performance-based fees on profitable trades</li>
                  <li>No monthly subscription or platform fees</li>
                  <li>Third-party broker fees may apply (Brokerage spreads and commissions)</li>
                  <li>Bank transfer fees for deposits/withdrawals may apply</li>
                </ul>
                <p>All fees will be clearly disclosed before any transactions.</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>7. Limitation of Liability</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p>
                  Waves Quant Engine shall not be liable for any direct, indirect, incidental, special, or consequential damages resulting from the use of our services, including but not limited to trading losses, system failures, or data breaches.
                </p>
                <p>
                  Our maximum liability is limited to the amount of fees paid by you in the 12 months preceding any claim.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>8. Privacy and Data Protection</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p>We are committed to protecting your privacy and personal data:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>All personal information is encrypted and securely stored</li>
                  <li>We do not share your data with third parties without consent</li>
                  <li>Trading data is used solely for platform improvement and support</li>
                  <li>You can request data deletion at any time</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>9. Termination</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p>Either party may terminate this agreement:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>You may close your account at any time</li>
                  <li>We may terminate accounts for violations of these terms</li>
                  <li>Upon termination, all outstanding positions will be closed</li>
                  <li>Remaining funds will be returned within 30 days</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>10. Changes to Terms</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p>
                  We reserve the right to modify these terms at any time. Changes will be communicated via email and platform notifications. Continued use of the service constitutes acceptance of modified terms.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>11. Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p>For questions about these Terms of Service, please contact us:</p>
                <ul className="list-none space-y-1">
                  <li>Email: legal@wavesquant.com</li>
                  <li>Phone: +233 (500) 33-4946</li>
                  <li>Address: 123 Financial District, Techiman, BE 10004</li>
                </ul>
              </CardContent>
            </Card>
          </div>

          <div className="mt-12 p-6 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground text-center">
              By using Waves Quant Engine, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

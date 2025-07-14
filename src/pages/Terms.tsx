import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

const Terms = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card/50 backdrop-blur-sm">
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
                Terms of Service
              </h1>
            </div>
            <div className="flex items-center space-x-6">
              <Link to="/about" className="text-foreground hover:text-primary transition-colors">About</Link>
              <Link to="/contact" className="text-foreground hover:text-primary transition-colors">Contact</Link>
              <Link to="/terms" className="text-foreground hover:text-primary transition-colors">Terms</Link>
              <Link to="/auth" className="text-foreground hover:text-primary transition-colors">Sign In</Link>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Terms of Service
          </h2>
          <p className="text-muted-foreground">
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>

        <div className="max-w-4xl mx-auto space-y-8">
          <Card>
            <CardHeader>
              <CardTitle>1. Agreement to Terms</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                By accessing and using Waves Quant Engine ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. 
                If you do not agree to abide by the above, please do not use this service.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>2. Use License</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                Permission is granted to temporarily download one copy of the materials on Waves Quant Engine's website for personal, 
                non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this license you may not:
              </p>
              <ul className="list-disc pl-6 mt-4">
                <li>modify or copy the materials</li>
                <li>use the materials for any commercial purpose or for any public display</li>
                <li>attempt to reverse engineer any software contained on the website</li>
                <li>remove any copyright or other proprietary notations from the materials</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>3. Investment Risks</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                Trading and investment involve substantial risk of loss and are not suitable for every investor. 
                The valuation of currencies, securities, and other financial instruments may fluctuate, and as a result, 
                clients may lose more than their original investment.
              </p>
              <p className="mt-4">
                <strong>Important Risk Disclosures:</strong>
              </p>
              <ul className="list-disc pl-6 mt-2">
                <li>Past performance is not indicative of future results</li>
                <li>All investments carry the risk of losses</li>
                <li>You should only invest money you can afford to lose</li>
                <li>AI trading systems may malfunction or produce unexpected results</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>4. Account Responsibilities</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                You are responsible for maintaining the confidentiality of your account information and password. 
                You accept responsibility for all activities that occur under your account.
              </p>
              <ul className="list-disc pl-6 mt-4">
                <li>Provide accurate and complete registration information</li>
                <li>Maintain the security of your login credentials</li>
                <li>Notify us immediately of any unauthorized account use</li>
                <li>Comply with all applicable laws and regulations</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>5. Deposits and Withdrawals</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                All deposits and withdrawals are processed according to our standard procedures:
              </p>
              <ul className="list-disc pl-6 mt-4">
                <li>Minimum deposit: $100 USD</li>
                <li>Deposits are typically processed within 24 hours</li>
                <li>Withdrawals require a minimum 2-week investment period</li>
                <li>Withdrawal requests are subject to review and approval</li>
                <li>We reserve the right to cancel transactions suspected of fraud or money laundering</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>6. Fees and Charges</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                Our fee structure is transparent and competitive:
              </p>
              <ul className="list-disc pl-6 mt-4">
                <li>Performance fee: 20% of profits above $10 daily profit threshold</li>
                <li>No management fees for standard accounts</li>
                <li>Payment processing fees may apply for certain deposit/withdrawal methods</li>
                <li>Fees are automatically deducted from your account balance</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>7. Prohibited Activities</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                The following activities are strictly prohibited:
              </p>
              <ul className="list-disc pl-6 mt-4">
                <li>Market manipulation or insider trading</li>
                <li>Money laundering or funding of illegal activities</li>
                <li>Attempting to hack or compromise our systems</li>
                <li>Creating multiple accounts to circumvent limits</li>
                <li>Providing false or misleading information</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>8. Limitation of Liability</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                In no event shall Waves Quant Engine or its suppliers be liable for any damages (including, without limitation, 
                damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use 
                the materials on our website, even if we or our authorized representative has been notified orally or in writing 
                of the possibility of such damage.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>9. Privacy Policy</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                Your privacy is important to us. We collect and use your personal information in accordance with our Privacy Policy, 
                which includes:
              </p>
              <ul className="list-disc pl-6 mt-4">
                <li>Personal identification information for account verification</li>
                <li>Trading activity data for performance analysis</li>
                <li>Communication preferences and support interactions</li>
                <li>We do not sell your personal information to third parties</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>10. Modifications</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                Waves Quant Engine may revise these terms of service for its website at any time without notice. 
                By using this website, you are agreeing to be bound by the then current version of these terms of service.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>11. Contact Information</CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert max-w-none">
              <p>
                If you have any questions about these Terms of Service, please contact us:
              </p>
              <ul className="list-none mt-4">
                <li>Email: legal@wavesquant.com</li>
                <li>Phone: +233 (500) 33-4946</li>
                <li>Address: Opposite Valley View University, Techiman, Site, Ghana</li>
              </ul>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-12">
          <Button onClick={() => navigate('/auth')}>
            I Agree - Sign Up Now
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Terms;


import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, ArrowLeft, FileText } from "lucide-react";
import { Link } from "react-router-dom";
import { ThemeToggle } from "@/components/theme/theme-toggle";

const Terms = () => {
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
            <span className="text-lg md:text-2xl font-bold">Terms</span>
            <ThemeToggle />
          </div>
        </div>
      </div>
      <div className="container mx-auto px-2 md:px-4 py-4 md:py-12">
        {/* Hero Section */}
        <div className="text-center mb-6 md:mb-16">
          <Badge variant="secondary" className="mb-3 md:mb-6 bg-card text-card-foreground border-card-foreground/30 backdrop-blur-sm text-xs md:text-sm">
            <FileText className="h-3 w-3 md:h-4 md:w-4 mr-1 md:mr-2" />
            Legal Information
          </Badge>
          
          <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold mb-4 md:mb-8 leading-tight">
            Terms & Conditions
          </h1>
          
          <p className="text-sm md:text-xl lg:text-2xl mb-6 md:mb-12 text-card-foreground/95 max-w-3xl mx-auto leading-relaxed font-medium">
            Please read these terms and conditions carefully before using our AI trading platform.
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <Card className="bg-card/10 backdrop-blur-md border-card-foreground/20 text-card-foreground">
            <CardHeader className="p-3 md:p-6">
              <CardTitle className="text-lg md:text-2xl">Terms of Service</CardTitle>
              <CardDescription className="text-xs md:text-base text-card-foreground/90">
                Last updated: {new Date().toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="p-3 md:p-6 space-y-4 md:space-y-6">
              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">1. Acceptance of Terms</h2>
                <p className="text-xs md:text-sm text-card-foreground/90 leading-relaxed">
                  By accessing and using Waves Quant Engine ("the Platform"), you accept and agree to be bound by the terms 
                  and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
                </p>
              </section>

              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">2. Description of Service</h2>
                <p className="text-xs md:text-sm text-card-foreground/90 leading-relaxed mb-2">
                  Waves Quant Engine provides an AI-powered trading platform that offers:
                </p>
                <ul className="list-disc list-inside text-xs md:text-sm text-card-foreground/90 space-y-1 ml-3 md:ml-4">
                  <li>Automated trading algorithms and strategies</li>
                  <li>Real-time market analysis and signals</li>
                  <li>Portfolio management and risk assessment tools</li>
                  <li>Performance analytics and reporting</li>
                </ul>
              </section>

              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">3. User Responsibilities</h2>
                <p className="text-xs md:text-sm text-card-foreground/90 leading-relaxed mb-2">
                  As a user of our platform, you agree to:
                </p>
                <ul className="list-disc list-inside text-xs md:text-sm text-card-foreground/90 space-y-1 ml-3 md:ml-4">
                  <li>Provide accurate and complete information during registration</li>
                  <li>Maintain the confidentiality of your account credentials</li>
                  <li>Use the platform in compliance with all applicable laws and regulations</li>
                  <li>Not attempt to interfere with or disrupt the platform's operation</li>
                  <li>Accept full responsibility for all trading decisions and their outcomes</li>
                </ul>
              </section>

              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">4. Risk Disclosure</h2>
                <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-2 md:p-4">
                  <p className="text-xs md:text-sm text-card-foreground/95 leading-relaxed font-medium">
                    <strong>IMPORTANT RISK WARNING:</strong> Trading in financial markets involves substantial risk of loss. 
                    Past performance does not guarantee future results. You should only trade with money you can afford to lose. 
                    Our AI algorithms, while sophisticated, cannot guarantee profits or prevent losses.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">5. Privacy Policy</h2>
                <p className="text-xs md:text-sm text-card-foreground/90 leading-relaxed">
                  We are committed to protecting your privacy. Our Privacy Policy explains how we collect, use, and protect 
                  your information when you use our platform. By using our service, you agree to the collection and use of 
                  information in accordance with our Privacy Policy.
                </p>
              </section>

              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">6. Intellectual Property</h2>
                <p className="text-xs md:text-sm text-card-foreground/90 leading-relaxed">
                  All content, algorithms, software, and intellectual property on the Waves Quant Engine platform are owned by 
                  or licensed to us. You may not copy, modify, distribute, or create derivative works based on our proprietary 
                  technology without explicit written permission.
                </p>
              </section>

              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">7. Limitation of Liability</h2>
                <p className="text-xs md:text-sm text-card-foreground/90 leading-relaxed">
                  In no event shall Waves Quant Engine, its officers, directors, employees, or agents be liable for any indirect, 
                  incidental, special, consequential, or punitive damages, including but not limited to loss of profits, trading 
                  losses, or loss of data, arising out of or in connection with your use of the platform.
                </p>
              </section>

              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">8. Termination</h2>
                <p className="text-xs md:text-sm text-card-foreground/90 leading-relaxed">
                  We reserve the right to terminate or suspend your account and access to the platform at our sole discretion, 
                  without notice, for conduct that we believe violates these Terms of Service or is harmful to other users, 
                  us, or third parties.
                </p>
              </section>

              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">9. Changes to Terms</h2>
                <p className="text-xs md:text-sm text-card-foreground/90 leading-relaxed">
                  We reserve the right to modify these terms at any time. Changes will be effective immediately upon posting to 
                  the platform. Your continued use of the platform after changes are posted constitutes your acceptance of the 
                  modified terms.
                </p>
              </section>

              <section>
                <h2 className="text-base md:text-xl font-semibold mb-2 md:mb-3 text-card-foreground">10. Contact Information</h2>
                <p className="text-xs md:text-sm text-card-foreground/90 leading-relaxed">
                  If you have any questions about these Terms of Service, please contact us at:
                </p>
                <div className="mt-2 md:mt-3 text-xs md:text-sm text-card-foreground/90">
                  <p>Email: legal@wavesquant.com</p>
                  <p>Phone: +1 (555) 123-4567</p>
                  <p>Address: 123 Financial District, New York, NY 10001</p>
                </div>
              </section>
            </CardContent>
          </Card>

          <div className="text-center mt-6 md:mt-8">
            <Link to="/auth">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold text-sm md:text-base">
                I Agree - Get Started
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Terms;

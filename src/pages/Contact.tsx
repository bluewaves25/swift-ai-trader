
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { 
  Brain, 
  Mail, 
  Phone, 
  MapPin, 
  MessageCircle,
  ArrowLeft,
  Send
} from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { ThemeToggle } from "@/components/theme/theme-toggle";

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate form submission
    setTimeout(() => {
      toast.success('Message sent successfully! We\'ll get back to you soon.');
      setFormData({ name: '', email: '', subject: '', message: '' });
      setLoading(false);
    }, 1000);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-2 md:px-4 py-2 md:py-4">
          <div className="flex items-center justify-between">
            <Link to="/">
              <Button variant="ghost" size="icon" className="hover:bg-muted">
                <ArrowLeft className="h-3 w-3" />
                <span className="sr-only">Back</span>
              </Button>
            </Link>
            <span className="text-lg md:text-2xl font-bold">Contact</span>
            <ThemeToggle />
          </div>
        </div>
      </div>

      <div className="container mx-auto px-2 md:px-4 py-4 md:py-12">
        {/* Hero Section */}
        <div className="text-center mb-6 md:mb-16">
          <Badge variant="secondary" className="mb-3 md:mb-6 bg-card border-card-foreground/30 backdrop-blur-sm text-xs md:text-sm">
            <MessageCircle className="h-2 w-2 md:h-3 md:w-3 mr-1 md:mr-2" />
            Get In Touch
          </Badge>
          
          <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold mb-4 md:mb-8 leading-tight">
            Contact Our
            <span className="block bg-gradient-to-r from-yellow-300 via-orange-400 to-red-400 bg-clip-text text-transparent">
              Expert Team
            </span>
          </h1>
          
          <p className="text-sm md:text-xl lg:text-2xl mb-6 md:mb-12 text-foreground/95 max-w-3xl mx-auto leading-relaxed font-medium">
            Have questions about our AI trading platform? We're here to help you get started 
            and maximize your trading potential.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-12">
          {/* Contact Form */}
          <Card className="bg-card border-card-foreground/20 backdrop-blur-md">
            <CardHeader className="p-3 md:p-6">
              <CardTitle className="text-lg md:text-2xl text-foreground">Send us a message</CardTitle>
              <CardDescription className="text-xs md:text-base text-foreground/90">
                Fill out the form below and we'll get back to you within 24 hours.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-3 md:p-6">
              <form onSubmit={handleSubmit} className="space-y-3 md:space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                  <div className="space-y-1 md:space-y-2">
                    <Label htmlFor="name" className="text-foreground text-xs md:text-sm">Name</Label>
                    <Input
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      className="bg-card border-card-foreground/20 text-foreground placeholder:text-foreground/40 text-xs md:text-sm"
                      placeholder="Your full name"
                    />
                  </div>
                  <div className="space-y-1 md:space-y-2">
                    <Label htmlFor="email" className="text-foreground text-xs md:text-sm">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="bg-card border-card-foreground/20 text-foreground placeholder:text-foreground/40 text-xs md:text-sm"
                      placeholder="your@email.com"
                    />
                  </div>
                </div>
                
                <div className="space-y-1 md:space-y-2">
                  <Label htmlFor="subject" className="text-foreground text-xs md:text-sm">Subject</Label>
                  <Input
                    id="subject"
                    name="subject"
                    value={formData.subject}
                    onChange={handleChange}
                    required
                    className="bg-card border-card-foreground/20 text-foreground placeholder:text-foreground/40 text-xs md:text-sm"
                    placeholder="What can we help you with?"
                  />
                </div>
                
                <div className="space-y-1 md:space-y-2">
                  <Label htmlFor="message" className="text-foreground text-xs md:text-sm">Message</Label>
                  <Textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    required
                    rows={4}
                    className="bg-card border-card-foreground/20 text-foreground placeholder:text-foreground/40 text-xs md:text-sm resize-none"
                    placeholder="Tell us more about your inquiry..."
                  />
                </div>
                
                <Button 
                  type="submit" 
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-foreground font-semibold text-xs md:text-sm"
                  disabled={loading}
                >
                  {loading ? "Sending..." : (
                    <>
                      Send Message
                      <Send className="ml-1 md:ml-2 h-2 w-2 md:h-3 md:w-3" />
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <div className="space-y-3 md:space-y-6">
            <Card className="bg-card border-card-foreground/20 backdrop-blur-md">
              <CardHeader className="p-3 md:p-6">
                <CardTitle className="text-lg md:text-2xl text-foreground">Contact Information</CardTitle>
                <CardDescription className="text-xs md:text-base text-foreground/90">
                  Reach out to us through any of these channels.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-3 md:p-6 space-y-3 md:space-y-4">
                <div className="flex items-center space-x-2 md:space-x-3">
                  <Mail className="h-3 w-3 md:h-4 md:w-4 text-blue-300" />
                  <div>
                    <p className="text-xs md:text-sm font-medium text-foreground">Email</p>
                    <p className="text-xs md:text-sm text-foreground/80">support@wavesquant.com</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 md:space-x-3">
                  <Phone className="h-3 w-3 md:h-4 md:w-4 text-green-300" />
                  <div>
                    <p className="text-xs md:text-sm font-medium text-foreground">Phone</p>
                    <p className="text-xs md:text-sm text-foreground/80">+233 (500) 33-4946</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 md:space-x-3">
                  <MapPin className="h-3 w-3 md:h-4 md:w-4 text-purple-300" />
                  <div>
                    <p className="text-xs md:text-sm font-medium text-foreground">Address</p>
                    <p className="text-xs md:text-sm text-foreground/80">
                      Site, Opposite Valley View University<br />
                      Techiman, Ghana
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-card-foreground/20 backdrop-blur-md">
              <CardHeader className="p-3 md:p-6">
                <CardTitle className="text-lg md:text-2xl text-foreground">Business Hours</CardTitle>
              </CardHeader>
              <CardContent className="p-3 md:p-6">
                <div className="space-y-1 md:space-y-2">
                  <div className="flex justify-between text-xs md:text-sm">
                    <span className="text-foreground/80">Monday - Friday</span>
                    <span className="text-foreground">9:00 AM - 6:00 PM GMT</span>
                  </div>
                  <div className="flex justify-between text-xs md:text-sm">
                    <span className="text-foreground/80">Saturday</span>
                    <span className="text-foreground">10:00 AM - 4:00 PM GMT</span>
                  </div>
                  <div className="flex justify-between text-xs md:text-sm">
                    <span className="text-foreground/80">Sunday</span>
                    <span className="text-foreground">Closed</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-card-foreground/20 backdrop-blur-md">
              <CardHeader className="p-3 md:p-6">
                <CardTitle className="text-lg md:text-2xl text-foreground">Quick Links</CardTitle>
              </CardHeader>
              <CardContent className="p-3 md:p-6">
                <div className="space-y-2 md:space-y-3">
                  <Link to="/auth" className="block">
                    <Button variant="ghost" className="w-full justify-start text-foreground hover:bg-muted text-xs md:text-sm">
                      Create Account
                    </Button>
                  </Link>
                  <Link to="/about" className="block">
                    <Button variant="ghost" className="w-full justify-start text-foreground hover:bg-muted text-xs md:text-sm">
                      Learn More About Us
                    </Button>
                  </Link>
                  <Link to="/terms" className="block">
                    <Button variant="ghost" className="w-full justify-start text-foreground hover:bg-muted text-xs md:text-sm">
                      Terms & Conditions
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;

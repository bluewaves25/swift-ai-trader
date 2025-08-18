import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageCircle, X, Send, User, Bot, Clock, CheckCircle, MessageSquare, History, Mic, MicOff, Minimize2, ChevronUp, ChevronDown } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot' | 'support';
  timestamp: Date;
  status?: 'sending' | 'sent' | 'read';
}

interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  status: 'active' | 'resolved' | 'pending';
  unreadCount: number;
}

const commonQuestions = [
  {
    question: "How do I deposit funds?",
    answer: "To deposit funds, go to your dashboard and click on 'Deposit' in the payments section. You can deposit via bank transfer, card, or crypto."
  },
  {
    question: "What are the trading fees?",
    answer: "Our trading fees are competitive: 0.1% for spot trading and 0.05% for futures. There are no deposit fees, and withdrawal fees vary by payment method."
  },
  {
    question: "How does the AI trading work?",
    answer: "Our AI analyzes market patterns using advanced machine learning algorithms. It executes trades based on proven strategies while managing risk automatically."
  },
  {
    question: "Can I withdraw my funds anytime?",
    answer: "Yes, you can request withdrawals 24/7. Processing times vary: crypto (5-30 mins), bank transfer (1-3 business days)."
  },
  {
    question: "Is my investment safe?",
    answer: "We use bank-level security, cold storage for crypto, and regulated brokers. Your funds are segregated and protected by insurance."
  }
];

export function SupportChat() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [activeTab, setActiveTab] = useState("chat");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI assistant. I can help you with common questions about trading, deposits, withdrawals, and platform features. How can I help you today?',
      sender: 'bot',
      timestamp: new Date(),
      status: 'sent'
    }
  ]);
  const [chatSessions] = useState<ChatSession[]>([
    {
      id: '1',
      title: 'General Inquiry',
      lastMessage: 'Thank you for your help!',
      timestamp: new Date(Date.now() - 3600000),
      status: 'resolved',
      unreadCount: 0
    },
    {
      id: '2',
      title: 'Deposit Issue',
      lastMessage: 'I\'ll check on that for you',
      timestamp: new Date(Date.now() - 7200000),
      status: 'pending',
      unreadCount: 2
    }
  ]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollUp, setShowScrollUp] = useState(false);
  const [showScrollDown, setShowScrollDown] = useState(false);

  // Auto-scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Scroll logic for showing buttons
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;
    const checkScroll = () => {
      setShowScrollUp(container.scrollTop > 8);
      setShowScrollDown(container.scrollTop < container.scrollHeight - container.clientHeight - 8);
    };
    container.addEventListener('scroll', checkScroll);
    checkScroll();
    return () => container.removeEventListener('scroll', checkScroll);
  }, [messages.length, isOpen]);

  const scrollToTop = () => {
    messagesContainerRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const scrollToBottom = () => {
    messagesContainerRef.current?.scrollTo({ top: messagesContainerRef.current.scrollHeight, behavior: 'smooth' });
  };

  const { isRecording, startRecording, stopRecording } = useAudioRecorder({
    onRecordingComplete: async (audioBlob) => {
      try {
        // Convert audio to base64 for sending to transcription service
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64Audio = (reader.result as string).split(',')[1];
          // Here you would send to your transcription service
          // For now, we'll just show a placeholder message
          setNewMessage("Voice message transcribed: [Audio content]");
        };
        reader.readAsDataURL(audioBlob);
      } catch (error) {
        toast.error("Failed to process audio recording");
      }
    }
  });

  const handleAudioToggle = async () => {
    try {
      if (isRecording) {
        stopRecording();
      } else {
        await startRecording();
      }
    } catch (error) {
      toast.error("Microphone access denied. Please enable microphone permissions.");
    }
  };

  const getBotResponse = (userMessage: string): string => {
    const message = userMessage.toLowerCase();
    
    // Check for common questions
    for (const qa of commonQuestions) {
      if (qa.question.toLowerCase().includes(message) || 
          message.includes(qa.question.toLowerCase().split(' ')[0]) ||
          (message.includes('deposit') && qa.question.toLowerCase().includes('deposit')) ||
          (message.includes('fee') && qa.question.toLowerCase().includes('fee')) ||
          (message.includes('withdraw') && qa.question.toLowerCase().includes('withdraw')) ||
          (message.includes('ai') && qa.question.toLowerCase().includes('ai')) ||
          (message.includes('safe') && qa.question.toLowerCase().includes('safe'))) {
        return qa.answer + "\n\nIs there anything else I can help you with? If you need further assistance, I can connect you with our support team.";
      }
    }
    
    // Default responses
    if (message.includes('hello') || message.includes('hi')) {
      return "Hello! I'm here to help you with any questions about our trading platform. What would you like to know?";
    }
    
    if (message.includes('human') || message.includes('support') || message.includes('agent')) {
      return "I'll connect you with our support team right away. They'll be able to provide more detailed assistance. Please hold on while I create a support ticket for you.";
    }
    
    return "I understand you're asking about: \"" + userMessage + "\". While I don't have specific information about that, I can connect you with our support team who will be able to help you better. Would you like me to create a support ticket?";
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      text: newMessage,
      sender: 'user',
      timestamp: new Date(),
      status: 'sending'
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = newMessage;
    setNewMessage("");
    setLoading(true);

    try {
      // Update message status to sent
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
      ));

      // Get bot response
      setTimeout(() => {
        const botResponse = getBotResponse(currentMessage);
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: botResponse,
          sender: 'bot',
          timestamp: new Date(),
          status: 'sent'
        };
        setMessages(prev => [...prev, botMessage]);
        setLoading(false);

        // Only require sign-in if bot suggests human support
        if ((botResponse.includes('support team') || botResponse.includes('support ticket')) && !user) {
          setTimeout(() => {
            setMessages(prev => [...prev, {
              id: (Date.now() + 2).toString(),
              text: "Please sign in to continue with human support.",
              sender: 'bot',
              timestamp: new Date(),
              status: 'sent'
            }]);
          }, 1000);
          return;
        }
        // If signed in and bot suggests human support, create ticket
        if ((botResponse.includes('support team') || botResponse.includes('support ticket')) && user) {
          setTimeout(async () => {
            try {
              const { error } = await supabase
                .from('support_tickets')
                .insert({
                  user_id: user.id,
                  subject: 'Chat Support Request',
                  description: `User message: ${currentMessage}\n\nBot response: ${botResponse}`,
                  status: 'open'
                });

              if (!error) {
                const ticketMessage: Message = {
                  id: (Date.now() + 3).toString(),
                  text: "✅ I've created a support ticket for you. Our team will respond within 24 hours. You'll receive updates via email.",
                  sender: 'bot',
                  timestamp: new Date(),
                  status: 'sent'
                };
                setMessages(prev => [...prev, ticketMessage]);
              }
            } catch (error) {
              console.error('Error creating support ticket:', error);
            }
          }, 1000);
        }
      }, 1000);

    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickQuestion = (question: string) => {
    setNewMessage(question);
    setTimeout(() => handleSendMessage(), 100);
  };

  return (
    <>
      {/* Support Chat Button */}
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          className="h-10 w-10 rounded-full shadow-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 border-0 relative"
        >
                      <MessageCircle className="h-3 w-3 text-white" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
        </Button>
      </div>

      {/* Enhanced Support Chat Modal - Slides up from bottom */}
      {isOpen && (
        <div className="fixed inset-0 z-50 pointer-events-none">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/20 pointer-events-auto" 
            onClick={() => setIsOpen(false)} 
          />
          {/* Chat Modal */}
          <div
            className="absolute right-4 bottom-8 md:bottom-8 z-50 pointer-events-auto transition-all duration-300 w-full max-w-sm"
            style={{ minWidth: 320, maxHeight: '80vh' }}
          >
            <Card className="flex flex-col bg-white/95 dark:bg-gray-900/95 shadow-2xl border-white/20 rounded-t-xl rounded-b-xl max-h-[80vh] h-[600px]">
              {/* Header */}
              <CardHeader className="flex-shrink-0 pb-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-t-xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <Bot className="h-4 w-4 p-1 bg-white/20 rounded-full" />
                      <div className="absolute -bottom-0.5 -right-0.5 w-2 h-2 bg-green-400 rounded-full border border-white"></div>
                    </div>
                    <div>
                      <CardTitle className="text-sm font-semibold">AI Support</CardTitle>
                      <p className="text-xs opacity-90">Usually responds instantly</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsMinimized(!isMinimized)}
                      className="h-4 w-4 p-0 text-white hover:bg-white/20"
                    >
                      <Minimize2 className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsOpen(false)}
                      className="h-4 w-4 p-0 text-white hover:bg-white/20"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>

              {/* Content - Hidden when minimized */}
              {!isMinimized && (
                <div className="flex-1 flex flex-col overflow-hidden max-h-[calc(80vh-56px)] relative">
                  <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
                    <TabsList className="grid w-full grid-cols-2 bg-white/50 dark:bg-gray-800/50 m-2 rounded-lg">
                      <TabsTrigger value="chat" className="flex items-center gap-2 text-xs">
                        <MessageSquare className="h-3 w-3" />
                        Chat
                      </TabsTrigger>
                      <TabsTrigger value="history" className="flex items-center gap-2 text-xs">
                        <History className="h-3 w-3" />
                        History
                      </TabsTrigger>
                    </TabsList>
                    {/* Quick Questions */}
                    <div className="p-2 border-b bg-white/50 dark:bg-gray-800/50">
                      <p className="text-xs font-medium mb-2">Quick questions:</p>
                      <div className="flex gap-1 flex-wrap">
                        {commonQuestions.slice(0, 3).map((qa, i) => (
                          <Button
                            key={i}
                            variant="outline"
                            size="sm"
                            className="text-xs h-5 px-2"
                            onClick={() => handleQuickQuestion(qa.question)}
                          >
                            {qa.question}
                          </Button>
                        ))}
                      </div>
                    </div>
                    {/* Messages area with scroll buttons */}
                    <div className="relative flex-1">
                      <div
                        ref={messagesContainerRef}
                        className="flex-1 p-3 overflow-y-auto pr-8" // add pr-8 for scroll buttons
                        style={{ maxHeight: '320px', minHeight: '120px' }}
                      >
                        <div className="space-y-3">
                          {messages.map((message) => (
                            <div
                              key={message.id}
                              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                              <div className={`flex items-start space-x-2 max-w-[85%] ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                                <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
                                  message.sender === 'user' 
                                    ? 'bg-blue-500' 
                                    : message.sender === 'bot' 
                                    ? 'bg-purple-500' 
                                    : 'bg-green-500'
                                }`}>
                                  {message.sender === 'user' ? (
                                    <User className="h-3 w-3 text-white" />
                                  ) : message.sender === 'bot' ? (
                                    <Bot className="h-3 w-3 text-white" />
                                  ) : (
                                    <MessageCircle className="h-3 w-3 text-white" />
                                  )}
                                </div>
                                <div className={`rounded-2xl px-3 py-2 border shadow-sm ${
                                  message.sender === 'user'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white border shadow-sm'
                                }`}>
                                  <p className="text-xs whitespace-pre-wrap">{message.text}</p>
                                  <div className={`flex items-center justify-between mt-1 ${
                                    message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                                  }`}>
                                    <p className="text-xs">
                                      {message.timestamp.toLocaleTimeString('en-US', { 
                                        hour: '2-digit', 
                                        minute: '2-digit' 
                                      })}
                                    </p>
                                    {message.sender === 'user' && (
                                      <div className="flex items-center space-x-1">
                                        {message.status === 'sending' && <Clock className="h-2 w-2" />}
                                        {message.status === 'sent' && <CheckCircle className="h-2 w-2" />}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                          {loading && (
                            <div className="flex justify-start">
                              <div className="flex items-start space-x-2">
                                <div className="w-6 h-6 rounded-full bg-purple-500 flex items-center justify-center">
                                  <Bot className="h-3 w-3 text-white" />
                                </div>
                                <div className="bg-white dark:bg-gray-700 rounded-2xl px-3 py-2 border shadow-sm">
                                  <div className="flex space-x-1">
                                    <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse"></div>
                                    <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse delay-100"></div>
                                    <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse delay-200"></div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                          <div ref={messagesEndRef} />
                        </div>
                      </div>
                      {/* Scroll buttons */}
                      {showScrollUp && (
                        <button
                          className="absolute right-2 top-2 z-30 bg-white dark:bg-gray-800 rounded-full shadow p-1 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700"
                          onClick={scrollToTop}
                          aria-label="Scroll to top"
                        >
                          <ChevronUp className="h-3 w-3" />
                        </button>
                      )}
                      {showScrollDown && (
                        <button
                          className="absolute right-2 bottom-2 z-30 bg-white dark:bg-gray-800 rounded-full shadow p-1 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700"
                          onClick={scrollToBottom}
                          aria-label="Scroll to bottom"
                        >
                          <ChevronDown className="h-3 w-3" />
                        </button>
                      )}
                    </div>
                    {/* Sticky Input */}
                    <div className="flex-shrink-0 p-2 border-t bg-white/50 dark:bg-gray-800/50 sticky bottom-0 z-20">
                      <div className="flex space-x-2">
                        <Input
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          onKeyPress={handleKeyPress}
                          placeholder="Type your message..."
                          className="flex-1 rounded-full border-gray-300 focus:border-blue-500 bg-white dark:bg-gray-700 text-xs"
                          disabled={loading}
                        />
                        <Button
                          onClick={handleAudioToggle}
                          variant={isRecording ? "destructive" : "outline"}
                          size="sm"
                          className="rounded-full w-8 h-8 p-0"
                        >
                          {isRecording ? <MicOff className="h-2 w-2" /> : <Mic className="h-2 w-2" />}
                        </Button>
                        <Button
                          onClick={handleSendMessage}
                          disabled={loading || !newMessage.trim()}
                          className="rounded-full w-8 h-8 p-0 bg-blue-500 hover:bg-blue-600"
                        >
                          <Send className="h-2 w-2" />
                        </Button>
                      </div>
                    </div>
                  </Tabs>
                </div>
              )}
            </Card>
          </div>
        </div>
      )}
    </>
  );
}

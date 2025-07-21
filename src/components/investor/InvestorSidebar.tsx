
import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  LayoutDashboard, 
  Wallet, 
  TrendingUp, 
  History, 
  BookOpen, 
  Settings, 
  User,
  Brain,
  ChevronDown,
  ChevronRight,
  PlusCircle,
  MinusCircle,
  List,
  LogOut,
  ChevronLeft,
  CreditCard,
  DollarSign,
  Users,
  ChevronUp
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

interface InvestorSidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  isMobileOpen?: boolean;
  onMobileToggle?: (open: boolean) => void;
}

const sidebarItems = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard, color: 'text-blue-600' },
  { id: 'portfolio', label: 'Portfolio', icon: Wallet, color: 'text-green-600' },
  { id: 'signals', label: 'Live Signals', icon: TrendingUp, color: 'text-purple-600' },
  { id: 'trades', label: 'Trade History', icon: History, color: 'text-orange-600' },
  { id: 'journal', label: 'Journal', icon: BookOpen, color: 'text-emerald-600' },
  { id: 'marketplace', label: 'Marketplace', icon: Brain, color: 'text-indigo-600' },
  { id: 'affiliate', label: 'Affiliate', icon: Users, color: 'text-pink-600' },
  { id: 'subscription', label: 'Subscription/Billing', icon: CreditCard, color: 'text-yellow-600' },
  { id: 'fees', label: 'Performance Fees', icon: DollarSign, color: 'text-indigo-600' },
  { id: 'settings', label: 'Settings', icon: Settings, color: 'text-gray-600' },
  { id: 'profile', label: 'Profile', icon: User, color: 'text-pink-600' },
];

export function InvestorSidebar({ activeSection, onSectionChange, isMobileOpen = false, onMobileToggle }: InvestorSidebarProps) {
  const { signOut, user } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [paymentsOpen, setPaymentsOpen] = useState(false);
  const [showScrollUp, setShowScrollUp] = useState(false);
  const [showScrollDown, setShowScrollDown] = useState(false);
  const sidebarContentRef = useRef<HTMLDivElement>(null);

  const paymentItems = [
    { id: 'deposit', label: 'Deposit', icon: PlusCircle, color: 'text-green-600', gradient: 'from-green-500 to-emerald-600' },
    { id: 'withdraw', label: 'Withdraw', icon: MinusCircle, color: 'text-red-600', gradient: 'from-red-500 to-rose-600' },
    { id: 'transactions', label: 'History', icon: List, color: 'text-blue-600', gradient: 'from-blue-500 to-indigo-600' },
  ];

  // Check scroll position and show/hide scroll buttons
  useEffect(() => {
    const checkScroll = () => {
      if (sidebarContentRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = sidebarContentRef.current;
        setShowScrollUp(scrollTop > 8);
        setShowScrollDown(scrollTop < scrollHeight - clientHeight - 8);
      }
    };

    const contentElement = sidebarContentRef.current;
    if (contentElement) {
      contentElement.addEventListener('scroll', checkScroll);
      checkScroll(); // Check initial state
      
      return () => contentElement.removeEventListener('scroll', checkScroll);
    }
  }, [isCollapsed]);

  const scrollToTop = () => {
    if (sidebarContentRef.current) {
      sidebarContentRef.current.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  };

  const scrollToBottom = () => {
    if (sidebarContentRef.current) {
      sidebarContentRef.current.scrollTo({
        top: sidebarContentRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  };

  const NavItem = ({ item, isActive = false }: { item: any; isActive?: boolean }) => (
    <SidebarMenuButton
      onClick={() => onSectionChange(item.id)}
      className={cn(
        "w-full justify-start h-12 mb-2 transition-all duration-300 group relative rounded-lg",
        isCollapsed ? "px-3" : "px-4",
        isActive && "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-400 border-r-2 border-blue-500 shadow-md",
        !isActive && "hover:bg-gray-100 dark:hover:bg-gray-800 hover:scale-[1.02] hover:shadow-sm"
      )}
    >
      <item.icon className={cn(
        "h-5 w-5 transition-colors duration-300 flex-shrink-0",
        isCollapsed ? "mx-auto" : "mr-3",
        isActive ? item.color : "text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300"
      )} />
      {!isCollapsed && (
        <span className="font-medium transition-all duration-300 text-sm truncate">{item.label}</span>
      )}
      {isActive && !isCollapsed && (
        <div className="absolute right-2 w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
      )}
    </SidebarMenuButton>
  );

  return (
    <div className={cn(
      "flex flex-col h-screen max-h-screen overflow-hidden bg-card border-r transition-all duration-300 relative",
      isCollapsed ? "w-16" : "w-64",
      "md:relative md:translate-x-0",
      "fixed inset-y-0 left-0 z-50 md:z-auto",
      isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
    )}>
      {/* Header */}
      <SidebarHeader className="flex-shrink-0">
        <div className="p-4">
          <div className="flex items-center justify-between">
            {!isCollapsed && (
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-sm">{user?.email?.split('@')[0] || 'User'}</span>
                <ChevronDown className="h-4 w-4 text-gray-400" />
              </div>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="h-8 w-8 p-0 hidden md:flex hover:bg-gray-100 dark:hover:bg-gray-800/50 rounded-full"
            >
              {isCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </SidebarHeader>

      {/* User Info - This section is removed as it's merged into the header */}
      
      {/* Scroll Up Button */}
      {showScrollUp && (
        <div className="absolute top-2 left-1/2 transform -translate-x-1/2 z-10">
          <Button size="sm" variant="secondary" onClick={scrollToTop} className="h-6 w-6 p-0 rounded-full shadow-lg">
            <ChevronUp className="h-3 w-3" />
          </Button>
        </div>
      )}
      <SidebarContent 
        ref={sidebarContentRef}
        className="flex-1 min-h-0 overflow-auto p-2 space-y-2 relative"
      >
        <div className={cn("space-y-2", !isCollapsed && "px-2")}>
          {!isCollapsed && (
            <p className="text-sm font-medium text-muted-foreground mb-2 px-2">
              Main Menu
            </p>
          )}
          {sidebarItems.slice(0, 5).map((item) => (
            <NavItem
              key={item.id}
              item={item}
              isActive={activeSection === item.id}
            />
          ))}
        </div>

        <Separator className="my-4" />

        {/* Payments Collapsible Menu */}
        <div className={cn("space-y-2", !isCollapsed && "px-2")}>
          {!isCollapsed && (
            <p className="text-sm font-medium text-muted-foreground mb-2 px-2">
              Financial Hub
            </p>
          )}
          <Collapsible open={paymentsOpen} onOpenChange={setPaymentsOpen}>
            <CollapsibleTrigger asChild>
              <SidebarMenuButton
                className={cn(
                  "w-full justify-start h-12 mb-2 transition-all duration-300 rounded-lg group",
                  isCollapsed ? "px-3" : "px-4",
                  (activeSection === 'deposit' || activeSection === 'withdraw' || activeSection === 'transactions') && 
                  "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-400 shadow-md"
                )}
              >
                <CreditCard className={cn(
                  "h-5 w-5 flex-shrink-0",
                  isCollapsed ? "mx-auto" : "mr-3"
                )} />
                {!isCollapsed && (
                  <>
                    <span className="text-sm font-medium">Payments</span>
                    {paymentsOpen ? 
                      <ChevronDown className="h-4 w-4 ml-auto transition-transform duration-200" /> : 
                      <ChevronRight className="h-4 w-4 ml-auto transition-transform duration-200" />
                    }
                  </>
                )}
              </SidebarMenuButton>
            </CollapsibleTrigger>
            {!isCollapsed && (
              <CollapsibleContent className="space-y-1">
                <SidebarMenuSub>
                  {paymentItems.map((item) => (
                    <SidebarMenuSubItem key={item.id}>
                      <SidebarMenuSubButton
                        onClick={() => onSectionChange(item.id)}
                        className={cn(
                          "transition-all duration-300 group hover:scale-[1.02] rounded-lg relative",
                          activeSection === item.id && "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-400 shadow-sm"
                        )}
                      >
                        <div className={cn(
                          "w-6 h-6 rounded-full flex items-center justify-center mr-3 transition-all duration-300",
                          activeSection === item.id ? `bg-gradient-to-r ${item.gradient} shadow-md` : "bg-gray-100 dark:bg-gray-700 group-hover:bg-gray-200 dark:group-hover:bg-gray-600"
                        )}>
                          <item.icon className={cn(
                            "h-3.5 w-3.5",
                            activeSection === item.id ? "text-white" : item.color
                          )} />
                        </div>
                        <span className="text-sm font-medium">{item.label}</span>
                        {activeSection === item.id && (
                          <div className="absolute right-2 w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></div>
                        )}
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  ))}
                </SidebarMenuSub>
              </CollapsibleContent>
            )}
          </Collapsible>
        </div>

        <Separator className="my-4" />

        {/* Account Section */}
        <div className={cn("space-y-2", !isCollapsed && "px-2")}>
          {!isCollapsed && (
            <p className="text-sm font-medium text-muted-foreground mb-2 px-2">
              Account
            </p>
          )}
          {sidebarItems.slice(5).map((item) => (
            <NavItem
              key={item.id}
              item={item}
              isActive={activeSection === item.id}
            />
          ))}
        </div>
      </SidebarContent>
      {/* Scroll Down Button */}
      {showScrollDown && (
        <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 z-10">
          <Button size="sm" variant="secondary" onClick={scrollToBottom} className="h-6 w-6 p-0 rounded-full shadow-lg">
            <ChevronDown className="h-3 w-3" />
          </Button>
        </div>
      )}

      {/* Sign Out Button */}
      <div className="p-2 border-t mt-auto">
        <Button
          variant="ghost"
          className={cn(
            "w-full justify-start h-12 text-gray-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-300 rounded-lg",
            isCollapsed ? "px-3" : "px-4"
          )}
          onClick={signOut}
        >
          <LogOut className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
          {!isCollapsed && <span className="font-medium text-sm">Sign Out</span>}
        </Button>
      </div>
    </div>
  );
}

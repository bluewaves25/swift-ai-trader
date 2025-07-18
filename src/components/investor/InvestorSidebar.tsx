
import { useState } from "react";
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
  CreditCard, 
  Settings, 
  User,
  Brain,
  ChevronDown,
  ChevronRight,
  PlusCircle,
  MinusCircle,
  List,
  LogOut,
  ChevronLeft
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
  { id: 'settings', label: 'Settings', icon: Settings, color: 'text-gray-600' },
  { id: 'profile', label: 'Profile', icon: User, color: 'text-pink-600' },
];

export function InvestorSidebar({ activeSection, onSectionChange, isMobileOpen = false, onMobileToggle }: InvestorSidebarProps) {
  const { signOut, user } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [paymentsOpen, setPaymentsOpen] = useState(false);

  const paymentItems = [
    { id: 'deposit', label: 'Deposit', icon: PlusCircle, color: 'text-green-600' },
    { id: 'withdraw', label: 'Withdraw', icon: MinusCircle, color: 'text-red-600' },
    { id: 'transactions', label: 'Transactions', icon: List, color: 'text-blue-600' },
  ];

  const NavItem = ({ item, isActive = false }: { item: any; isActive?: boolean }) => (
    <SidebarMenuButton
      onClick={() => onSectionChange(item.id)}
      className={cn(
        "w-full justify-start h-10 md:h-12 mb-1 transition-all duration-300 group relative",
        isCollapsed ? "px-2 md:px-3" : "px-3 md:px-4",
        isActive && "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-400 border-r-2 border-blue-500",
        !isActive && "hover:bg-gray-100 dark:hover:bg-gray-800 hover:scale-105"
      )}
    >
      <item.icon className={cn(
        "h-4 w-4 md:h-5 md:w-5 transition-colors duration-300",
        isCollapsed ? "mx-auto" : "mr-2 md:mr-3",
        isActive ? item.color : "text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300"
      )} />
      {!isCollapsed && (
        <span className="font-medium transition-all duration-300 text-sm md:text-base">{item.label}</span>
      )}
      {isActive && !isCollapsed && (
        <div className="absolute right-2 w-2 h-2 rounded-full bg-blue-500"></div>
      )}
    </SidebarMenuButton>
  );

  return (
    <div className={cn(
      "flex flex-col h-full bg-card border-r transition-all duration-300 relative",
      isCollapsed ? "w-12 md:w-16" : "w-56 md:w-64",
      "md:relative md:translate-x-0",
      "fixed inset-y-0 left-0 z-50 md:z-auto",
      isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
    )}>
      {/* Header */}
      <SidebarHeader>
        <div className="p-2 md:p-4 border-b bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
          <div className="flex items-center justify-between">
            {!isCollapsed && (
              <div className="flex items-center space-x-2 md:space-x-3">
                <div className="p-1 md:p-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg">
                  <Brain className="h-4 w-4 md:h-6 md:w-6 text-white" />
                </div>
                <div>
                  <span className="font-bold text-sm md:text-lg bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Investor
                  </span>
                  <div className="flex items-center space-x-1 md:space-x-2 mt-1">
                    <div className="w-1.5 h-1.5 md:w-2 md:h-2 rounded-full bg-green-500"></div>
                    <span className="text-xs text-muted-foreground">Online</span>
                  </div>
                </div>
              </div>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="h-6 w-6 md:h-8 md:w-8 p-0 hidden md:flex hover:bg-white/50 dark:hover:bg-gray-800/50"
            >
              {isCollapsed ? (
                <ChevronRight className="h-3 w-3 md:h-4 md:w-4" />
              ) : (
                <ChevronLeft className="h-3 w-3 md:h-4 md:w-4" />
              )}
            </Button>
          </div>
        </div>
      </SidebarHeader>

      {/* User Info */}
      {!isCollapsed && (
        <div className="p-2 md:p-4 border-b bg-gray-50 dark:bg-gray-800/50">
          <div className="flex items-center space-x-2 md:space-x-3">
            <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs md:text-sm">
              {user?.email?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs md:text-sm font-medium truncate">{user?.email}</p>
              <Badge variant="outline" className="text-xs mt-1 border-blue-200 text-blue-700 bg-blue-50 dark:border-blue-800 dark:text-blue-400 dark:bg-blue-900/20">
                Investor
              </Badge>
            </div>
          </div>
        </div>
      )}

      {/* Main Navigation */}
      <SidebarContent className="flex-1 p-1 md:p-2 space-y-1 overflow-y-auto">
        <div className={cn("space-y-1", !isCollapsed && "px-1 md:px-2")}>
          {!isCollapsed && (
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 md:mb-3 px-1 md:px-2">
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

        <Separator className="my-2 md:my-4" />

        {/* Payments Collapsible Menu */}
        <div className={cn("space-y-1", !isCollapsed && "px-1 md:px-2")}>
          {!isCollapsed && (
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 md:mb-3 px-1 md:px-2">
              Payments
            </p>
          )}
          <Collapsible open={paymentsOpen} onOpenChange={setPaymentsOpen}>
            <CollapsibleTrigger asChild>
              <SidebarMenuButton
                className={cn(
                  "w-full justify-start h-10 md:h-12 mb-1 transition-all duration-300",
                  isCollapsed ? "px-2 md:px-3" : "px-3 md:px-4",
                  (activeSection === 'deposit' || activeSection === 'withdraw' || activeSection === 'transactions') && 
                  "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-400"
                )}
              >
                <CreditCard className={cn("h-4 w-4 md:h-5 md:w-5", isCollapsed ? "mx-auto" : "mr-2 md:mr-3")} />
                {!isCollapsed && (
                  <>
                    <span className="text-sm md:text-base">Payments</span>
                    {paymentsOpen ? <ChevronDown className="h-3 w-3 md:h-4 md:w-4 ml-auto" /> : <ChevronRight className="h-3 w-3 md:h-4 md:w-4 ml-auto" />}
                  </>
                )}
              </SidebarMenuButton>
            </CollapsibleTrigger>
            {!isCollapsed && (
              <CollapsibleContent>
                <SidebarMenuSub>
                  {paymentItems.map((item) => (
                    <SidebarMenuSubItem key={item.id}>
                      <SidebarMenuSubButton
                        onClick={() => onSectionChange(item.id)}
                        className={cn(
                          "transition-all duration-300",
                          activeSection === item.id && "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-400"
                        )}
                      >
                        <item.icon className="h-3 w-3 md:h-4 md:w-4 mr-1 md:mr-2" />
                        <span className="text-xs md:text-sm">{item.label}</span>
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  ))}
                </SidebarMenuSub>
              </CollapsibleContent>
            )}
          </Collapsible>
        </div>

        <Separator className="my-2 md:my-4" />

        {/* Account Section */}
        <div className={cn("space-y-1", !isCollapsed && "px-1 md:px-2")}>
          {!isCollapsed && (
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 md:mb-3 px-1 md:px-2">
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

      {/* Sign Out Button */}
      <div className="p-1 md:p-2 border-t bg-gray-50 dark:bg-gray-800/50">
        <Button
          variant="ghost"
          className={cn(
            "w-full justify-start h-10 md:h-12 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-300",
            isCollapsed ? "px-2 md:px-3" : "px-3 md:px-4"
          )}
          onClick={signOut}
        >
          <LogOut className={cn("h-4 w-4 md:h-5 md:w-5", isCollapsed ? "mx-auto" : "mr-2 md:mr-3")} />
          {!isCollapsed && <span className="font-medium text-sm md:text-base">Sign Out</span>}
        </Button>
      </div>
    </div>
  );
}

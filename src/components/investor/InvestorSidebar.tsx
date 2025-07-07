
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
  LogOut
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

interface InvestorSidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

const sidebarItems = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'portfolio', label: 'Portfolio', icon: Wallet },
  { id: 'signals', label: 'Live Signals', icon: TrendingUp },
  { id: 'trades', label: 'Trade History', icon: History },
  { id: 'journal', label: 'Journal', icon: BookOpen },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'profile', label: 'Profile', icon: User },
];

export function InvestorSidebar({ activeSection, onSectionChange }: InvestorSidebarProps) {
  const { signOut } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [paymentsOpen, setPaymentsOpen] = useState(false);

  const paymentItems = [
    { id: 'deposit', label: 'Deposit', icon: PlusCircle },
    { id: 'withdraw', label: 'Withdraw', icon: MinusCircle },
    { id: 'transactions', label: 'Transactions', icon: List },
  ];

  return (
    <div className={cn(
      "flex flex-col h-full bg-card border-r transition-all duration-300",
      isCollapsed ? "w-16" : "w-64"
    )}>
      <SidebarHeader>
        <div className="flex items-center justify-between px-4 py-2">
          {!isCollapsed && (
            <div className="flex items-center space-x-2">
              <Brain className="h-6 w-6 text-primary" />
              <span className="font-bold text-lg">Waves Quant</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="h-8 w-8 p-0"
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
      </SidebarHeader>

      <SidebarContent className="flex-1">
        <SidebarMenu className="space-y-1 p-2">
          {sidebarItems.map((item) => (
            <SidebarMenuItem key={item.id}>
              <SidebarMenuButton
                onClick={() => onSectionChange(item.id)}
                className={cn(
                  "w-full justify-start h-12",
                  isCollapsed && "px-2",
                  activeSection === item.id && "bg-primary/10 text-primary font-medium"
                )}
              >
                <item.icon className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
                {!isCollapsed && <span>{item.label}</span>}
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}

          {/* Payments Collapsible Menu */}
          <SidebarMenuItem>
            <Collapsible open={paymentsOpen} onOpenChange={setPaymentsOpen}>
              <CollapsibleTrigger asChild>
                <SidebarMenuButton
                  className={cn(
                    "w-full justify-start h-12",
                    isCollapsed && "px-2",
                    (activeSection === 'deposit' || activeSection === 'withdraw' || activeSection === 'transactions') && 
                    "bg-primary/10 text-primary font-medium"
                  )}
                >
                  <CreditCard className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
                  {!isCollapsed && (
                    <>
                      <span>Payments</span>
                      {paymentsOpen ? <ChevronDown className="h-4 w-4 ml-auto" /> : <ChevronRight className="h-4 w-4 ml-auto" />}
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
                            activeSection === item.id && "bg-primary/10 text-primary font-medium"
                          )}
                        >
                          <item.icon className="h-4 w-4 mr-2" />
                          {item.label}
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    ))}
                  </SidebarMenuSub>
                </CollapsibleContent>
              )}
            </Collapsible>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>

      {/* Sign Out Button */}
      <div className="p-2 border-t">
        <Button
          variant="ghost"
          onClick={signOut}
          className={cn(
            "w-full justify-start h-12 text-red-600 hover:text-red-700 hover:bg-red-50",
            isCollapsed && "px-2"
          )}
        >
          <LogOut className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
          {!isCollapsed && <span>Sign Out</span>}
        </Button>
      </div>
    </div>
  );
}

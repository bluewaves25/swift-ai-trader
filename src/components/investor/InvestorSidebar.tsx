
import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
  useSidebar,
} from "@/components/ui/sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  BarChart3,
  Wallet,
  Activity,
  FileText,
  CreditCard,
  Settings,
  User,
  TrendingUp,
  Eye,
  ChevronDown,
  DollarSign,
  ArrowUpCircle,
  ArrowDownCircle,
  LogOut,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

interface InvestorSidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export function InvestorSidebar({ activeSection, onSectionChange }: InvestorSidebarProps) {
  const { collapsed } = useSidebar();
  const { signOut } = useAuth();
  const [paymentsOpen, setPaymentsOpen] = useState(false);

  const mainMenuItems = [
    { id: "overview", title: "Overview", icon: BarChart3 },
    { id: "portfolio", title: "Portfolio", icon: Wallet },
    { id: "signals", title: "Live Signals", icon: Activity },
    { id: "trades", title: "Trade History", icon: TrendingUp },
    { id: "journal", title: "Journal", icon: FileText },
  ];

  const paymentItems = [
    { id: "deposit", title: "Deposit", icon: ArrowUpCircle },
    { id: "withdraw", title: "Withdraw", icon: ArrowDownCircle },
  ];

  const bottomMenuItems = [
    { id: "settings", title: "Settings", icon: Settings },
    { id: "profile", title: "Profile", icon: User },
  ];

  const isActive = (id: string) => activeSection === id;

  return (
    <Sidebar className={collapsed ? "w-14" : "w-64"} collapsible>
      <SidebarHeader className="p-4">
        <div className="flex items-center space-x-2">
          <TrendingUp className="h-8 w-8 text-primary" />
          {!collapsed && (
            <div>
              <h2 className="text-lg font-bold">Waves Quant</h2>
              <Badge variant="outline" className="text-xs">
                <Eye className="h-3 w-3 mr-1" />
                Investor
              </Badge>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Trading</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainMenuItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    asChild
                    isActive={isActive(item.id)}
                    onClick={() => onSectionChange(item.id)}
                  >
                    <button className="flex items-center space-x-2 w-full text-left">
                      <item.icon className="h-4 w-4" />
                      {!collapsed && <span>{item.title}</span>}
                    </button>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Payments</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <Collapsible open={paymentsOpen} onOpenChange={setPaymentsOpen}>
                  <CollapsibleTrigger asChild>
                    <SidebarMenuButton className="flex items-center justify-between w-full">
                      <div className="flex items-center space-x-2">
                        <CreditCard className="h-4 w-4" />
                        {!collapsed && <span>Payments</span>}
                      </div>
                      {!collapsed && <ChevronDown className="h-4 w-4" />}
                    </SidebarMenuButton>
                  </CollapsibleTrigger>
                  {!collapsed && (
                    <CollapsibleContent className="ml-6 mt-2 space-y-1">
                      {paymentItems.map((item) => (
                        <Button
                          key={item.id}
                          variant={isActive(item.id) ? "default" : "ghost"}
                          size="sm"
                          className="w-full justify-start"
                          onClick={() => onSectionChange(item.id)}
                        >
                          <item.icon className="h-4 w-4 mr-2" />
                          {item.title}
                        </Button>
                      ))}
                    </CollapsibleContent>
                  )}
                </Collapsible>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Account</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {bottomMenuItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    asChild
                    isActive={isActive(item.id)}
                    onClick={() => onSectionChange(item.id)}
                  >
                    <button className="flex items-center space-x-2 w-full text-left">
                      <item.icon className="h-4 w-4" />
                      {!collapsed && <span>{item.title}</span>}
                    </button>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-4">
        <Button
          variant="outline"
          onClick={signOut}
          className="w-full justify-start"
        >
          <LogOut className="h-4 w-4 mr-2" />
          {!collapsed && "Sign Out"}
        </Button>
      </SidebarFooter>
    </Sidebar>
  );
}

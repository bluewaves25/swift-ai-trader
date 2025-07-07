import { cn } from "@/lib/utils";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { 
  LayoutDashboard, 
  Wallet, 
  TrendingUp, 
  History, 
  BookOpen, 
  CreditCard, 
  Settings, 
  User,
  Brain
} from "lucide-react";

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
  { id: 'payments', label: 'Payments', icon: CreditCard },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'profile', label: 'Profile', icon: User },
];

export function InvestorSidebar({ activeSection, onSectionChange }: InvestorSidebarProps) {
  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center space-x-2 px-4 py-2">
          <Brain className="h-6 w-6 text-primary" />
          <span className="font-bold text-lg">Waves Quant</span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          {sidebarItems.map((item) => (
            <SidebarMenuItem key={item.id}>
              <SidebarMenuButton
                onClick={() => onSectionChange(item.id)}
                className={cn(
                  "w-full justify-start",
                  activeSection === item.id && "bg-primary/10 text-primary font-medium"
                )}
              >
                <item.icon className="h-4 w-4" />
                <span>{item.label}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
    </Sidebar>
  );
}

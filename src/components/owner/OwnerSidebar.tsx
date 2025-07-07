import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { 
  LayoutDashboard, 
  Activity, 
  BarChart3, 
  Settings,
  Users,
  TrendingUp,
  Shield,
  Brain,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Info,
  Mail,
  FileText,
  Cpu,
  Target,
  AlertTriangle
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

interface OwnerSidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export function OwnerSidebar({ activeSection, onSectionChange }: OwnerSidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { signOut } = useAuth();

  const mainNavItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'engine', label: 'Trading Engine', icon: Cpu },
    { id: 'signals', label: 'Live Signals', icon: Activity },
    { id: 'strategies', label: 'Strategies', icon: Brain },
    { id: 'trades', label: 'Trade History', icon: TrendingUp },
    { id: 'risk', label: 'Risk Management', icon: Shield },
    { id: 'analytics', label: 'Performance', icon: BarChart3 },
    { id: 'users', label: 'User Management', icon: Users },
  ];

  const bottomNavItems = [
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const footerLinks = [
    { id: 'about', label: 'About', icon: Info, href: '/about' },
    { id: 'contact', label: 'Contact', icon: Mail, href: '/contact' },
    { id: 'terms', label: 'Terms', icon: FileText, href: '/terms' },
  ];

  const NavItem = ({ item, isActive = false }: { item: any; isActive?: boolean }) => (
    <Button
      variant={isActive ? "secondary" : "ghost"}
      className={cn(
        "w-full justify-start h-12",
        isCollapsed && "px-2",
        isActive && "bg-primary/10 text-primary"
      )}
      onClick={() => onSectionChange(item.id)}
    >
      <item.icon className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
      {!isCollapsed && <span>{item.label}</span>}
    </Button>
  );

  return (
    <div className={cn(
      "flex flex-col h-full bg-card border-r transition-all duration-300",
      isCollapsed ? "w-16" : "w-64"
    )}>
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-6 w-6 text-primary" />
              <span className="font-semibold">Owner Panel</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="h-8 w-8 p-0"
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 p-2 space-y-1">
        {mainNavItems.map((item) => (
          <NavItem
            key={item.id}
            item={item}
            isActive={activeSection === item.id}
          />
        ))}

        {/* Bottom Navigation */}
        <div className="pt-4 border-t space-y-1">
          {bottomNavItems.map((item) => (
            <NavItem
              key={item.id}
              item={item}
              isActive={activeSection === item.id}
            />
          ))}
        </div>
      </div>

      {/* Footer Links */}
      <div className="p-2 border-t space-y-1">
        {footerLinks.map((link) => (
          <Button
            key={link.id}
            variant="ghost"
            className={cn(
              "w-full justify-start h-10 text-sm text-muted-foreground",
              isCollapsed && "px-2"
            )}
            onClick={() => window.open(link.href, '_blank')}
          >
            <link.icon className={cn("h-4 w-4", isCollapsed ? "mx-auto" : "mr-3")} />
            {!isCollapsed && <span>{link.label}</span>}
          </Button>
        ))}

        {/* Sign Out Button */}
        <Button
          variant="ghost"
          className={cn(
            "w-full justify-start h-10 text-sm text-red-600 hover:text-red-700 hover:bg-red-50",
            isCollapsed && "px-2"
          )}
          onClick={signOut}
        >
          <LogOut className={cn("h-4 w-4", isCollapsed ? "mx-auto" : "mr-3")} />
          {!isCollapsed && <span>Sign Out</span>}
        </Button>
      </div>
    </div>
  );
}


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
  Cpu,
  Target,
  Menu,
  X
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface OwnerSidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export function OwnerSidebar({ activeSection, onSectionChange }: OwnerSidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { signOut, user } = useAuth();

  const mainNavItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard, color: 'text-blue-600' },
    { id: 'engine', label: 'Trading Engine', icon: Cpu, color: 'text-green-600' },
    { id: 'signals', label: 'Live Signals', icon: Activity, color: 'text-purple-600' },
    { id: 'strategies', label: 'Strategies', icon: Brain, color: 'text-orange-600' },
    { id: 'trades', label: 'Trade History', icon: TrendingUp, color: 'text-emerald-600' },
    { id: 'risk', label: 'Risk Management', icon: Shield, color: 'text-red-600' },
    { id: 'analytics', label: 'Performance', icon: BarChart3, color: 'text-indigo-600' },
    { id: 'users', label: 'User Management', icon: Users, color: 'text-pink-600' },
    { id: 'subscription', label: 'Subscription/Billing', icon: Target, color: 'text-yellow-600' },
    { id: 'settings', label: 'Settings', icon: Settings, color: 'text-gray-600' },
  ];

  const NavItem = ({ item, isActive = false }: { item: any; isActive?: boolean }) => (
    <Button
      variant={isActive ? "secondary" : "ghost"}
      className={cn(
        "w-full justify-start h-12 mb-1 transition-all duration-300 group relative",
        isCollapsed ? "px-3" : "px-4",
        isActive && "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-400 border-r-2 border-blue-500",
        !isActive && "hover:bg-gray-100 dark:hover:bg-gray-800 hover:scale-105"
      )}
      onClick={() => {
        onSectionChange(item.id);
        setIsMobileOpen(false);
      }}
    >
      <item.icon className={cn(
        "h-5 w-5 transition-colors duration-300",
        isCollapsed ? "mx-auto" : "mr-3",
        isActive ? item.color : "text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300"
      )} />
      {!isCollapsed && (
        <span className="font-medium transition-all duration-300">{item.label}</span>
      )}
      {isActive && !isCollapsed && (
        <div className="absolute right-2 w-2 h-2 rounded-full bg-blue-500"></div>
      )}
    </Button>
  );

  return (
    <>
      {/* Mobile Menu Button */}
      <Button
        variant="outline"
        size="icon"
        className="fixed top-4 left-4 z-50 md:hidden"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        {isMobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
      </Button>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setIsMobileOpen(false)} />
      )}

      {/* Sidebar */}
      <div className={cn(
        "flex flex-col h-full bg-card border-r transition-all duration-300 relative",
        isCollapsed ? "w-16" : "w-64",
        "md:relative md:translate-x-0",
        "fixed inset-y-0 left-0 z-50 md:z-auto",
        isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}>
        {/* Header */}
        <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
          <div className="flex items-center justify-between">
            {!isCollapsed && (
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg">
                  <Brain className="h-6 w-6 text-white" />
                </div>
                <div>
                  <span className="font-bold text-lg bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Owner Panel
                  </span>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-xs text-muted-foreground">Online</span>
                  </div>
                </div>
              </div>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="h-8 w-8 p-0 hidden md:flex hover:bg-white/50 dark:hover:bg-gray-800/50"
            >
              {isCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* User Info */}
        {!isCollapsed && (
          <div className="p-4 border-b bg-gray-50 dark:bg-gray-800/50">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                {user?.email?.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.email}</p>
                <Badge variant="outline" className="text-xs mt-1 border-green-200 text-green-700 bg-green-50 dark:border-green-800 dark:text-green-400 dark:bg-green-900/20">
                  Owner
                </Badge>
              </div>
            </div>
          </div>
        )}

        {/* Main Navigation */}
        <div className="flex-1 p-2 space-y-1 overflow-y-auto">
          <div className={cn("space-y-1", !isCollapsed && "px-2")}>
            {!isCollapsed && (
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-2">
                Main Menu
              </p>
            )}
            {mainNavItems.slice(0, 5).map((item) => (
              <NavItem
                key={item.id}
                item={item}
                isActive={activeSection === item.id}
              />
            ))}
          </div>

          <Separator className="my-4" />

          <div className={cn("space-y-1", !isCollapsed && "px-2")}>
            {!isCollapsed && (
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-2">
                Management
              </p>
            )}
            {mainNavItems.slice(5).map((item) => (
              <NavItem
                key={item.id}
                item={item}
                isActive={activeSection === item.id}
              />
            ))}
          </div>
        </div>

        {/* Sign Out Button */}
        <div className="p-2 border-t bg-gray-50 dark:bg-gray-800/50">
          <Button
            variant="ghost"
            className={cn(
              "w-full justify-start h-12 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-300",
              isCollapsed && "px-3"
            )}
            onClick={signOut}
          >
            <LogOut className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
            {!isCollapsed && <span className="font-medium">Sign Out</span>}
          </Button>
        </div>
      </div>
    </>
  );
}

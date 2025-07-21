
import { useState, useRef, useEffect } from "react";
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
  X,
  ChevronUp,
  ChevronDown
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
  const [showScrollUp, setShowScrollUp] = useState(false);
  const [showScrollDown, setShowScrollDown] = useState(false);
  const navRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkScroll = () => {
      if (navRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = navRef.current;
        setShowScrollUp(scrollTop > 8);
        setShowScrollDown(scrollTop < scrollHeight - clientHeight - 8);
      }
    };
    const navElement = navRef.current;
    if (navElement) {
      navElement.addEventListener('scroll', checkScroll);
      checkScroll();
      return () => navElement.removeEventListener('scroll', checkScroll);
    }
  }, [isCollapsed]);

  const scrollToTop = () => {
    if (navRef.current) {
      navRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };
  const scrollToBottom = () => {
    if (navRef.current) {
      navRef.current.scrollTo({ top: navRef.current.scrollHeight, behavior: 'smooth' });
    }
  };

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
        "w-full justify-start h-12 mb-2 transition-all duration-300 group relative rounded-lg",
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
        <span className="font-medium transition-all duration-300 text-sm">{item.label}</span>
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
        "flex flex-col h-screen max-h-screen overflow-hidden bg-card border-r transition-all duration-300 relative",
        isCollapsed ? "w-16" : "w-64",
        "md:relative md:translate-x-0",
        "fixed inset-y-0 left-0 z-50 md:z-auto",
        isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}>
        {/* Header */}
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

        {/* User Info - This section is removed and merged into the header */}

        {/* Main Navigation */}
        {/* Scroll Up Button */}
        {showScrollUp && (
          <div className="absolute top-2 left-1/2 transform -translate-x-1/2 z-10">
            <Button size="sm" variant="secondary" onClick={scrollToTop} className="h-6 w-6 p-0 rounded-full shadow-lg">
              <ChevronUp className="h-3 w-3" />
            </Button>
          </div>
        )}
        <div ref={navRef} className="flex-1 min-h-0 overflow-auto p-2 space-y-2 relative">
          <div className={cn("space-y-2", !isCollapsed && "px-2")}>
            {!isCollapsed && (
              <p className="text-sm font-medium text-muted-foreground mb-3 px-2">
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

          <div className={cn("space-y-2", !isCollapsed && "px-2")}>
            {!isCollapsed && (
              <p className="text-sm font-medium text-muted-foreground mb-3 px-2">
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
    </>
  );
}

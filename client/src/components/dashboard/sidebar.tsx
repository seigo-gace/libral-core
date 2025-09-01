import { 
  BarChart3, 
  Users, 
  Bell, 
  CreditCard, 
  Network, 
  Database, 
  Container, 
  Route,
  Menu,
  X,
  Star,
  Settings,
  Package
} from "lucide-react";
import { Link, useLocation } from "wouter";
import { useState } from "react";
import { Button } from "@/components/ui/button";

const navigation = [
  { name: 'HUDダッシュボード', href: '/dashboard-hud', icon: BarChart3 },
  { name: 'HUDユーザーメニュー', href: '/hud-user-menu', icon: Package },
  { name: '管理ダッシュボード', href: '/admin-dashboard', icon: Settings },
  { name: '開発ダッシュボード', href: '/dashboard', icon: Users },
  { name: 'ユーザーメニュー', href: '/user-menu', icon: Users },
  { name: '通信ゲートウェイ', href: '/communication-gateway', icon: Route },
  { name: 'ユーザー管理', href: '/user-management', icon: Users },
  { name: 'イベント管理', href: '/event-management', icon: Bell },
  { name: '決済管理', href: '/payment-management', icon: CreditCard },
  { name: '決済デモ', href: '/payment-demo', icon: Star },
  { name: 'APIハブ', href: '/api-hub', icon: Network },
  { name: 'データベース', href: '/database-management', icon: Database },
  { name: 'コンテナ管理', href: '/container-management', icon: Container },
];

export function Sidebar() {
  const [location] = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const renderNavigation = (isMobile = false) => (
    <nav className={`${isMobile ? 'mt-6' : 'mt-8'} flex-1 px-4 space-y-1`}>
      {navigation.map((item) => {
        const Icon = item.icon;
        const isActive = location === item.href || (location === '/' && item.href === '/dashboard');
        
        const content = (
          <div className={`${
            isActive
              ? 'bg-dark-700 text-dark-50'
              : 'text-dark-300 hover:bg-dark-700 hover:text-dark-50'
          } group flex items-center px-3 py-3 text-sm font-medium rounded-md cursor-pointer transition-colors`}>
            <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-primary' : 'text-dark-400'}`} />
            {item.name}
          </div>
        );

        if (item.href.startsWith('/')) {
          return (
            <Link key={item.name} href={item.href} onClick={isMobile ? closeMobileMenu : undefined}>
              {content}
            </Link>
          );
        } else {
          return (
            <div key={item.name} onClick={isMobile ? closeMobileMenu : undefined}>
              {content}
            </div>
          );
        }
      })}
    </nav>
  );

  return (
    <>
      {/* Mobile Menu Button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <Button
          onClick={toggleMobileMenu}
          variant="outline"
          size="sm"
          className="bg-dark-800 border-dark-600 text-dark-50 hover:bg-dark-700"
          data-testid="button-mobile-menu"
        >
          <Menu className="h-4 w-4" />
        </Button>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-dark-900 bg-opacity-50" onClick={closeMobileMenu} />
      )}

      {/* Mobile Sidebar */}
      <div className={`
        md:hidden fixed inset-y-0 left-0 z-50 w-80 transform transition-transform duration-300 ease-in-out
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full bg-dark-800 border-r border-dark-700">
          {/* Mobile Header */}
          <div className="flex items-center justify-between p-4 border-b border-dark-700">
            <Link href="/dashboard" onClick={closeMobileMenu}>
              <div className="flex items-center cursor-pointer">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <Container className="h-4 w-4 text-white" />
                </div>
                <h1 className="ml-3 text-xl font-bold text-dark-50">Libral Core</h1>
              </div>
            </Link>
            <Button
              onClick={closeMobileMenu}
              variant="ghost"
              size="sm"
              className="text-dark-400 hover:text-dark-50"
              data-testid="button-close-mobile-menu"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          
          {renderNavigation(true)}
          
          {/* Mobile System Status */}
          <div className="flex-shrink-0 border-t border-dark-700 p-4">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-success rounded-full mr-2"></div>
              <span className="text-sm text-dark-300">システム正常</span>
            </div>
          </div>
        </div>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col">
        <div className="flex flex-col flex-grow pt-5 overflow-y-auto bg-dark-800 border-r border-dark-700">
          <div className="flex items-center flex-shrink-0 px-4">
            <Link href="/dashboard">
              <div className="flex items-center cursor-pointer">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <Container className="h-4 w-4 text-white" />
                </div>
                <h1 className="ml-3 text-xl font-bold text-dark-50">Libral Core</h1>
              </div>
            </Link>
          </div>
          
          {renderNavigation()}
          
          {/* Desktop System Status */}
          <div className="flex-shrink-0 flex border-t border-dark-700 p-4">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-success rounded-full mr-2"></div>
              <span className="text-sm text-dark-300">システム正常</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

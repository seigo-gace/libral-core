import { 
  BarChart3, 
  Users, 
  Bell, 
  CreditCard, 
  Network, 
  Database, 
  Container, 
  Route,
  Sparkles
} from "lucide-react";
import { Link, useLocation } from "wouter";

const navigation = [
  { name: 'ダッシュボード', href: '/dashboard', icon: BarChart3 },
  { name: 'スタンプ作成', href: '/stamp-creator', icon: Sparkles },
  { name: '通信ゲートウェイ', href: '#', icon: Route },
  { name: 'ユーザー管理', href: '#', icon: Users },
  { name: 'イベント管理', href: '#', icon: Bell },
  { name: '決済管理', href: '#', icon: CreditCard },
  { name: 'APIハブ', href: '#', icon: Network },
  { name: 'データベース', href: '#', icon: Database },
  { name: 'コンテナ管理', href: '#', icon: Container },
];

export function Sidebar() {
  const [location] = useLocation();

  return (
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
        
        <nav className="mt-8 flex-1 px-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location === item.href || (location === '/' && item.href === '/dashboard');
            
            const content = (
              <div className={`${
                isActive
                  ? 'bg-dark-700 text-dark-50'
                  : 'text-dark-300 hover:bg-dark-700 hover:text-dark-50'
              } group flex items-center px-2 py-2 text-sm font-medium rounded-md cursor-pointer`}>
                <Icon className={`mr-3 h-4 w-4 ${isActive ? 'text-primary' : 'text-dark-400'}`} />
                {item.name}
              </div>
            );

            if (item.href.startsWith('/')) {
              return (
                <Link key={item.name} href={item.href}>
                  {content}
                </Link>
              );
            } else {
              return (
                <div key={item.name}>
                  {content}
                </div>
              );
            }
          })}
        </nav>
        
        {/* System Status Indicator */}
        <div className="flex-shrink-0 flex border-t border-dark-700 p-4">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-success rounded-full mr-2"></div>
            <span className="text-sm text-dark-300">システム正常</span>
          </div>
        </div>
      </div>
    </div>
  );
}

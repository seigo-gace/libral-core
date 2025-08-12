import { 
  BarChart3, 
  Users, 
  Bell, 
  CreditCard, 
  Network, 
  Database, 
  Container, 
  Route
} from "lucide-react";

const navigation = [
  { name: 'ダッシュボード', href: '#', icon: BarChart3, current: true },
  { name: '通信ゲートウェイ', href: '#', icon: Route, current: false },
  { name: 'ユーザー管理', href: '#', icon: Users, current: false },
  { name: 'イベント管理', href: '#', icon: Bell, current: false },
  { name: '決済管理', href: '#', icon: CreditCard, current: false },
  { name: 'APIハブ', href: '#', icon: Network, current: false },
  { name: 'データベース', href: '#', icon: Database, current: false },
  { name: 'コンテナ管理', href: '#', icon: Container, current: false },
];

export function Sidebar() {
  return (
    <div className="hidden md:flex md:w-64 md:flex-col">
      <div className="flex flex-col flex-grow pt-5 overflow-y-auto bg-dark-800 border-r border-dark-700">
        <div className="flex items-center flex-shrink-0 px-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Container className="h-4 w-4 text-white" />
            </div>
            <h1 className="ml-3 text-xl font-bold text-dark-50">Libral Core</h1>
          </div>
        </div>
        
        <nav className="mt-8 flex-1 px-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <a
                key={item.name}
                href={item.href}
                className={`${
                  item.current
                    ? 'bg-dark-700 text-dark-50'
                    : 'text-dark-300 hover:bg-dark-700 hover:text-dark-50'
                } group flex items-center px-2 py-2 text-sm font-medium rounded-md`}
              >
                <Icon className="text-dark-400 mr-3 h-4 w-4" />
                {item.name}
              </a>
            );
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

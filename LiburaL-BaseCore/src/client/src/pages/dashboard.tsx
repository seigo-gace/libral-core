import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { HudCard, HudButton, HexPanel, RadarDisplay, MetricPanel, WarningStrip } from "@/components/ui/hud-elements";
import { 
  Activity, 
  Users, 
  Zap, 
  Server, 
  Database, 
  Shield,
  Cpu,
  MemoryStick,
  Wifi,
  AlertTriangle,
  Settings,
  RefreshCw
} from "lucide-react";

interface SystemMetrics {
  cpuUsage: string;
  memoryUsage: string;
  activeUsers: string;
  apiRequestsPerMinute: string;
}

export default function Dashboard() {
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const { data: metrics } = useQuery<SystemMetrics>({
    queryKey: ['/api/system/metrics'],
    refetchInterval: 5000
  });

  const { data: modules } = useQuery({
    queryKey: ['/api/modules'],
    refetchInterval: 10000
  });

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const coreModules = [
    { id: 'aegis-pgp', name: '暗号化', icon: <Shield className="w-4 h-4" />, status: 'active' },
    { id: 'communication', name: '通信', icon: <Wifi className="w-4 h-4" />, status: 'active' },
    { id: 'database', name: 'DB', icon: <Database className="w-4 h-4" />, status: 'active' },
    { id: 'events', name: 'イベント', icon: <Activity className="w-4 h-4" />, status: 'active' },
    { id: 'payment', name: '決済', icon: <Zap className="w-4 h-4" />, status: 'active' },
    { id: 'users', name: 'ユーザー', icon: <Users className="w-4 h-4" />, status: 'active' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-gray-900 text-white overflow-hidden">
      {/* Mobile-First HUD Interface */}
      <div className="p-4 space-y-4 max-w-md mx-auto lg:max-w-6xl">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold text-cyan-400 font-mono">LIBRAL CORE</h1>
            <p className="text-xs text-gray-400">システム監視コンソール</p>
          </div>
          <HudButton 
            onClick={handleRefresh} 
            disabled={isRefreshing}
            variant="primary"
            size="sm"
            data-testid="button-refresh-hud"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </HudButton>
        </div>

        {/* Left Panel - Hexagonal Module Status */}
        <div className="lg:flex lg:space-x-6">
          <div className="lg:w-20 mb-4 lg:mb-0">
            <div className="flex flex-row lg:flex-col space-x-2 lg:space-x-0 lg:space-y-2 overflow-x-auto lg:overflow-x-visible">
              {coreModules.map((module) => (
                <HexPanel 
                  key={module.id} 
                  active={module.status === 'active'}
                  size="sm"
                  className="flex-shrink-0"
                >
                  <div className="text-xs text-center">
                    {module.icon}
                    <div className="text-[10px] mt-1">{module.name}</div>
                  </div>
                </HexPanel>
              ))}
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="flex-1 space-y-4">
            
            {/* System Metrics Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <HudCard variant="primary">
                <MetricPanel
                  title="CPU使用率"
                  value={metrics?.cpuUsage || '0'}
                  unit="%"
                  trend="stable"
                  color="#00bcd4"
                  icon={<Cpu className="w-4 h-4" />}
                />
              </HudCard>
              
              <HudCard variant="secondary">
                <MetricPanel
                  title="メモリ"
                  value={metrics?.memoryUsage || '0'}
                  unit="%"
                  trend="up"
                  color="#3f51b5"
                  icon={<MemoryStick className="w-4 h-4" />}
                />
              </HudCard>
              
              <HudCard variant="info" className="col-span-2 lg:col-span-1">
                <MetricPanel
                  title="アクティブユーザー"
                  value={metrics?.activeUsers || '0'}
                  trend="up"
                  color="#9c27b0"
                  icon={<Users className="w-4 h-4" />}
                />
              </HudCard>
              
              <HudCard variant="primary" className="hidden lg:block">
                <MetricPanel
                  title="API呼出/分"
                  value={metrics?.apiRequestsPerMinute || '0'}
                  trend="stable"
                  color="#00bcd4"
                  icon={<Activity className="w-4 h-4" />}
                />
              </HudCard>
            </div>

            {/* Main Display Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              
              {/* Radar Display */}
              <HudCard variant="primary" className="flex flex-col items-center justify-center p-6">
                <div className="mb-4">
                  <RadarDisplay progress={85} size={120} color="#00bcd4" />
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-cyan-400">システム正常</div>
                  <div className="text-xs text-gray-400">稼働率 99.8%</div>
                </div>
              </HudCard>
              
              {/* Status Panel */}
              <HudCard variant="secondary" className="lg:col-span-2">
                <div className="space-y-3">
                  <h3 className="text-lg font-bold text-blue-400 mb-4">{">>> HUD風近未来素材 <<<"}</h3>
                  
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { label: 'セキュリティ', status: '保護済み', color: 'text-green-400' },
                      { label: 'データ主権', status: '維持', color: 'text-cyan-400' },
                      { label: '暗号化', status: 'AES-256', color: 'text-blue-400' },
                      { label: 'Telegram統合', status: '接続中', color: 'text-purple-400' },
                    ].map((item, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-white/5 rounded">
                        <span className="text-sm text-gray-300">{item.label}</span>
                        <span className={`text-xs font-mono ${item.color}`}>{item.status}</span>
                      </div>
                    ))}
                  </div>
                  
                  {/* Progress Bars */}
                  <div className="space-y-2 mt-4">
                    {[
                      { label: 'システム負荷', progress: 23 },
                      { label: 'ネットワーク', progress: 67 },
                      { label: 'ストレージ', progress: 45 },
                    ].map((item, index) => (
                      <div key={index} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">{item.label}</span>
                          <span className="text-cyan-400">{item.progress}%</span>
                        </div>
                        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500"
                            style={{ width: `${item.progress}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </HudCard>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <HudButton 
                variant="primary" 
                onClick={() => window.location.href = '/admin-dashboard'}
                data-testid="button-admin-dashboard"
              >
                <Settings className="w-4 h-4 mr-2" />
                管理
              </HudButton>
              <HudButton 
                variant="secondary" 
                onClick={() => window.location.href = '/hud-user-menu'}
                data-testid="button-user-menu"
              >
                <Users className="w-4 h-4 mr-2" />
                ユーザー
              </HudButton>
              <HudButton variant="primary" data-testid="button-analytics">
                <Activity className="w-4 h-4 mr-2" />
                分析
              </HudButton>
              <HudButton variant="secondary" data-testid="button-settings">
                <Server className="w-4 h-4 mr-2" />
                設定
              </HudButton>
            </div>

          </div>
        </div>

        {/* Warning Strip */}
        <WarningStrip>
          <span className="text-sm font-mono">システム監視中 - 全モジュール正常動作</span>
        </WarningStrip>

      </div>
    </div>
  );
}

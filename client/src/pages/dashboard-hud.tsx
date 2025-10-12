import { useState, useEffect } from "react";
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
  RefreshCw,
  Terminal
} from "lucide-react";

interface SystemMetrics {
  cpuUsage: string;
  memoryUsage: string;
  activeUsers: string;
  apiRequestsPerMinute: string;
}

export default function DashboardHud() {
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [doorOpen, setDoorOpen] = useState(false);

  const { data: metrics } = useQuery<SystemMetrics>({
    queryKey: ['/api/system/metrics'],
    refetchInterval: 5000
  });

  useEffect(() => {
    setTimeout(() => setDoorOpen(true), 100);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const handleModuleClick = (moduleId: string) => {
    switch (moduleId) {
      case 'aegis-pgp':
        window.location.href = '/gpg-config';
        break;
      case 'communication':
        window.location.href = '/communication-gateway';
        break;
      case 'database':
        window.location.href = '/database-management';
        break;
      case 'events':
        window.location.href = '/event-management';
        break;
      case 'payment':
        window.location.href = '/payment-management';
        break;
      case 'users':
        window.location.href = '/user-management';
        break;
      case 'c3-apps':
        window.location.href = '/c3/apps';
        break;
      case 'c3-console':
        window.location.href = '/c3/console';
        break;
      default:
        alert(`${moduleId}モジュールの管理画面に移動します`);
    }
  };

  const coreModules = [
    { id: 'aegis-pgp', name: '暗号化', icon: <Shield className="w-4 h-4" />, status: 'active' },
    { id: 'communication', name: '通信', icon: <Wifi className="w-4 h-4" />, status: 'active' },
    { id: 'database', name: 'DB', icon: <Database className="w-4 h-4" />, status: 'active' },
    { id: 'events', name: 'イベント', icon: <Activity className="w-4 h-4" />, status: 'active' },
    { id: 'payment', name: '決済', icon: <Zap className="w-4 h-4" />, status: 'active' },
    { id: 'users', name: 'ユーザー', icon: <Users className="w-4 h-4" />, status: 'active' },
    { id: 'c3-apps', name: 'C3 Apps', icon: <Terminal className="w-4 h-4" />, status: 'active' },
    { id: 'c3-console', name: 'Console', icon: <Server className="w-4 h-4" />, status: 'active' },
  ];

  return (
    <div className="relative min-h-screen bg-[#080A0F] overflow-hidden">
      {/* Grid Background */}
      <div className="absolute inset-0 opacity-10 pointer-events-none" 
           style={{ 
             backgroundImage: `
               linear-gradient(#00FFD1 1px, transparent 1px),
               linear-gradient(90deg, #00FFD1 1px, transparent 1px)
             `,
             backgroundSize: '20px 20px'
           }} 
      />
      
      {/* Noise Texture */}
      <div className="absolute inset-0 opacity-5 pointer-events-none"
           style={{
             backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' /%3E%3C/svg%3E")`
           }}
      />

      {/* Door Animation - Left */}
      <div 
        className={`door-left fixed left-0 top-0 h-full w-1/2 bg-[#080A0F] z-50 transition-transform duration-[800ms] ease-[cubic-bezier(0.25,1,0.5,1)] ${
          doorOpen ? '-translate-x-full' : 'translate-x-0'
        }`}
        style={{
          clipPath: 'polygon(0 0, 85% 0, 100% 50%, 85% 100%, 0 100%)',
          borderRight: '2px solid #00FFD1',
          boxShadow: doorOpen ? 'none' : '0 0 30px #00FFD1'
        }}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-[#00FFD1] text-6xl md:text-8xl font-bold animate-pulse" 
               style={{ fontFamily: 'Major Mono Display, monospace' }}>L</div>
        </div>
      </div>

      {/* Door Animation - Right */}
      <div 
        className={`door-right fixed right-0 top-0 h-full w-1/2 bg-[#080A0F] z-50 transition-transform duration-[800ms] ease-[cubic-bezier(0.25,1,0.5,1)] ${
          doorOpen ? 'translate-x-full' : 'translate-x-0'
        }`}
        style={{
          clipPath: 'polygon(15% 0, 100% 0, 100% 100%, 15% 100%, 0% 50%)',
          borderLeft: '2px solid #00FFD1',
          boxShadow: doorOpen ? 'none' : '0 0 30px #00FFD1'
        }}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-[#00FFD1] text-6xl md:text-8xl font-bold animate-pulse"
               style={{ fontFamily: 'Major Mono Display, monospace' }}>C</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen text-white" style={{ fontFamily: 'Share Tech Mono, monospace' }}>
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#00FFD1] to-transparent" />
        
        {/* Mobile: Single Column Layout, Desktop: Multi-column Layout */}
        <div className="p-4 space-y-4 max-w-md mx-auto lg:max-w-7xl">
          
          {/* Header */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 md:w-12 md:h-12 border-2 border-[#00FFD1] flex items-center justify-center"
                   style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' }}>
                <Terminal className="text-[#00FFD1] w-5 h-5 md:w-6 md:h-6" />
              </div>
              <div>
                <h1 className="text-lg md:text-2xl font-bold text-[#00FFD1] tracking-[0.2em]" 
                    style={{ fontFamily: 'Major Mono Display, monospace' }}>LIBRAL CORE</h1>
                <p className="text-[10px] md:text-xs text-[#00FFD1]/60 tracking-[0.3em]">NEON CYBERPUNK HUD - システム監視コンソール</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-[#00FFD1]/60 text-xs md:text-sm tracking-wider">[系統-連続]</div>
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
          </div>

          {/* Mobile: Horizontal scroll, Desktop: Vertical sidebar */}
          <div className="flex flex-col lg:flex-row lg:space-x-6">
            {/* Left Panel - Hexagonal Module Status */}
            <div className="mb-4 lg:mb-0 lg:w-24">
              <div className="flex flex-row lg:flex-col gap-2 overflow-x-auto lg:overflow-x-visible pb-2 lg:pb-0">
                {coreModules.map((module) => (
                  <HexPanel 
                    key={module.id} 
                    active={module.status === 'active'}
                    size="sm"
                    className="flex-shrink-0 cursor-pointer hover:scale-105 transition-transform border border-[#00FFD1]/50 hover:border-[#00FFD1]"
                    onClick={() => handleModuleClick(module.id)}
                    data-testid={`hex-${module.id}`}
                  >
                    <div className="text-xs text-center text-[#00FFD1]">
                      {module.icon}
                      <div className="text-[9px] md:text-[10px] mt-1">{module.name}</div>
                    </div>
                  </HexPanel>
                ))}
              </div>
            </div>

            {/* Main Content Grid */}
            <div className="flex-1 space-y-4">
              
              {/* System Metrics Row - Mobile: 2 cols, Desktop: 4 cols */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
                <HudCard variant="primary" className="border-[#00FFD1]/50">
                  <MetricPanel
                    title="CPU使用率"
                    value={metrics?.cpuUsage || '0'}
                    unit="%"
                    trend="stable"
                    color="#00FFD1"
                    icon={<Cpu className="w-4 h-4" />}
                  />
                </HudCard>
                
                <HudCard variant="secondary" className="border-[#00FFD1]/50">
                  <MetricPanel
                    title="メモリ"
                    value={metrics?.memoryUsage || '0'}
                    unit="%"
                    trend="up"
                    color="#00FFD1"
                    icon={<MemoryStick className="w-4 h-4" />}
                  />
                </HudCard>
                
                <HudCard variant="info" className="col-span-2 lg:col-span-1 border-[#00FFD1]/50">
                  <MetricPanel
                    title="アクティブユーザー"
                    value={metrics?.activeUsers || '0'}
                    trend="up"
                    color="#00FFD1"
                    icon={<Users className="w-4 h-4" />}
                  />
                </HudCard>
                
                <HudCard variant="primary" className="hidden lg:block border-[#00FFD1]/50">
                  <MetricPanel
                    title="API呼出/分"
                    value={metrics?.apiRequestsPerMinute || '0'}
                    trend="stable"
                    color="#00FFD1"
                    icon={<Activity className="w-4 h-4" />}
                  />
                </HudCard>
              </div>

              {/* Main Display Area - Mobile: Stack, Desktop: 3-column grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                
                {/* Radar Display */}
                <HudCard variant="primary" className="flex flex-col items-center justify-center p-6 border-[#00FFD1]/50 bg-[#00FFD1]/5">
                  <div className="mb-4">
                    <RadarDisplay progress={85} size={120} color="#00FFD1" />
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-[#00FFD1]">システム正常</div>
                    <div className="text-xs text-[#00FFD1]/60">稼働率 99.8%</div>
                  </div>
                </HudCard>
                
                {/* Status Panel */}
                <HudCard variant="secondary" className="lg:col-span-2 border-[#00FFD1]/50 bg-[#00FFD1]/5">
                  <div className="space-y-3">
                    <h3 className="text-base md:text-lg font-bold text-[#00FFD1] mb-4" 
                        style={{ fontFamily: 'Major Mono Display, monospace' }}>
                      NEON CYBERPUNK HUD
                    </h3>
                    
                    {/* Mobile: 1 col, Desktop: 2 cols */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {[
                        { label: 'セキュリティ', status: '保護済み', color: 'text-[#00FFD1]' },
                        { label: 'データ主権', status: '維持', color: 'text-[#00FFD1]' },
                        { label: '暗号化', status: 'AES-256', color: 'text-[#00FFD1]' },
                        { label: 'Telegram統合', status: '接続中', color: 'text-[#00FFD1]' },
                      ].map((item, index) => (
                        <div key={index} 
                             className="flex justify-between items-center p-3 bg-black/30 border border-[#00FFD1]/30 rounded"
                             data-testid={`status-${item.label}`}>
                          <span className="text-xs md:text-sm text-[#00FFD1]/80">{item.label}</span>
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
                            <span className="text-[#00FFD1]/80">{item.label}</span>
                            <span className="text-[#00FFD1]">{item.progress}%</span>
                          </div>
                          <div className="h-2 bg-[#00FFD1]/10 border border-[#00FFD1]/30 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-[#00FFD1] rounded-full transition-all duration-500"
                              style={{ 
                                width: `${item.progress}%`,
                                boxShadow: '0 0 10px #00FFD1'
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </HudCard>
              </div>

              {/* Action Buttons - Mobile: 2 cols, Desktop: 4 cols */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <HudButton 
                  variant="primary" 
                  onClick={() => window.location.href = '/admin-dashboard'}
                  className="border-[#00FFD1]/50 hover:border-[#00FFD1] text-[#00FFD1]"
                  data-testid="button-admin-dashboard"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  <span className="text-xs md:text-sm">管理</span>
                </HudButton>
                <HudButton 
                  variant="secondary" 
                  onClick={() => window.location.href = '/hud-user-menu'}
                  className="border-[#00FFD1]/50 hover:border-[#00FFD1] text-[#00FFD1]"
                  data-testid="button-user-menu"
                >
                  <Users className="w-4 h-4 mr-2" />
                  <span className="text-xs md:text-sm">ユーザー</span>
                </HudButton>
                <HudButton 
                  variant="primary" 
                  onClick={() => window.location.href = '/analytics'}
                  className="border-[#00FFD1]/50 hover:border-[#00FFD1] text-[#00FFD1]"
                  data-testid="button-analytics"
                >
                  <Activity className="w-4 h-4 mr-2" />
                  <span className="text-xs md:text-sm">分析</span>
                </HudButton>
                <HudButton 
                  variant="secondary" 
                  onClick={() => window.location.href = '/settings'}
                  className="border-[#00FFD1]/50 hover:border-[#00FFD1] text-[#00FFD1]"
                  data-testid="button-settings"
                >
                  <Server className="w-4 h-4 mr-2" />
                  <span className="text-xs md:text-sm">設定</span>
                </HudButton>
              </div>

            </div>
          </div>

          {/* Warning Strip */}
          <WarningStrip>
            <span className="text-xs md:text-sm font-mono text-[#00FFD1]">
              システム監視中 - 全モジュール正常動作 - LIBRAL CORE v1.0
            </span>
          </WarningStrip>

        </div>

        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#00FFD1] to-transparent" />
      </div>
    </div>
  );
}

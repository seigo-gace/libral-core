import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FuturisticCard, MetricDisplay, ProgressRing } from "@/components/ui/futuristic-card";
import { 
  Activity, 
  Users, 
  Zap, 
  Server, 
  Database, 
  AlertCircle, 
  Cpu, 
  MemoryStick, 
  HardDrive, 
  Wifi, 
  Settings, 
  Shield, 
  Bot, 
  Link as LinkIcon,
  RefreshCw,
  ChevronRight,
  Info,
  Play,
  Pause,
  AlertTriangle
} from "lucide-react";

interface SystemMetrics {
  cpuUsage: string;
  memoryUsage: string;
  activeUsers: string;
  apiRequestsPerMinute: string;
}

interface ModuleInfo {
  id: string;
  name: string;
  version: string;
  status: 'active' | 'inactive' | 'error' | 'updating';
  description: string;
  uptime: string;
  lastUpdate: string;
  dependencies: string[];
}

const moduleDetails: Record<string, ModuleInfo> = {
  'communication-gateway': {
    id: 'communication-gateway',
    name: '通信ゲートウェイ',
    version: '2.1.0',
    status: 'active',
    description: 'マルチプロトコル通信管理システム。Telegram、Email、Webhookを統合管理',
    uptime: '99.9%',
    lastUpdate: '2024-12-20',
    dependencies: ['redis', 'telegram-api', 'smtp-server']
  },
  'user-management': {
    id: 'user-management',
    name: 'ユーザー管理',
    version: '1.8.3',
    status: 'active',
    description: 'Telegram個人サーバー統合ユーザー管理システム',
    uptime: '99.8%',
    lastUpdate: '2024-12-18',
    dependencies: ['postgresql', 'telegram-auth']
  },
  'event-management': {
    id: 'event-management',
    name: 'イベント管理',
    version: '3.0.1',
    status: 'active',
    description: 'リアルタイムイベント処理と個人サーバー管理ボタン',
    uptime: '99.7%',
    lastUpdate: '2024-12-19',
    dependencies: ['websocket', 'redis', 'telegram-bot']
  },
  'payment-management': {
    id: 'payment-management',
    name: '決済管理',
    version: '2.2.4',
    status: 'active',
    description: 'Telegram Stars統合決済システム。暗号化請求ログ管理',
    uptime: '99.9%',
    lastUpdate: '2024-12-21',
    dependencies: ['telegram-payments', 'crypto-service']
  },
  'api-hub': {
    id: 'api-hub',
    name: 'APIハブ',
    version: '1.6.2',
    status: 'active',
    description: '暗号化API認証情報管理とコスト追跡システム',
    uptime: '99.8%',
    lastUpdate: '2024-12-20',
    dependencies: ['vault-service', 'metrics-collector']
  },
  'database-management': {
    id: 'database-management',
    name: 'データベース管理',
    version: '2.5.1',
    status: 'active',
    description: 'PostgreSQL、Redis、Neonデータベース統合管理',
    uptime: '99.9%',
    lastUpdate: '2024-12-19',
    dependencies: ['postgresql', 'redis', 'neon-api']
  },
  'container-management': {
    id: 'container-management',
    name: 'コンテナ管理',
    version: '1.4.0',
    status: 'inactive',
    description: 'Dockerコンテナとマイクロサービス運用管理',
    uptime: '98.5%',
    lastUpdate: '2024-12-15',
    dependencies: ['docker-api', 'kubernetes']
  },
  'aegis-pgp': {
    id: 'aegis-pgp',
    name: 'Aegis-PGP暗号化',
    version: '3.1.2',
    status: 'active',
    description: 'エンタープライズ級GPG暗号化システム（SEIPDv2/AES-256-OCB）',
    uptime: '99.9%',
    lastUpdate: '2024-12-21',
    dependencies: ['gpg-core', 'secure-vault']
  }
};

export default function AdminDashboard() {
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

  // queryClientをインポート
  const queryClient = useQueryClient();

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // 実際にAPIを呼び出してデータを更新
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['/api/system/metrics'] }),
        queryClient.invalidateQueries({ queryKey: ['/api/modules'] })
      ]);
    } catch (error) {
      console.error('System refresh failed:', error);
    } finally {
      setTimeout(() => setIsRefreshing(false), 1000);
    }
  };

  const handleModuleAction = async (moduleId: string, action: string) => {
    try {
      let endpoint = '';
      let method = 'GET';
      
      switch (action) {
        case 'logs':
          // ログページにリダイレクト
          window.location.href = `/logs/${moduleId}`;
          return;
        case 'config':
          // 設定ページにリダイレクト
          if (moduleId === 'aegis-pgp') {
            window.location.href = '/gpg-config';
          } else if (moduleId === 'communication-gateway') {
            window.location.href = '/communication-gateway';
          } else if (moduleId === 'user-management') {
            window.location.href = '/user-management';
          } else if (moduleId === 'event-management') {
            window.location.href = '/event-management';
          } else if (moduleId === 'payment-management') {
            window.location.href = '/payment-management';
          } else if (moduleId === 'api-hub') {
            window.location.href = '/api-hub';
          } else if (moduleId === 'database-management') {
            window.location.href = '/database-management';
          } else if (moduleId === 'container-management') {
            window.location.href = '/container-management';
          } else {
            window.location.href = '/settings';
          }
          return;
        case 'restart':
          endpoint = `/api/modules/${moduleId}/restart`;
          method = 'POST';
          break;
        case 'start':
          endpoint = `/api/modules/${moduleId}/start`;
          method = 'POST';
          break;
      }

      if (endpoint) {
        const response = await fetch(endpoint, { method });
        if (response.ok) {
          alert(`${action}操作が成功しました`);
          queryClient.invalidateQueries({ queryKey: ['/api/modules'] });
        } else {
          throw new Error(`${action}操作が失敗しました`);
        }
      }
    } catch (error) {
      console.error(`Module ${action} failed:`, error);
      alert(`操作中にエラーが発生しました: ${error}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green';
      case 'inactive': return 'yellow';
      case 'error': return 'red';
      case 'updating': return 'blue';
      default: return 'blue';
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'inactive': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'updating': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Play className="h-4 w-4" />;
      case 'inactive': return <Pause className="h-4 w-4" />;
      case 'error': return <AlertTriangle className="h-4 w-4" />;
      case 'updating': return <RefreshCw className="h-4 w-4 animate-spin" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  const renderModuleDetail = (moduleId: string) => {
    const module = moduleDetails[moduleId];
    if (!module) return null;

    return (
      <FuturisticCard className="mt-4" glowColor={getStatusColor(module.status)} active={true}>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg bg-${getStatusColor(module.status)}-500/20`}>
                {getStatusIcon(module.status)}
              </div>
              <div>
                <CardTitle className="flex items-center space-x-2">
                  <span>{module.name}</span>
                  <Badge variant="outline">v{module.version}</Badge>
                </CardTitle>
                <CardDescription>ID: {module.id}</CardDescription>
              </div>
            </div>
            <Badge className={getStatusBadgeClass(module.status)}>
              {module.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">{module.description}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricDisplay
              value={module.uptime}
              label="UPTIME"
              icon={<Activity className="h-4 w-4" />}
              color={getStatusColor(module.status)}
            />
            <MetricDisplay
              value={module.lastUpdate}
              label="LAST UPDATE"
              icon={<RefreshCw className="h-4 w-4" />}
              color="blue"
            />
            <MetricDisplay
              value={module.dependencies.length.toString()}
              label="DEPENDENCIES"
              icon={<LinkIcon className="h-4 w-4" />}
              color="purple"
            />
          </div>

          <div>
            <h4 className="font-medium mb-2 text-sm uppercase tracking-wider">Dependencies:</h4>
            <div className="flex flex-wrap gap-2">
              {module.dependencies.map((dep, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {dep}
                </Badge>
              ))}
            </div>
          </div>

          <div className="flex space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => handleModuleAction(module.id, 'logs')}
              data-testid={`button-logs-${module.id}`}
            >
              <Activity className="h-3 w-3 mr-1" />
              ログ
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => handleModuleAction(module.id, 'config')}
              data-testid={`button-config-${module.id}`}
            >
              <Settings className="h-3 w-3 mr-1" />
              設定
            </Button>
            {module.status === 'active' ? (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => handleModuleAction(module.id, 'restart')}
                data-testid={`button-restart-${module.id}`}
              >
                <RefreshCw className="h-3 w-3 mr-1" />
                再起動
              </Button>
            ) : (
              <Button 
                size="sm" 
                onClick={() => handleModuleAction(module.id, 'start')}
                data-testid={`button-start-${module.id}`}
              >
                <Play className="h-3 w-3 mr-1" />
                開始
              </Button>
            )}
          </div>
        </CardContent>
      </FuturisticCard>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-black/20">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white">
                LIBRAL CORE
                <span className="text-blue-400 ml-2">ADMIN</span>
              </h1>
              <p className="text-blue-200/80 text-sm sm:text-base">
                システム管理 & トラブルシューティング コンソール
              </p>
            </div>
            <Button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="bg-blue-600 hover:bg-blue-700 text-white"
              data-testid="button-refresh-admin"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              システム更新
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* System Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <FuturisticCard glowColor="blue" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={`${metrics?.cpuUsage || '0'}%`}
                label="CPU USAGE"
                icon={<Cpu className="h-5 w-5" />}
                color="blue"
                trend={parseInt(metrics?.cpuUsage || '0') > 50 ? 'up' : 'neutral'}
              />
            </CardContent>
          </FuturisticCard>

          <FuturisticCard glowColor="green" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={`${metrics?.memoryUsage || '0'}%`}
                label="MEMORY"
                icon={<MemoryStick className="h-5 w-5" />}
                color="green"
                trend={parseInt(metrics?.memoryUsage || '0') > 70 ? 'up' : 'neutral'}
              />
            </CardContent>
          </FuturisticCard>

          <FuturisticCard glowColor="purple" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={metrics?.activeUsers || '0'}
                label="ACTIVE USERS"
                icon={<Users className="h-5 w-5" />}
                color="purple"
                trend="up"
              />
            </CardContent>
          </FuturisticCard>

          <FuturisticCard glowColor="yellow" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={metrics?.apiRequestsPerMinute || '0'}
                label="API REQ/MIN"
                icon={<Activity className="h-5 w-5" />}
                color="yellow"
                trend="neutral"
              />
            </CardContent>
          </FuturisticCard>
        </div>

        {/* Module Management */}
        <FuturisticCard glowColor="blue" active={true}>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Bot className="h-5 w-5" />
              <span>モジュール管理</span>
            </CardTitle>
            <CardDescription className="text-blue-200/80">
              システムモジュールの状態監視と管理介入
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.values(moduleDetails).map((module) => (
              <div key={module.id}>
                <div className="flex items-center justify-between p-3 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10 hover:bg-white/10 transition-all">
                  <div className="flex items-center space-x-3 flex-1">
                    <div className={`p-2 rounded-lg bg-${getStatusColor(module.status)}-500/20`}>
                      {getStatusIcon(module.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-white truncate">{module.name}</h3>
                      <p className="text-sm text-gray-300 truncate">
                        v{module.version} • {module.status} • {module.uptime}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={getStatusBadgeClass(module.status)}>
                      {module.status}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedModule(selectedModule === module.id ? null : module.id)}
                      className="text-white hover:bg-white/10"
                      data-testid={`button-details-${module.id}`}
                    >
                      <ChevronRight className={`h-4 w-4 transition-transform ${selectedModule === module.id ? 'rotate-90' : ''}`} />
                    </Button>
                  </div>
                </div>
                {selectedModule === module.id && renderModuleDetail(module.id)}
              </div>
            ))}
          </CardContent>
        </FuturisticCard>

        {/* System Health */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FuturisticCard glowColor="green" active={true}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-white">
                <Shield className="h-5 w-5" />
                <span>セキュリティ状態</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-center">
                <ProgressRing progress={98} size={100} color="#10b981">
                  <div className="text-center">
                    <div className="text-xl font-bold text-white">98%</div>
                    <div className="text-xs text-gray-300">安全</div>
                  </div>
                </ProgressRing>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between text-gray-300">
                  <span>Aegis-PGP暗号化:</span>
                  <span className="text-green-400">有効</span>
                </div>
                <div className="flex justify-between text-gray-300">
                  <span>Telegram個人サーバー:</span>
                  <span className="text-green-400">稼働中</span>
                </div>
                <div className="flex justify-between text-gray-300">
                  <span>データ主権:</span>
                  <span className="text-green-400">保護済み</span>
                </div>
              </div>
            </CardContent>
          </FuturisticCard>

          <FuturisticCard glowColor="yellow" active={true}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-white">
                <AlertCircle className="h-5 w-5" />
                <span>システムアラート</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-3 p-2 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                  <AlertTriangle className="h-4 w-4 text-yellow-400" />
                  <div className="flex-1 text-sm">
                    <div className="text-white">コンテナ管理モジュール停止中</div>
                    <div className="text-gray-400">手動介入が必要</div>
                  </div>
                  <Button size="sm" variant="outline" className="text-yellow-400 border-yellow-400">
                    対応
                  </Button>
                </div>
                
                <div className="flex items-center space-x-3 p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                  <Info className="h-4 w-4 text-blue-400" />
                  <div className="flex-1 text-sm">
                    <div className="text-white">システム更新利用可能</div>
                    <div className="text-gray-400">Libral Core v2.1.1</div>
                  </div>
                  <Button size="sm" variant="outline" className="text-blue-400 border-blue-400">
                    更新
                  </Button>
                </div>
              </div>
            </CardContent>
          </FuturisticCard>
        </div>
      </div>
    </div>
  );
}
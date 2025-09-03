import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FuturisticCard } from "@/components/ui/futuristic-card";
import { 
  FileText, 
  Download, 
  Search, 
  Filter, 
  AlertCircle, 
  Info, 
  AlertTriangle, 
  CheckCircle,
  RefreshCw,
  Calendar,
  Clock
} from "lucide-react";

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'error' | 'warn' | 'info' | 'debug';
  module: string;
  message: string;
  metadata?: Record<string, any>;
}

const mockLogs: LogEntry[] = [
  {
    id: '1',
    timestamp: '2024-12-21T12:53:45Z',
    level: 'info',
    module: 'aegis-pgp',
    message: 'GPG key generated successfully',
    metadata: { keyId: 'F1B2C3D4', userId: 'admin@libral.core' }
  },
  {
    id: '2',
    timestamp: '2024-12-21T12:52:30Z',
    level: 'warn',
    module: 'communication-gateway',
    message: 'Telegram API rate limit approaching',
    metadata: { remaining: 5, resetTime: '2024-12-21T13:00:00Z' }
  },
  {
    id: '3',
    timestamp: '2024-12-21T12:51:15Z',
    level: 'error',
    module: 'container-management',
    message: 'Container restart failed',
    metadata: { containerId: 'libral-worker-3', exitCode: 1 }
  },
  {
    id: '4',
    timestamp: '2024-12-21T12:50:00Z',
    level: 'info',
    module: 'payment-management',
    message: 'Telegram Stars payment processed',
    metadata: { amount: 100, userId: 'user123', transactionId: 'tx_abc123' }
  },
  {
    id: '5',
    timestamp: '2024-12-21T12:48:45Z',
    level: 'debug',
    module: 'event-management',
    message: 'WebSocket connection established',
    metadata: { clientId: 'client_789', ip: '192.168.1.100' }
  }
];

export default function Logs() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedModule, setSelectedModule] = useState<string>('all');
  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [timeRange, setTimeRange] = useState('1h');

  const { data: logs = mockLogs, refetch } = useQuery<LogEntry[]>({
    queryKey: ['/api/logs', selectedModule, selectedLevel, timeRange],
    queryFn: async () => {
      // Mock API call
      return mockLogs.filter(log => {
        const moduleMatch = selectedModule === 'all' || log.module === selectedModule;
        const levelMatch = selectedLevel === 'all' || log.level === selectedLevel;
        const searchMatch = searchTerm === '' || 
          log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.module.toLowerCase().includes(searchTerm.toLowerCase());
        
        return moduleMatch && levelMatch && searchMatch;
      });
    },
    refetchInterval: 5000
  });

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'warn': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'info': return <Info className="h-4 w-4 text-blue-500" />;
      case 'debug': return <CheckCircle className="h-4 w-4 text-gray-500" />;
      default: return <Info className="h-4 w-4 text-gray-500" />;
    }
  };

  const getLogBadgeClass = (level: string) => {
    switch (level) {
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'warn': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'info': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'debug': return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('ja-JP');
  };

  const exportLogs = () => {
    const dataStr = JSON.stringify(logs, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `libral-core-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const modules = ['all', 'aegis-pgp', 'communication-gateway', 'container-management', 'payment-management', 'event-management', 'user-management', 'api-hub', 'database-management'];
  const levels = ['all', 'error', 'warn', 'info', 'debug'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="container mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center space-x-3">
              <FileText className="h-8 w-8 text-blue-400" />
              <span>システムログ</span>
            </h1>
            <p className="text-blue-200/80 mt-2">
              Libral Coreシステムのログを監視します
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              onClick={exportLogs}
              className="text-white border-white/20 hover:bg-white/10"
              data-testid="button-export-logs"
            >
              <Download className="h-4 w-4 mr-2" />
              ログをエクスポート
            </Button>
            <Button
              variant="outline"
              onClick={() => refetch()}
              className="text-white border-white/20 hover:bg-white/10"
              data-testid="button-refresh-logs"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              更新
            </Button>
            <Button 
              onClick={() => window.location.href = '/admin-dashboard'}
              variant="outline"
              className="text-white border-white/20 hover:bg-white/10"
            >
              戻る
            </Button>
          </div>
        </div>

        {/* Filters */}
        <FuturisticCard glowColor="blue" active={true}>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Filter className="h-5 w-5" />
              <span>フィルター</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="text-white text-sm">検索</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="ログを検索..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-white/5 border-white/20 text-white"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-white text-sm">モジュール</label>
                <Select value={selectedModule} onValueChange={setSelectedModule}>
                  <SelectTrigger className="bg-white/5 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {modules.map((module) => (
                      <SelectItem key={module} value={module}>
                        {module === 'all' ? '全て' : module}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <label className="text-white text-sm">ログレベル</label>
                <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                  <SelectTrigger className="bg-white/5 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {levels.map((level) => (
                      <SelectItem key={level} value={level}>
                        {level === 'all' ? '全て' : level.toUpperCase()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <label className="text-white text-sm">時間範囲</label>
                <Select value={timeRange} onValueChange={setTimeRange}>
                  <SelectTrigger className="bg-white/5 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1h">過去1時間</SelectItem>
                    <SelectItem value="6h">過去6時間</SelectItem>
                    <SelectItem value="24h">過去24時間</SelectItem>
                    <SelectItem value="7d">過去7日間</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </FuturisticCard>

        {/* Log Entries */}
        <FuturisticCard glowColor="green" active={true}>
          <CardHeader>
            <CardTitle className="flex items-center justify-between text-white">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>ログエントリ</span>
              </div>
              <Badge variant="outline" className="text-white">
                {logs?.length || 0} 件
              </Badge>
            </CardTitle>
            <CardDescription className="text-green-200/80">
              リアルタイムでシステムログを表示
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {logs?.map((log) => (
                <div key={log.id} className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-all">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      {getLogIcon(log.level)}
                      <div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getLogBadgeClass(log.level)}>
                            {log.level.toUpperCase()}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {log.module}
                          </Badge>
                        </div>
                        <div className="text-white font-medium mt-1">{log.message}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-400">
                      <Calendar className="h-3 w-3" />
                      <span>{formatTimestamp(log.timestamp)}</span>
                    </div>
                  </div>
                  
                  {log.metadata && (
                    <div className="mt-3 p-3 bg-black/20 rounded border border-white/5">
                      <div className="text-xs text-gray-400 mb-2">メタデータ:</div>
                      <pre className="text-xs text-gray-300 overflow-x-auto">
                        {JSON.stringify(log.metadata, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
              
              {(!logs || logs.length === 0) && (
                <div className="text-center py-8 text-gray-400">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>現在のフィルター条件に一致するログがありません</p>
                </div>
              )}
            </div>
          </CardContent>
        </FuturisticCard>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-white/5 border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-red-400">
                    {logs?.filter(l => l.level === 'error').length || 0}
                  </div>
                  <div className="text-sm text-gray-400">エラー</div>
                </div>
                <AlertCircle className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/5 border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-yellow-400">
                    {logs?.filter(l => l.level === 'warn').length || 0}
                  </div>
                  <div className="text-sm text-gray-400">警告</div>
                </div>
                <AlertTriangle className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/5 border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-blue-400">
                    {logs?.filter(l => l.level === 'info').length || 0}
                  </div>
                  <div className="text-sm text-gray-400">情報</div>
                </div>
                <Info className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/5 border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-gray-400">
                    {logs?.filter(l => l.level === 'debug').length || 0}
                  </div>
                  <div className="text-sm text-gray-400">デバッグ</div>
                </div>
                <CheckCircle className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Database, Server, Activity, HardDrive, Zap, RefreshCw } from "lucide-react";

interface DatabaseConnection {
  id: string;
  name: string;
  type: 'postgresql' | 'redis' | 'neon';
  status: 'connected' | 'disconnected' | 'error';
  connections: string;
  responseTime: number;
  uptime: number;
  dataSize: string;
}

interface DatabaseMetrics {
  totalConnections: string;
  queryPerSecond: number;
  cacheHitRate: number;
  diskUsage: string;
}

export default function DatabaseManagement() {
  const { data: connections, isLoading: connectionsLoading } = useQuery<DatabaseConnection[]>({
    queryKey: ['/api/database/connections'],
  });

  const { data: metrics, isLoading: metricsLoading } = useQuery<DatabaseMetrics>({
    queryKey: ['/api/database/metrics'],
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'disconnected': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  const getDatabaseIcon = (type: string) => {
    switch (type) {
      case 'postgresql': return <Database className="h-5 w-5 text-blue-500" />;
      case 'redis': return <Zap className="h-5 w-5 text-red-500" />;
      case 'neon': return <Server className="h-5 w-5 text-purple-500" />;
      default: return <Database className="h-5 w-5" />;
    }
  };

  if (connectionsLoading || metricsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">データベース管理</h1>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="space-y-0 pb-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">データベース管理</h1>
          <p className="text-muted-foreground">
            PostgreSQL、Redis、Neonデータベースの統合管理
          </p>
        </div>
        <Button data-testid="button-refresh">
          <RefreshCw className="h-4 w-4 mr-2" />
          リフレッシュ
        </Button>
      </div>

      {/* 統計カード */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">接続数</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-total-connections">
              {metrics?.totalConnections || '0/100'}
            </div>
            <p className="text-xs text-muted-foreground">
              アクティブ接続
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">クエリ/秒</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-queries-per-second">
              {metrics?.queryPerSecond || '0'} QPS
            </div>
            <p className="text-xs text-muted-foreground">
              平均パフォーマンス
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">キャッシュヒット率</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-cache-hit-rate">
              {metrics?.cacheHitRate || '0'}%
            </div>
            <p className="text-xs text-muted-foreground">
              Redis効率
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">ディスク使用量</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-disk-usage">
              {metrics?.diskUsage || '0 GB'}
            </div>
            <p className="text-xs text-muted-foreground">
              ストレージ使用量
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="connections" className="space-y-4">
        <TabsList>
          <TabsTrigger value="connections">データベース接続</TabsTrigger>
          <TabsTrigger value="schema">スキーマ管理</TabsTrigger>
          <TabsTrigger value="performance">パフォーマンス</TabsTrigger>
          <TabsTrigger value="backup">バックアップ</TabsTrigger>
        </TabsList>

        <TabsContent value="connections" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>データベース接続</CardTitle>
              <CardDescription>
                すべてのデータベース接続の状態と統計
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {connections?.length === 0 ? (
                  <Alert>
                    <AlertDescription>
                      データベース接続情報を読み込んでいます...
                    </AlertDescription>
                  </Alert>
                ) : (
                  connections?.map((connection) => (
                    <div key={connection.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        {getDatabaseIcon(connection.type)}
                        <div>
                          <h3 className="font-medium" data-testid={`text-connection-name-${connection.id}`}>
                            {connection.name}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {connection.connections} • {connection.responseTime}ms • {connection.dataSize}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(connection.status)} data-testid={`status-connection-${connection.id}`}>
                          {connection.status}
                        </Badge>
                        <Button variant="outline" size="sm" data-testid={`button-manage-${connection.id}`}>
                          管理
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schema" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>スキーマ管理</CardTitle>
              <CardDescription>
                Drizzle ORMによるスキーマとマイグレーション管理
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  スキーマ管理機能は開発中です。
                  現在はDrizzle Kitの `npm run db:push` でスキーマ更新が可能です。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>パフォーマンス監視</CardTitle>
              <CardDescription>
                クエリパフォーマンスとリソース使用量
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  パフォーマンス監視ダッシュボードは開発中です。
                  現在、{metrics?.queryPerSecond || 0} QPS で稼働中です。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="backup" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>バックアップ管理</CardTitle>
              <CardDescription>
                自動バックアップとリストア機能
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  バックアップ管理機能は開発中です。
                  Neonデータベースの自動バックアップが有効です。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
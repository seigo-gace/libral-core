import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MessageSquare, Phone, Mail, Webhook, Settings, Activity } from "lucide-react";

interface CommunicationAdapter {
  id: string;
  name: string;
  type: 'telegram' | 'email' | 'webhook';
  status: 'active' | 'inactive' | 'error';
  messagesProcessed: number;
  lastActivity: string;
  config: Record<string, any>;
}

interface CommunicationStats {
  totalMessages: number;
  activeAdapters: number;
  errorRate: number;
  responseTime: number;
}

export default function CommunicationGateway() {
  const { data: adapters, isLoading: adaptersLoading } = useQuery<CommunicationAdapter[]>({
    queryKey: ['/api/communication/adapters'],
  });

  const { data: stats, isLoading: statsLoading } = useQuery<CommunicationStats>({
    queryKey: ['/api/communication/stats'],
  });

  const getAdapterIcon = (type: string) => {
    switch (type) {
      case 'telegram': return <MessageSquare className="h-5 w-5" />;
      case 'email': return <Mail className="h-5 w-5" />;
      case 'webhook': return <Webhook className="h-5 w-5" />;
      default: return <Activity className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'inactive': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  if (adaptersLoading || statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">通信ゲートウェイ</h1>
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
          <h1 className="text-3xl font-bold">通信ゲートウェイ</h1>
          <p className="text-muted-foreground">
            マルチプロトコル通信システムの管理と監視
          </p>
        </div>
        <Button data-testid="button-settings">
          <Settings className="h-4 w-4 mr-2" />
          設定
        </Button>
      </div>

      {/* 統計カード */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">総メッセージ数</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-total-messages">
              {stats?.totalMessages?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              +20.1% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">アクティブアダプター</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-active-adapters">
              {stats?.activeAdapters || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              全{adapters?.length || 0}アダプター中
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">エラー率</CardTitle>
            <Phone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-error-rate">
              {stats?.errorRate?.toFixed(2) || '0.00'}%
            </div>
            <p className="text-xs text-muted-foreground">
              -0.5% from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均応答時間</CardTitle>
            <Mail className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-response-time">
              {stats?.responseTime || '0'}ms
            </div>
            <p className="text-xs text-muted-foreground">
              +2ms from last hour
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="adapters" className="space-y-4">
        <TabsList>
          <TabsTrigger value="adapters">アダプター</TabsTrigger>
          <TabsTrigger value="routing">ルーティング</TabsTrigger>
          <TabsTrigger value="logs">ログ</TabsTrigger>
        </TabsList>

        <TabsContent value="adapters" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>通信アダプター</CardTitle>
              <CardDescription>
                登録済みの通信プロトコルアダプターの状態
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {adapters?.length === 0 ? (
                  <Alert>
                    <AlertDescription>
                      現在、登録されているアダプターはありません。
                    </AlertDescription>
                  </Alert>
                ) : (
                  adapters?.map((adapter) => (
                    <div key={adapter.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        {getAdapterIcon(adapter.type)}
                        <div>
                          <h3 className="font-medium" data-testid={`text-adapter-name-${adapter.id}`}>
                            {adapter.name}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {adapter.messagesProcessed.toLocaleString()} messages processed
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(adapter.status)} data-testid={`status-adapter-${adapter.id}`}>
                          {adapter.status}
                        </Badge>
                        <Button variant="outline" size="sm" data-testid={`button-configure-${adapter.id}`}>
                          設定
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="routing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>メッセージルーティング</CardTitle>
              <CardDescription>
                自動フェイルオーバー設定（Telegram → Email → Webhook）
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  ルーティング設定機能は開発中です。現在はデフォルト設定が使用されています。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>通信ログ</CardTitle>
              <CardDescription>
                リアルタイム通信ログとエラー追跡
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  通信ログ表示機能は開発中です。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
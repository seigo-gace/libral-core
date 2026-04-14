import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Network, Key, Activity, DollarSign, Search, Plus, Settings, Eye } from "lucide-react";
import { useState } from "react";

interface APICredential {
  id: string;
  name: string;
  provider: string;
  status: 'active' | 'inactive' | 'expired' | 'error';
  usage: number;
  limit: number;
  cost: number;
  currency: string;
  lastUsed: string;
  createdAt: string;
  encrypted: boolean;
}

interface APIEndpoint {
  id: string;
  path: string;
  method: string;
  description: string;
  provider: string;
  requestCount: number;
  averageResponseTime: number;
  errorRate: number;
  lastCalled: string;
}

interface APIStats {
  totalCredentials: number;
  activeIntegrations: number;
  monthlyApiCalls: number;
  totalCost: number;
}

export default function APIHub() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterProvider, setFilterProvider] = useState<string>("all");

  const { data: credentials, isLoading: credentialsLoading } = useQuery<APICredential[]>({
    queryKey: ['/api/credentials'],
  });

  const { data: endpoints, isLoading: endpointsLoading } = useQuery<APIEndpoint[]>({
    queryKey: ['/api/analytics/endpoints'],
  });

  const { data: stats, isLoading: statsLoading } = useQuery<APIStats>({
    queryKey: ['/api/integrations/stats'],
  });

  const filteredCredentials = credentials?.filter(credential => {
    const matchesSearch = credential.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         credential.provider.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesProvider = filterProvider === "all" || credential.provider === filterProvider;
    return matchesSearch && matchesProvider;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'inactive': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
      case 'expired': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'error': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: currency || 'USD'
    }).format(amount);
  };

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === 0) return 0;
    return Math.round((used / limit) * 100);
  };

  if (credentialsLoading || endpointsLoading || statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">APIハブ</h1>
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
          <h1 className="text-3xl font-bold">APIハブ</h1>
          <p className="text-muted-foreground">
            暗号化API認証情報と使用量追跡管理
          </p>
        </div>
        <Button data-testid="button-add-credential">
          <Plus className="h-4 w-4 mr-2" />
          API認証情報追加
        </Button>
      </div>

      {/* 統計カード */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API認証情報</CardTitle>
            <Key className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-total-credentials">
              {stats?.totalCredentials || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              暗号化保存済み
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">アクティブ統合</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-active-integrations">
              {stats?.activeIntegrations || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              外部サービス連携
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">月間API呼び出し</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-monthly-api-calls">
              {stats?.monthlyApiCalls?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">月間コスト</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-total-cost">
              {formatCurrency(stats?.totalCost || 0, 'USD')}
            </div>
            <p className="text-xs text-muted-foreground">
              コスト管理対象
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="credentials" className="space-y-4">
        <TabsList>
          <TabsTrigger value="credentials">API認証情報</TabsTrigger>
          <TabsTrigger value="endpoints">エンドポイント分析</TabsTrigger>
          <TabsTrigger value="usage">使用量追跡</TabsTrigger>
          <TabsTrigger value="cost">コスト管理</TabsTrigger>
        </TabsList>

        <TabsContent value="credentials" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>API認証情報</CardTitle>
              <CardDescription>
                暗号化されたAPI認証情報と使用統計
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 mb-4">
                <div className="relative flex-1 max-w-sm">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="認証情報名またはプロバイダーで検索..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                    data-testid="input-credential-search"
                  />
                </div>
                <select 
                  value={filterProvider}
                  onChange={(e) => setFilterProvider(e.target.value)}
                  className="px-3 py-2 border rounded-md bg-background"
                  data-testid="select-provider-filter"
                >
                  <option value="all">すべてのプロバイダー</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="google">Google</option>
                  <option value="aws">AWS</option>
                  <option value="azure">Azure</option>
                </select>
              </div>

              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>名前</TableHead>
                      <TableHead>プロバイダー</TableHead>
                      <TableHead>ステータス</TableHead>
                      <TableHead>使用量</TableHead>
                      <TableHead>コスト</TableHead>
                      <TableHead>最終使用</TableHead>
                      <TableHead>暗号化</TableHead>
                      <TableHead className="w-[100px]">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredCredentials?.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center py-4">
                          <Alert>
                            <AlertDescription>
                              該当するAPI認証情報が見つかりません。
                            </AlertDescription>
                          </Alert>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredCredentials?.map((credential) => (
                        <TableRow key={credential.id} data-testid={`row-credential-${credential.id}`}>
                          <TableCell className="font-medium" data-testid={`text-credential-name-${credential.id}`}>
                            {credential.name}
                          </TableCell>
                          <TableCell className="capitalize" data-testid={`text-credential-provider-${credential.id}`}>
                            {credential.provider}
                          </TableCell>
                          <TableCell>
                            <Badge className={getStatusColor(credential.status)} data-testid={`badge-credential-status-${credential.id}`}>
                              {credential.status}
                            </Badge>
                          </TableCell>
                          <TableCell data-testid={`text-credential-usage-${credential.id}`}>
                            <div className="space-y-1">
                              <div className="text-sm">
                                {credential.usage.toLocaleString()} / {credential.limit.toLocaleString()}
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-1.5 dark:bg-gray-700">
                                <div 
                                  className="bg-blue-600 h-1.5 rounded-full" 
                                  style={{ width: `${getUsagePercentage(credential.usage, credential.limit)}%` }}
                                ></div>
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {getUsagePercentage(credential.usage, credential.limit)}%
                              </div>
                            </div>
                          </TableCell>
                          <TableCell data-testid={`text-credential-cost-${credential.id}`}>
                            {formatCurrency(credential.cost, credential.currency)}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground" data-testid={`text-credential-last-used-${credential.id}`}>
                            {new Date(credential.lastUsed).toLocaleDateString('ja-JP')}
                          </TableCell>
                          <TableCell data-testid={`text-credential-encrypted-${credential.id}`}>
                            {credential.encrypted ? (
                              <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                暗号化済み
                              </Badge>
                            ) : (
                              <Badge variant="outline">
                                未暗号化
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            <div className="flex space-x-1">
                              <Button variant="ghost" size="sm" data-testid={`button-view-${credential.id}`}>
                                <Eye className="h-3 w-3" />
                              </Button>
                              <Button variant="ghost" size="sm" data-testid={`button-settings-${credential.id}`}>
                                <Settings className="h-3 w-3" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="endpoints" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>APIエンドポイント分析</CardTitle>
              <CardDescription>
                各エンドポイントのパフォーマンスと使用統計
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  APIエンドポイント分析機能は開発中です。
                  リクエスト統計、応答時間、エラー率の詳細分析が利用可能になります。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="usage" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>使用量追跡</CardTitle>
              <CardDescription>
                API使用量の詳細追跡とアラート設定
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  使用量追跡機能は開発中です。
                  リアルタイム使用量監視、制限アラート、コスト予測が利用可能になります。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="cost" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>コスト管理</CardTitle>
              <CardDescription>
                APIコストの分析と予算管理
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  コスト管理機能は開発中です。
                  月間予算設定、コスト予測、プロバイダー別分析が利用可能になります。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
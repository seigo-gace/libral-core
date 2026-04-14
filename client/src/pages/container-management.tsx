import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Container, Play, Square, RotateCcw, Cpu, MemoryStick, HardDrive, Network } from "lucide-react";

interface ContainerInfo {
  id: string;
  name: string;
  image: string;
  status: 'running' | 'stopped' | 'restarting' | 'error';
  cpuUsage: number;
  memoryUsage: number;
  networkIO: string;
  uptime: string;
  ports: string[];
}

interface ContainerStats {
  totalContainers: number;
  runningContainers: number;
  cpuTotal: number;
  memoryTotal: number;
}

export default function ContainerManagement() {
  const { data: containers, isLoading: containersLoading } = useQuery<ContainerInfo[]>({
    queryKey: ['/api/containers'],
  });

  const { data: stats, isLoading: statsLoading } = useQuery<ContainerStats>({
    queryKey: ['/api/containers/stats'],
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'stopped': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
      case 'restarting': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Play className="h-4 w-4 text-green-500" />;
      case 'stopped': return <Square className="h-4 w-4 text-gray-500" />;
      case 'restarting': return <RotateCcw className="h-4 w-4 text-yellow-500" />;
      case 'error': return <Square className="h-4 w-4 text-red-500" />;
      default: return <Container className="h-4 w-4" />;
    }
  };

  if (containersLoading || statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">コンテナ管理</h1>
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
          <h1 className="text-3xl font-bold">コンテナ管理</h1>
          <p className="text-muted-foreground">
            Dockerコンテナとマイクロサービスの管理
          </p>
        </div>
        <Button data-testid="button-deploy">
          <Container className="h-4 w-4 mr-2" />
          新規デプロイ
        </Button>
      </div>

      {/* 統計カード */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">総コンテナ数</CardTitle>
            <Container className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-total-containers">
              {stats?.totalContainers || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              デプロイ済みコンテナ
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">稼働中</CardTitle>
            <Play className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-running-containers">
              {stats?.runningContainers || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              アクティブコンテナ
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CPU使用率</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-cpu-total">
              {stats?.cpuTotal || '0'}%
            </div>
            <p className="text-xs text-muted-foreground">
              全コンテナ合計
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">メモリ使用量</CardTitle>
            <MemoryStick className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-memory-total">
              {stats?.memoryTotal || '0'}%
            </div>
            <p className="text-xs text-muted-foreground">
              全コンテナ合計
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="containers" className="space-y-4">
        <TabsList>
          <TabsTrigger value="containers">コンテナ一覧</TabsTrigger>
          <TabsTrigger value="images">イメージ管理</TabsTrigger>
          <TabsTrigger value="networks">ネットワーク</TabsTrigger>
          <TabsTrigger value="volumes">ボリューム</TabsTrigger>
        </TabsList>

        <TabsContent value="containers" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>コンテナ一覧</CardTitle>
              <CardDescription>
                すべてのコンテナの状態とリソース使用量
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {containers?.length === 0 ? (
                  <Alert>
                    <AlertDescription>
                      現在稼働中のコンテナはありません。
                      Replitワークフローでアプリケーションが実行されています。
                    </AlertDescription>
                  </Alert>
                ) : (
                  containers?.map((container) => (
                    <div key={container.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        {getStatusIcon(container.status)}
                        <div>
                          <h3 className="font-medium" data-testid={`text-container-name-${container.id}`}>
                            {container.name}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {container.image} • {container.uptime} • {container.networkIO}
                          </p>
                          <div className="flex space-x-2 text-xs text-muted-foreground mt-1">
                            <span>CPU: {container.cpuUsage}%</span>
                            <span>Memory: {container.memoryUsage}%</span>
                            <span>Ports: {container.ports.join(', ')}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(container.status)} data-testid={`status-container-${container.id}`}>
                          {container.status}
                        </Badge>
                        <Button variant="outline" size="sm" data-testid={`button-manage-${container.id}`}>
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

        <TabsContent value="images" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Dockerイメージ</CardTitle>
              <CardDescription>
                コンテナイメージの管理とバージョン履歴
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  Dockerイメージ管理機能は開発中です。
                  現在はReplitネイティブワークフローを使用しています。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="networks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>ネットワーク管理</CardTitle>
              <CardDescription>
                コンテナ間ネットワークとポート管理
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  ネットワーク管理機能は開発中です。
                  現在はReplit自動ポート設定（5000番）を使用しています。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="volumes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>ボリューム管理</CardTitle>
              <CardDescription>
                永続化ストレージとデータボリューム
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  ボリューム管理機能は開発中です。
                  現在はReplitファイルシステムとPostgreSQLが永続化されています。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
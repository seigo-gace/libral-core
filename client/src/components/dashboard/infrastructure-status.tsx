import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Database, Layers, Container } from "lucide-react";

interface InfrastructureStatus {
  database: {
    connections: string;
    size: string;
    queriesPerSecond: number;
    replicationStatus: string;
  };
  redis: {
    memoryUsed: string;
    connectedClients: number;
    pubsubChannels: number;
    hitRatio: string;
  };
  docker: {
    runningContainers: string;
    cpuUsage: string;
    memoryUsage: string;
    volumes: number;
  };
}

export function InfrastructureStatus() {
  const { data: infrastructure, isLoading } = useQuery<InfrastructureStatus>({
    queryKey: ['/api/infrastructure/status'],
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="bg-dark-800 border-dark-700">
            <CardHeader>
              <div className="animate-pulse h-6 bg-dark-600 rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[...Array(4)].map((_, j) => (
                  <div key={j} className="animate-pulse flex justify-between">
                    <div className="h-4 bg-dark-600 rounded w-1/3"></div>
                    <div className="h-4 bg-dark-600 rounded w-1/4"></div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Database Status */}
      <Card className="bg-dark-800 border-dark-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-dark-50 flex items-center">
            <Database className="mr-2 h-5 w-5 text-primary" />
            PostgreSQL
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">接続数</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.database.connections || "0/100"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">データベースサイズ</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.database.size || "0 GB"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">クエリ/秒</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.database.queriesPerSecond || 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">レプリケーション</span>
              <Badge className="bg-success bg-opacity-10 text-success">
                {infrastructure?.database.replicationStatus || "不明"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Redis Status */}
      <Card className="bg-dark-800 border-dark-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-dark-50 flex items-center">
            <Layers className="mr-2 h-5 w-5 text-error" />
            Redis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">使用メモリ</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.redis.memoryUsed || "0 MB"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">接続クライアント</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.redis.connectedClients || 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">Pub/Sub チャネル</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.redis.pubsubChannels || 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">キャッシュヒット率</span>
              <span className="text-sm font-medium text-success">
                {infrastructure?.redis.hitRatio || "0%"}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Docker Status */}
      <Card className="bg-dark-800 border-dark-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-dark-50 flex items-center">
            <Container className="mr-2 h-5 w-5 text-primary" />
            Docker
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">実行中コンテナ</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.docker.runningContainers || "0/0"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">CPU使用率</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.docker.cpuUsage || "0%"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">メモリ使用量</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.docker.memoryUsage || "0 GB"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-dark-400">ボリューム</span>
              <span className="text-sm font-medium text-dark-50">
                {infrastructure?.docker.volumes || 0}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

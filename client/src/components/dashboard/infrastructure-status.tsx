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
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="bg-dark-800 border-dark-700">
            <CardHeader className="pb-3 sm:pb-4">
              <div className="animate-pulse h-5 sm:h-6 bg-dark-600 rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 sm:space-y-4">
                {[...Array(4)].map((_, j) => (
                  <div key={j} className="animate-pulse flex justify-between">
                    <div className="h-3 sm:h-4 bg-dark-600 rounded w-1/3"></div>
                    <div className="h-3 sm:h-4 bg-dark-600 rounded w-1/4"></div>
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
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
      {/* Database Status */}
      <Card className="bg-dark-800 border-dark-700" data-testid="card-database-status">
        <CardHeader className="pb-3 sm:pb-4">
          <CardTitle className="text-base sm:text-lg font-semibold text-dark-50 flex items-center">
            <Database className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-primary" />
            PostgreSQL
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 sm:space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">接続数</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50" data-testid="text-database-connections">
                {infrastructure?.database.connections || "0/100"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">データベースサイズ</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50">
                {infrastructure?.database.size || "120MB"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">QPS</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50">
                {infrastructure?.database.queriesPerSecond || 45}/sec
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">レプリケーション</span>
              <Badge className="bg-success bg-opacity-10 text-success text-xs">
                {infrastructure?.database.replicationStatus || "同期済み"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Redis Status */}
      <Card className="bg-dark-800 border-dark-700" data-testid="card-redis-status">
        <CardHeader className="pb-3 sm:pb-4">
          <CardTitle className="text-base sm:text-lg font-semibold text-dark-50 flex items-center">
            <Layers className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-error" />
            Redis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 sm:space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">使用メモリ</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50">
                {infrastructure?.redis.memoryUsed || "12MB"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">接続クライアント</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50">
                {infrastructure?.redis.connectedClients || 5}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">Pub/Sub チャネル</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50">
                {infrastructure?.redis.pubsubChannels || 3}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">キャッシュヒット率</span>
              <span className="text-xs sm:text-sm font-medium text-success">
                {infrastructure?.redis.hitRatio || "95%"}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Docker Status */}
      <Card className="bg-dark-800 border-dark-700 sm:col-span-2 xl:col-span-1" data-testid="card-docker-status">
        <CardHeader className="pb-3 sm:pb-4">
          <CardTitle className="text-base sm:text-lg font-semibold text-dark-50 flex items-center">
            <Container className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-primary" />
            Docker
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 sm:space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">実行中コンテナ</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50">
                {infrastructure?.docker.runningContainers || "3/5"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">CPU使用率</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50">
                {infrastructure?.docker.cpuUsage || "25%"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">メモリ使用量</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50">
                {infrastructure?.docker.memoryUsage || "1.2GB"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs sm:text-sm text-dark-400">ボリューム</span>
              <span className="text-xs sm:text-sm font-medium text-dark-50">
                {infrastructure?.docker.volumes || 8}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

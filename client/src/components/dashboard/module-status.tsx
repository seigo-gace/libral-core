import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Container } from "lucide-react";
import { useWebSocket } from "@/hooks/use-websocket";
import { useEffect, useState } from "react";

interface Module {
  id: string;
  name: string;
  version: string;
  status: string;
  port?: number;
  endpoint?: string;
  lastHealthCheck?: string;
}

export function ModuleStatus() {
  const [modules, setModules] = useState<Module[]>([]);

  const { data: initialModules, isLoading } = useQuery<Module[]>({
    queryKey: ['/api/modules'],
    refetchInterval: 60000, // Refetch every minute
  });

  // WebSocket connection for real-time module status updates
  useWebSocket('/ws', {
    onMessage: (message) => {
      if (message.type === 'module_status' && message.data) {
        const { moduleId, status } = message.data;
        setModules(prevModules =>
          prevModules.map(module =>
            module.id === moduleId ? { ...module, status } : module
          )
        );
      }
    }
  });

  useEffect(() => {
    if (initialModules) {
      setModules(initialModules);
    }
  }, [initialModules]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success bg-opacity-10 text-success';
      case 'high_load':
        return 'bg-warning bg-opacity-10 text-warning';
      case 'error':
        return 'bg-error bg-opacity-10 text-error';
      default:
        return 'bg-dark-600 text-dark-300';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '正常';
      case 'high_load':
        return '高負荷';
      case 'error':
        return 'エラー';
      default:
        return '不明';
    }
  };

  const getStatusDotColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success';
      case 'high_load':
        return 'bg-warning';
      case 'error':
        return 'bg-error';
      default:
        return 'bg-dark-500';
    }
  };

  if (isLoading) {
    return (
      <Card className="bg-dark-800 border-dark-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-dark-50 flex items-center">
            <Container className="mr-2 h-5 w-5 text-primary" />
            モジュール状態
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse py-3 border-b border-dark-700 last:border-b-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-dark-600 rounded-full mr-3"></div>
                    <div>
                      <div className="h-4 bg-dark-600 rounded w-24 mb-1"></div>
                      <div className="h-3 bg-dark-600 rounded w-16"></div>
                    </div>
                  </div>
                  <div className="h-6 bg-dark-600 rounded w-12"></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-dark-800 border-dark-700">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-dark-50 flex items-center">
          <Container className="mr-2 h-5 w-5 text-primary" />
          モジュール状態
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {modules.map((module) => (
            <div key={module.id} className="flex items-center justify-between py-3 border-b border-dark-700 last:border-b-0">
              <div className="flex items-center">
                <div className={`w-3 h-3 ${getStatusDotColor(module.status)} rounded-full mr-3`}></div>
                <div>
                  <p className="text-sm font-medium text-dark-50">{module.name}</p>
                  <p className="text-xs text-dark-400">
                    {module.version} • Port {module.port}
                  </p>
                </div>
              </div>
              <Badge className={getStatusColor(module.status)}>
                {getStatusText(module.status)}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

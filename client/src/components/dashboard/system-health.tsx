import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Cpu, MemoryStick, Users, Activity, TrendingUp, TrendingDown } from "lucide-react";
import { useWebSocket } from "@/hooks/use-websocket";
import { useEffect, useState } from "react";

interface SystemMetrics {
  cpuUsage: string;
  memoryUsage: string;
  activeUsers: string;
  apiRequestsPerMinute: string;
}

export function SystemHealth() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);

  const { data: initialMetrics, isLoading } = useQuery<SystemMetrics>({
    queryKey: ['/api/system/metrics'],
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // WebSocket connection for real-time updates
  useWebSocket('/ws', {
    onMessage: (message) => {
      if (message.type === 'metrics_update' && message.data) {
        setMetrics(prevMetrics => ({
          ...prevMetrics,
          ...message.data
        }));
      }
    }
  });

  useEffect(() => {
    if (initialMetrics) {
      setMetrics(initialMetrics);
    }
  }, [initialMetrics]);

  const currentMetrics = metrics || initialMetrics;

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4 lg:gap-6 mb-6 sm:mb-8">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="bg-dark-800 border-dark-700">
            <CardContent className="p-3 sm:p-4 lg:p-6">
              <div className="animate-pulse">
                <div className="h-3 sm:h-4 bg-dark-700 rounded w-1/2 mb-2"></div>
                <div className="h-6 sm:h-8 bg-dark-700 rounded w-1/3"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const healthCards = [
    {
      title: "CPU使用率",
      value: `${currentMetrics?.cpuUsage || '0'}%`,
      icon: Cpu,
      color: "success",
      trend: "down",
      trendText: "2.5% from last hour"
    },
    {
      title: "メモリ使用量", 
      value: `${currentMetrics?.memoryUsage || '0'}%`,
      icon: MemoryStick,
      color: "warning",
      trend: "up",
      trendText: "5.2% from last hour"
    },
    {
      title: "アクティブユーザー",
      value: currentMetrics?.activeUsers || '0',
      icon: Users,
      color: "primary",
      trend: "up", 
      trendText: "12 new today"
    },
    {
      title: "API リクエスト/分",
      value: currentMetrics?.apiRequestsPerMinute || '0',
      icon: Activity,
      color: "secondary",
      trend: "up",
      trendText: "Normal load"
    }
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4 lg:gap-6 mb-6 sm:mb-8">
      {healthCards.map((card) => {
        const Icon = card.icon;
        const TrendIcon = card.trend === 'up' ? TrendingUp : TrendingDown;
        const colorClass = card.color === 'success' ? 'text-success' : 
                          card.color === 'warning' ? 'text-warning' :
                          card.color === 'primary' ? 'text-primary' : 'text-secondary';
        const bgColorClass = card.color === 'success' ? 'bg-success' : 
                            card.color === 'warning' ? 'bg-warning' :
                            card.color === 'primary' ? 'bg-primary' : 'bg-secondary';

        return (
          <Card key={card.title} className="bg-dark-800 border-dark-700" data-testid={`card-metric-${card.title.toLowerCase().replace(/\s+/g, '-')}`}>
            <CardContent className="p-3 sm:p-4 lg:p-6">
              <div className="flex flex-col space-y-2 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
                <div className="order-2 sm:order-1">
                  <p className="text-xs sm:text-sm font-medium text-dark-400 leading-tight">{card.title}</p>
                  <p className={`text-lg sm:text-xl lg:text-2xl font-bold ${colorClass} mt-1`} data-testid={`text-value-${card.title.toLowerCase().replace(/\s+/g, '-')}`}>
                    {card.value}
                  </p>
                </div>
                <div className={`order-1 sm:order-2 w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 ${bgColorClass} bg-opacity-10 rounded-lg flex items-center justify-center self-end sm:self-auto`}>
                  <Icon className={`h-4 w-4 sm:h-5 sm:w-5 lg:h-6 lg:w-6 ${colorClass}`} />
                </div>
              </div>
              <div className="mt-2 sm:mt-3 lg:mt-4">
                <div className={`flex items-center text-xs sm:text-sm ${colorClass}`}>
                  <TrendIcon className="h-3 w-3 mr-1 flex-shrink-0" />
                  <span className="truncate">{card.trendText}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

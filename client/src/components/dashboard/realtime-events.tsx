import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity } from "lucide-react";
import { useWebSocket } from "@/hooks/use-websocket";
import { useEffect, useState } from "react";

interface Event {
  id: string;
  type: string;
  source: string;
  userId?: string;
  data: any;
  level: string;
  createdAt: string;
}

export function RealtimeEvents() {
  const [events, setEvents] = useState<Event[]>([]);

  const { data: initialEvents, isLoading } = useQuery<Event[]>({
    queryKey: ['/api/events'],
    refetchInterval: 30000,
  });

  // WebSocket connection for real-time events
  useWebSocket('/ws', {
    onMessage: (message) => {
      if (message.type === 'new_event' && message.data) {
        setEvents(prevEvents => [message.data, ...prevEvents].slice(0, 10));
      } else if (message.type === 'system_event' && message.data) {
        setEvents(prevEvents => [message.data, ...prevEvents].slice(0, 10));
      }
    }
  });

  useEffect(() => {
    if (initialEvents) {
      setEvents(initialEvents.slice(0, 10));
    }
  }, [initialEvents]);

  const getEventColor = (level: string) => {
    switch (level) {
      case 'info':
        return 'bg-primary';
      case 'warning':
        return 'bg-warning';
      case 'error':
        return 'bg-error';
      default:
        return 'bg-success';
    }
  };

  const formatEventTitle = (event: Event) => {
    switch (event.type) {
      case 'user_auth_success':
        return 'ユーザー認証成功';
      case 'user_registered':
        return '新規ユーザー登録';
      case 'api_request':
        return 'API リクエスト';
      case 'payment_completed':
        return '決済完了';
      case 'webhook_received':
        return 'Webhook受信';
      case 'module_health_check':
        return 'モジュールヘルスチェック';
      default:
        return event.type;
    }
  };

  const formatEventDescription = (event: Event) => {
    const timeAgo = getTimeAgo(event.createdAt);
    
    switch (event.type) {
      case 'user_auth_success':
        return `user_id: ${event.userId} • ${timeAgo}`;
      case 'user_registered':
        return `telegram_id: ${event.data?.telegramId || 'unknown'} • ${timeAgo}`;
      case 'api_request':
        return `${event.data?.method || 'GET'} ${event.data?.path || '/api'} • ${timeAgo}`;
      case 'payment_completed':
        return `¥${event.data?.amount || '0'} • transaction_id: ${event.data?.transactionId} • ${timeAgo}`;
      case 'webhook_received':
        return `${event.source} message • ${timeAgo}`;
      case 'module_health_check':
        return `${event.data?.moduleId || 'unknown'} status: ${event.data?.status || 'unknown'} • ${timeAgo}`;
      default:
        return `${event.source} • ${timeAgo}`;
    }
  };

  const getTimeAgo = (dateString: string) => {
    const now = new Date();
    const eventTime = new Date(dateString);
    const diffInMinutes = Math.floor((now.getTime() - eventTime.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'たった今';
    if (diffInMinutes < 60) return `${diffInMinutes}分前`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}時間前`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}日前`;
  };

  if (isLoading) {
    return (
      <Card className="bg-dark-800 border-dark-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-dark-50 flex items-center">
            <Activity className="mr-2 h-5 w-5 text-secondary" />
            リアルタイムイベント
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="animate-pulse flex items-start space-x-3 py-2">
                <div className="w-2 h-2 bg-dark-600 rounded-full mt-2"></div>
                <div className="flex-1">
                  <div className="h-4 bg-dark-600 rounded w-3/4 mb-1"></div>
                  <div className="h-3 bg-dark-600 rounded w-1/2"></div>
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
          <Activity className="mr-2 h-5 w-5 text-secondary" />
          リアルタイムイベント
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 max-h-80 overflow-y-auto">
          {events.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-dark-400">イベントがありません</p>
            </div>
          ) : (
            events.map((event) => (
              <div key={event.id} className="flex items-start space-x-3 py-2">
                <div className={`w-2 h-2 ${getEventColor(event.level)} rounded-full mt-2 flex-shrink-0`}></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-dark-50">{formatEventTitle(event)}</p>
                  <p className="text-xs text-dark-400">{formatEventDescription(event)}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}

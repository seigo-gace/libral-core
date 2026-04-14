import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Receipt, CheckCircle, Clock, Video, Star } from "lucide-react";

interface ApiEndpoint {
  id: string;
  path: string;
  method: string;
  requestCount: number;
  averageResponseTime: string | null;
  lastRequestAt: string | null;
}

interface Transaction {
  id: string;
  userId: string;
  type: string;
  amount: string;
  currency: string;
  status: string;
  createdAt: string;
  metadata?: any;
}

export function Analytics() {
  const { data: endpoints, isLoading: endpointsLoading } = useQuery<ApiEndpoint[]>({
    queryKey: ['/api/analytics/endpoints'],
    refetchInterval: 60000,
  });

  const { data: transactions, isLoading: transactionsLoading } = useQuery<Transaction[]>({
    queryKey: ['/api/transactions'],
    refetchInterval: 30000,
  });

  const getEndpointColor = (path: string) => {
    if (path.includes('auth')) return 'text-success';
    if (path.includes('payment')) return 'text-primary';
    if (path.includes('webhook')) return 'text-warning';
    return 'text-secondary';
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'sticker_purchase':
        return CheckCircle;
      case 'telegram_stars':
        return Star;
      case 'subscription':
        return Video;
      default:
        return CheckCircle;
    }
  };

  const getTransactionTitle = (type: string) => {
    switch (type) {
      case 'sticker_purchase':
        return 'ステッカーパック購入';
      case 'telegram_stars':
        return 'Telegram Stars購入';
      case 'subscription':
        return 'プレミアム配信';
      default:
        return 'その他の取引';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success';
      case 'pending':
        return 'text-warning';
      case 'failed':
        return 'text-error';
      default:
        return 'text-dark-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '完了';
      case 'pending':
        return '処理中';
      case 'failed':
        return '失敗';
      default:
        return status;
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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* API Analytics */}
      <Card className="bg-dark-800 border-dark-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-dark-50 flex items-center">
            <TrendingUp className="mr-2 h-5 w-5 text-secondary" />
            API解析
          </CardTitle>
        </CardHeader>
        <CardContent>
          {endpointsLoading ? (
            <div className="space-y-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="animate-pulse flex items-center justify-between py-3 border-b border-dark-700 last:border-b-0">
                  <div className="flex-1">
                    <div className="h-4 bg-dark-600 rounded w-3/4 mb-1"></div>
                    <div className="h-3 bg-dark-600 rounded w-1/2"></div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="h-3 bg-dark-600 rounded w-8"></div>
                    <div className="w-3 h-3 bg-dark-600 rounded-full"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {!endpoints || endpoints.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-dark-400">APIエンドポイントデータがありません</p>
                </div>
              ) : (
                endpoints.slice(0, 4).map((endpoint) => (
                  <div key={endpoint.id} className="flex items-center justify-between py-3 border-b border-dark-700 last:border-b-0">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-dark-50">{endpoint.path}</p>
                      <p className="text-xs text-dark-400">
                        平均応答時間: {endpoint.averageResponseTime ? `${Math.round(parseFloat(endpoint.averageResponseTime))}ms` : 'N/A'}
                      </p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`text-xs ${getEndpointColor(endpoint.path)}`}>
                        ↑ {endpoint.requestCount || 0}
                      </span>
                      <div className={`w-3 h-3 ${getEndpointColor(endpoint.path).replace('text-', 'bg-')} rounded-full`}></div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Transactions */}
      <Card className="bg-dark-800 border-dark-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-dark-50 flex items-center">
            <Receipt className="mr-2 h-5 w-5 text-warning" />
            最近の取引
          </CardTitle>
        </CardHeader>
        <CardContent>
          {transactionsLoading ? (
            <div className="space-y-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="animate-pulse flex items-center justify-between py-3 border-b border-dark-700 last:border-b-0">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-dark-600 rounded-full"></div>
                    <div>
                      <div className="h-4 bg-dark-600 rounded w-24 mb-1"></div>
                      <div className="h-3 bg-dark-600 rounded w-16"></div>
                    </div>
                  </div>
                  <div className="h-4 bg-dark-600 rounded w-12"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {!transactions || transactions.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-dark-400">取引データがありません</p>
                </div>
              ) : (
                transactions.slice(0, 4).map((transaction) => {
                  const Icon = getTransactionIcon(transaction.type);
                  const iconColor = transaction.status === 'completed' ? 'text-success' : 
                                   transaction.status === 'pending' ? 'text-warning' : 'text-error';
                  const bgColor = transaction.status === 'completed' ? 'bg-success' : 
                                 transaction.status === 'pending' ? 'bg-warning' : 'bg-error';

                  return (
                    <div key={transaction.id} className="flex items-center justify-between py-3 border-b border-dark-700 last:border-b-0">
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 ${bgColor} bg-opacity-10 rounded-full flex items-center justify-center`}>
                          <Icon className={`${iconColor} h-4 w-4`} />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-dark-50">
                            {getTransactionTitle(transaction.type)}
                          </p>
                          <p className="text-xs text-dark-400">
                            ID: {transaction.id.slice(0, 8)}... • {getTimeAgo(transaction.createdAt)}
                          </p>
                        </div>
                      </div>
                      {transaction.status === 'completed' ? (
                        <span className="text-sm font-medium text-success">
                          ¥{parseFloat(transaction.amount).toLocaleString()}
                        </span>
                      ) : (
                        <Badge className={`${bgColor} bg-opacity-10 ${iconColor}`}>
                          {getStatusText(transaction.status)}
                        </Badge>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

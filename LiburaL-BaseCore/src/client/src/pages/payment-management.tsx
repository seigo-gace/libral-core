import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CreditCard, DollarSign, TrendingUp, Star, Search, Settings, Plus, Smartphone, Network } from "lucide-react";
import { useState } from "react";

interface Transaction {
  id: string;
  type: 'payment' | 'refund' | 'subscription' | 'commission';
  amount: number;
  currency: 'USD' | 'JPY' | 'EUR' | 'STARS';
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  paymentMethod: 'telegram_stars' | 'credit_card' | 'crypto';
  userId: string;
  username: string;
  description: string;
  timestamp: string;
  metadata: Record<string, any>;
}

interface PaymentStats {
  totalRevenue: number;
  monthlyRevenue: number;
  telegramStarsEarned: number;
  pluginCommissions: number;
  pendingPayments: number;
  refundRate: number;
}

export default function PaymentManagement() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const { data: transactions, isLoading: transactionsLoading } = useQuery<Transaction[]>({
    queryKey: ['/api/transactions'],
  });

  const { data: stats, isLoading: statsLoading } = useQuery<PaymentStats>({
    queryKey: ['/api/payments/stats'],
  });

  const filteredTransactions = transactions?.filter(transaction => {
    const matchesSearch = transaction.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         transaction.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === "all" || transaction.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'failed': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'refunded': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  const getPaymentMethodIcon = (method: string) => {
    switch (method) {
      case 'telegram_stars': return <Star className="h-4 w-4 text-yellow-500" />;
      case 'credit_card': return <CreditCard className="h-4 w-4" />;
      case 'crypto': return <DollarSign className="h-4 w-4 text-orange-500" />;
      default: return <CreditCard className="h-4 w-4" />;
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    if (currency === 'STARS') {
      return `${amount} ⭐`;
    }
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: currency === 'USD' ? 'USD' : currency === 'EUR' ? 'EUR' : 'JPY'
    }).format(amount);
  };

  if (transactionsLoading || statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">決済管理</h1>
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
          <h1 className="text-3xl font-bold">決済管理</h1>
          <p className="text-muted-foreground">
            Telegram Stars統合と暗号化請求ログ管理
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" data-testid="button-export">
            エクスポート
          </Button>
          <Button data-testid="button-add-payment">
            <Plus className="h-4 w-4 mr-2" />
            手動決済
          </Button>
        </div>
      </div>

      {/* 統計カード */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">総収益</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-total-revenue">
              {formatCurrency(stats?.totalRevenue || 0, 'USD')}
            </div>
            <p className="text-xs text-muted-foreground">
              +20.1% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">今月の収益</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-monthly-revenue">
              {formatCurrency(stats?.monthlyRevenue || 0, 'USD')}
            </div>
            <p className="text-xs text-muted-foreground">
              +8% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Telegram Stars</CardTitle>
            <Star className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-telegram-stars">
              {stats?.telegramStarsEarned?.toLocaleString() || '0'} ⭐
            </div>
            <p className="text-xs text-muted-foreground">
              今月獲得したStars
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">プラグイン収益</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-plugin-commissions">
              {formatCurrency(stats?.pluginCommissions || 0, 'USD')}
            </div>
            <p className="text-xs text-muted-foreground">
              開発者への自動分配
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="transactions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="transactions">取引履歴</TabsTrigger>
          <TabsTrigger value="billing">請求管理</TabsTrigger>
          <TabsTrigger value="commissions">収益分配</TabsTrigger>
          <TabsTrigger value="settings">決済設定</TabsTrigger>
        </TabsList>

        <TabsContent value="transactions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>取引履歴</CardTitle>
              <CardDescription>
                すべての決済取引と状況の詳細
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 mb-4">
                <div className="relative flex-1 max-w-sm">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="ユーザー名または説明で検索..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                    data-testid="input-transaction-search"
                  />
                </div>
                <select 
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border rounded-md bg-background"
                  data-testid="select-transaction-status"
                >
                  <option value="all">すべてのステータス</option>
                  <option value="completed">完了</option>
                  <option value="pending">処理中</option>
                  <option value="failed">失敗</option>
                  <option value="refunded">返金済み</option>
                </select>
              </div>

              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>取引ID</TableHead>
                      <TableHead>ユーザー</TableHead>
                      <TableHead>金額</TableHead>
                      <TableHead>決済方法</TableHead>
                      <TableHead>ステータス</TableHead>
                      <TableHead>説明</TableHead>
                      <TableHead>日時</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredTransactions?.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-4">
                          <Alert>
                            <AlertDescription>
                              該当する取引が見つかりません。
                            </AlertDescription>
                          </Alert>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredTransactions?.map((transaction) => (
                        <TableRow key={transaction.id} data-testid={`row-transaction-${transaction.id}`}>
                          <TableCell className="font-mono text-sm" data-testid={`text-transaction-id-${transaction.id}`}>
                            {transaction.id.slice(0, 8)}...
                          </TableCell>
                          <TableCell data-testid={`text-transaction-user-${transaction.id}`}>
                            {transaction.username}
                          </TableCell>
                          <TableCell className="font-medium" data-testid={`text-transaction-amount-${transaction.id}`}>
                            {formatCurrency(transaction.amount, transaction.currency)}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center space-x-2">
                              {getPaymentMethodIcon(transaction.paymentMethod)}
                              <span className="capitalize" data-testid={`text-payment-method-${transaction.id}`}>
                                {transaction.paymentMethod.replace('_', ' ')}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge className={getStatusColor(transaction.status)} data-testid={`badge-transaction-status-${transaction.id}`}>
                              {transaction.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="max-w-xs truncate" data-testid={`text-transaction-description-${transaction.id}`}>
                            {transaction.description}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground" data-testid={`text-transaction-timestamp-${transaction.id}`}>
                            {new Date(transaction.timestamp).toLocaleString('ja-JP')}
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

        <TabsContent value="billing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>暗号化請求ログ</CardTitle>
              <CardDescription>
                プライバシー保護された請求書管理
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  暗号化請求ログ機能は開発中です。
                  すべての請求データはエンドツーエンド暗号化されて保存されます。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="commissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>プラグイン開発者収益分配</CardTitle>
              <CardDescription>
                自動収益分配システムと統計
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  プラグイン開発者への自動収益分配機能は開発中です。
                  現在、{formatCurrency(stats?.pluginCommissions || 0, 'USD')}が分配対象です。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>決済プロバイダー設定</CardTitle>
              <CardDescription>
                日本ユーザー向け決済オプションとTelegram協力プロバイダー
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Telegram Stars設定 */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Star className="h-6 w-6 text-yellow-500" />
                    <div>
                      <h3 className="font-medium">Telegram Stars</h3>
                      <p className="text-sm text-muted-foreground">
                        Telegram公式決済システム（推奨）
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    有効
                  </Badge>
                </div>
                <div className="ml-9 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>手数料:</span>
                    <span className="font-medium text-green-600">無料</span>
                  </div>
                  <div className="flex justify-between">
                    <span>処理時間:</span>
                    <span>即座</span>
                  </div>
                  <div className="flex justify-between">
                    <span>利用可能地域:</span>
                    <span>全世界</span>
                  </div>
                </div>
              </div>

              <hr />

              {/* PayPay設定 */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Smartphone className="h-6 w-6 text-red-500" />
                    <div>
                      <h3 className="font-medium">PayPay</h3>
                      <p className="text-sm text-muted-foreground">
                        日本最大のモバイル決済サービス
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    有効
                  </Badge>
                </div>
                <div className="ml-9 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>手数料:</span>
                    <span className="font-medium text-green-600">無料（PayPay残高）</span>
                  </div>
                  <div className="flex justify-between">
                    <span>処理時間:</span>
                    <span>即座</span>
                  </div>
                  <div className="flex justify-between">
                    <span>利用可能地域:</span>
                    <span>日本のみ</span>
                  </div>
                  <div className="flex justify-between">
                    <span>特徴:</span>
                    <span>QRコード決済対応</span>
                  </div>
                </div>
              </div>

              <hr />

              {/* PayPal設定 */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Network className="h-6 w-6 text-blue-600" />
                    <div>
                      <h3 className="font-medium">PayPal</h3>
                      <p className="text-sm text-muted-foreground">
                        グローバル決済プラットフォーム
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    有効
                  </Badge>
                </div>
                <div className="ml-9 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>手数料:</span>
                    <span>3.6% + 40円</span>
                  </div>
                  <div className="flex justify-between">
                    <span>処理時間:</span>
                    <span>即座</span>
                  </div>
                  <div className="flex justify-between">
                    <span>利用可能地域:</span>
                    <span>全世界</span>
                  </div>
                  <div className="flex justify-between">
                    <span>特徴:</span>
                    <span>ゲスト決済対応</span>
                  </div>
                </div>
              </div>

              <hr />

              {/* クレジットカード設定 */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <CreditCard className="h-6 w-6 text-gray-600" />
                    <div>
                      <h3 className="font-medium">クレジットカード</h3>
                      <p className="text-sm text-muted-foreground">
                        Visa, Mastercard, JCB, Amex対応
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    有効
                  </Badge>
                </div>
                <div className="ml-9 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>手数料:</span>
                    <span>3.6%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>処理時間:</span>
                    <span>即座</span>
                  </div>
                  <div className="flex justify-between">
                    <span>利用可能地域:</span>
                    <span>全世界</span>
                  </div>
                  <div className="flex justify-between">
                    <span>セキュリティ:</span>
                    <span>3D Secure対応</span>
                  </div>
                </div>
              </div>

              <Alert className="mt-6">
                <Settings className="h-4 w-4" />
                <AlertDescription>
                  <strong>日本ユーザー向け最適化:</strong> 
                  日本在住のユーザーには自動的にPayPayとTelegram Starsが優先表示されます。
                  海外ユーザーにはPayPalとクレジットカードが表示されます。
                </AlertDescription>
              </Alert>

              <Alert>
                <Star className="h-4 w-4" />
                <AlertDescription>
                  <strong>Telegram協力プロバイダー:</strong>
                  Telegram Starsは手数料無料で最も経済的な決済方法です。
                  ユーザーにはTelegram Starsの利用を推奨しています。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
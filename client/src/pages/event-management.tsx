import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Bell, Calendar, Activity, AlertCircle, CheckCircle, Clock, Filter } from "lucide-react";
import { useState } from "react";

interface Event {
  id: string;
  type: 'system' | 'user' | 'payment' | 'api' | 'security';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'processing' | 'resolved' | 'failed';
  timestamp: string;
  source: string;
  metadata: Record<string, any>;
}

interface EventStats {
  totalEvents: number;
  pendingEvents: number;
  resolvedToday: number;
  criticalEvents: number;
}

export default function EventManagement() {
  const [filterType, setFilterType] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");

  const { data: events, isLoading: eventsLoading } = useQuery<Event[]>({
    queryKey: ['/api/events'],
  });

  const { data: stats, isLoading: statsLoading } = useQuery<EventStats>({
    queryKey: ['/api/events/stats'],
  });

  const filteredEvents = events?.filter(event => {
    const matchesType = filterType === "all" || event.type === filterType;
    const matchesSearch = event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesType && matchesSearch;
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'processing': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'failed': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'system': return <Activity className="h-4 w-4" />;
      case 'user': return <Bell className="h-4 w-4" />;
      case 'payment': return <CheckCircle className="h-4 w-4" />;
      case 'api': return <AlertCircle className="h-4 w-4" />;
      case 'security': return <AlertCircle className="h-4 w-4 text-red-500" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  if (eventsLoading || statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">イベント管理</h1>
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
          <h1 className="text-3xl font-bold">イベント管理</h1>
          <p className="text-muted-foreground">
            リアルタイムイベント処理と個人サーバー管理ボタン
          </p>
        </div>
        <Button data-testid="button-create-event">
          <Calendar className="h-4 w-4 mr-2" />
          新規イベント
        </Button>
      </div>

      {/* 統計カード */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">総イベント数</CardTitle>
            <Bell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-total-events">
              {stats?.totalEvents?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              過去30日間
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">処理待ち</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-pending-events">
              {stats?.pendingEvents || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              要対応イベント
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">本日解決</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-resolved-today">
              {stats?.resolvedToday || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              +15% from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">重要アラート</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-critical-events">
              {stats?.criticalEvents || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              クリティカル・重要
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="events" className="space-y-4">
        <TabsList>
          <TabsTrigger value="events">イベントログ</TabsTrigger>
          <TabsTrigger value="realtime">リアルタイム監視</TabsTrigger>
          <TabsTrigger value="personal-servers">個人サーバー管理</TabsTrigger>
        </TabsList>

        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>イベントログ</CardTitle>
              <CardDescription>
                システム全体のイベント履歴と処理状況
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 mb-4">
                <div className="relative flex-1 max-w-sm">
                  <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="イベントを検索..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                    data-testid="input-event-search"
                  />
                </div>
                <select 
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-3 py-2 border rounded-md bg-background"
                  data-testid="select-event-type"
                >
                  <option value="all">すべてのタイプ</option>
                  <option value="system">システム</option>
                  <option value="user">ユーザー</option>
                  <option value="payment">決済</option>
                  <option value="api">API</option>
                  <option value="security">セキュリティ</option>
                </select>
              </div>

              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>タイプ</TableHead>
                      <TableHead>イベント</TableHead>
                      <TableHead>重要度</TableHead>
                      <TableHead>ステータス</TableHead>
                      <TableHead>ソース</TableHead>
                      <TableHead>時刻</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredEvents?.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center py-4">
                          <Alert>
                            <AlertDescription>
                              該当するイベントが見つかりません。
                            </AlertDescription>
                          </Alert>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredEvents?.map((event) => (
                        <TableRow key={event.id} data-testid={`row-event-${event.id}`}>
                          <TableCell>
                            <div className="flex items-center space-x-2">
                              {getTypeIcon(event.type)}
                              <span className="capitalize" data-testid={`text-event-type-${event.id}`}>
                                {event.type}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div>
                              <div className="font-medium" data-testid={`text-event-title-${event.id}`}>
                                {event.title}
                              </div>
                              <div className="text-sm text-muted-foreground" data-testid={`text-event-description-${event.id}`}>
                                {event.description}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge className={getSeverityColor(event.severity)} data-testid={`badge-severity-${event.id}`}>
                              {event.severity}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge className={getStatusColor(event.status)} data-testid={`badge-status-${event.id}`}>
                              {event.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm" data-testid={`text-event-source-${event.id}`}>
                            {event.source}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground" data-testid={`text-event-timestamp-${event.id}`}>
                            {new Date(event.timestamp).toLocaleString('ja-JP')}
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

        <TabsContent value="realtime" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>リアルタイム監視</CardTitle>
              <CardDescription>
                進行中のイベントとリアルタイム処理状況
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  リアルタイム監視ダッシュボードは開発中です。
                  WebSocket経由でリアルタイムイベントを監視できます。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="personal-servers" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>個人サーバー管理ボタン</CardTitle>
              <CardDescription>
                Telegram個人ログサーバーの管理とワンクリック操作
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  個人サーバー管理機能は開発中です。
                  Telegramの管理者ボタンで最小限の権限での操作が可能になります。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
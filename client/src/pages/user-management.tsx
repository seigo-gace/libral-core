import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Users, UserPlus, Shield, Settings, Search, MoreHorizontal } from "lucide-react";
import { useState } from "react";

interface User {
  id: string;
  username: string;
  email: string;
  telegramId?: string;
  status: 'active' | 'inactive' | 'suspended';
  role: 'user' | 'admin' | 'developer';
  createdAt: string;
  lastActive: string;
  personalServerEnabled: boolean;
}

interface UserStats {
  totalUsers: number;
  activeUsers: number;
  newUsersToday: number;
  personalServersActive: number;
}

export default function UserManagement() {
  const [searchTerm, setSearchTerm] = useState("");

  const { data: users, isLoading: usersLoading } = useQuery<User[]>({
    queryKey: ['/api/users'],
  });

  const { data: stats, isLoading: statsLoading } = useQuery<UserStats>({
    queryKey: ['/api/users/stats'],
  });

  const filteredUsers = users?.filter(user => 
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'developer': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'user': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'inactive': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
      case 'suspended': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  if (usersLoading || statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">ユーザー管理</h1>
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
          <h1 className="text-3xl font-bold">ユーザー管理</h1>
          <p className="text-muted-foreground">
            Telegram個人ログサーバーとユーザーデータ主権管理
          </p>
        </div>
        <Button data-testid="button-add-user">
          <UserPlus className="h-4 w-4 mr-2" />
          新規ユーザー
        </Button>
      </div>

      {/* 統計カード */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">総ユーザー数</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-total-users">
              {stats?.totalUsers?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">アクティブユーザー</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-active-users">
              {stats?.activeUsers?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              過去24時間
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">本日の新規</CardTitle>
            <UserPlus className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-new-users-today">
              {stats?.newUsersToday || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              +8% from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">個人サーバー</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid="text-personal-servers">
              {stats?.personalServersActive || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              アクティブなTelegramサーバー
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users">ユーザー一覧</TabsTrigger>
          <TabsTrigger value="servers">個人サーバー</TabsTrigger>
          <TabsTrigger value="privacy">プライバシー設定</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>ユーザー一覧</CardTitle>
              <CardDescription>
                すべてのユーザーとその権限、アクセス状況
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 mb-4">
                <div className="relative flex-1 max-w-sm">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="ユーザー名またはメールで検索..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                    data-testid="input-user-search"
                  />
                </div>
              </div>

              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ユーザー名</TableHead>
                      <TableHead>メール</TableHead>
                      <TableHead>役割</TableHead>
                      <TableHead>ステータス</TableHead>
                      <TableHead>個人サーバー</TableHead>
                      <TableHead>最終アクティブ</TableHead>
                      <TableHead className="w-[50px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers?.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-4">
                          <Alert>
                            <AlertDescription>
                              該当するユーザーが見つかりません。
                            </AlertDescription>
                          </Alert>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredUsers?.map((user) => (
                        <TableRow key={user.id} data-testid={`row-user-${user.id}`}>
                          <TableCell className="font-medium" data-testid={`text-username-${user.id}`}>
                            {user.username}
                          </TableCell>
                          <TableCell data-testid={`text-email-${user.id}`}>
                            {user.email}
                          </TableCell>
                          <TableCell>
                            <Badge className={getRoleColor(user.role)} data-testid={`badge-role-${user.id}`}>
                              {user.role}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge className={getStatusColor(user.status)} data-testid={`badge-status-${user.id}`}>
                              {user.status}
                            </Badge>
                          </TableCell>
                          <TableCell data-testid={`text-personal-server-${user.id}`}>
                            {user.personalServerEnabled ? (
                              <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                有効
                              </Badge>
                            ) : (
                              <Badge variant="outline">無効</Badge>
                            )}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground" data-testid={`text-last-active-${user.id}`}>
                            {new Date(user.lastActive).toLocaleDateString('ja-JP')}
                          </TableCell>
                          <TableCell>
                            <Button variant="ghost" size="sm" data-testid={`button-actions-${user.id}`}>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
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

        <TabsContent value="servers" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Telegram個人ログサーバー</CardTitle>
              <CardDescription>
                ユーザーデータ主権を保証する個人サーバー管理
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  Telegram個人ログサーバー管理機能は開発中です。
                  現在、{stats?.personalServersActive || 0}台のサーバーがアクティブです。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="privacy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>プライバシー設定</CardTitle>
              <CardDescription>
                GDPR準拠とデータ主権設定
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  プライバシー設定管理機能は開発中です。
                  すべてのデータはユーザー個人のTelegramサーバーに保存されます。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
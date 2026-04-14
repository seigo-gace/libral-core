import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { FuturisticCard, MetricDisplay } from "@/components/ui/futuristic-card";
import { 
  Activity, 
  TrendingUp, 
  Users, 
  Database, 
  Cpu, 
  MemoryStick, 
  Network, 
  HardDrive,
  Calendar,
  BarChart3,
  Download
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

// Mock data for analytics
const systemPerformanceData = [
  { time: '00:00', cpu: 25, memory: 65, network: 45 },
  { time: '04:00', cpu: 15, memory: 58, network: 32 },
  { time: '08:00', cpu: 45, memory: 72, network: 68 },
  { time: '12:00', cpu: 35, memory: 68, network: 55 },
  { time: '16:00', cpu: 55, memory: 75, network: 78 },
  { time: '20:00', cpu: 42, memory: 71, network: 61 },
];

const apiUsageData = [
  { endpoint: '/api/aegis/encrypt', calls: 1247, avgTime: 45 },
  { endpoint: '/api/modules', calls: 856, avgTime: 12 },
  { endpoint: '/api/system/metrics', calls: 2341, avgTime: 8 },
  { endpoint: '/api/events', calls: 623, avgTime: 25 },
  { endpoint: '/api/stamps/create', calls: 342, avgTime: 350 },
];

const moduleUsageData = [
  { name: 'Aegis-PGP', value: 35, color: '#3b82f6' },
  { name: 'Communication', value: 25, color: '#10b981' },
  { name: 'Payment', value: 20, color: '#f59e0b' },
  { name: 'Events', value: 15, color: '#ef4444' },
  { name: 'Others', value: 5, color: '#8b5cf6' },
];

const userActivityData = [
  { date: '01/15', activeUsers: 23, newUsers: 5, sessions: 145 },
  { date: '01/16', activeUsers: 28, newUsers: 7, sessions: 167 },
  { date: '01/17', activeUsers: 31, newUsers: 4, sessions: 189 },
  { date: '01/18', activeUsers: 26, newUsers: 6, sessions: 156 },
  { date: '01/19', activeUsers: 35, newUsers: 9, sessions: 203 },
  { date: '01/20', activeUsers: 29, newUsers: 3, sessions: 178 },
  { date: '01/21', activeUsers: 33, newUsers: 8, sessions: 195 },
];

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('performance');

  const { data: systemStats } = useQuery({
    queryKey: ['/api/analytics/system', timeRange],
    queryFn: async () => ({
      totalRequests: 125847,
      averageResponseTime: 45,
      uptime: 99.8,
      errorRate: 0.12,
      peakConcurrentUsers: 156,
      dataTransferred: '2.8 TB'
    })
  });

  const { data: moduleStats } = useQuery({
    queryKey: ['/api/analytics/modules', timeRange],
    queryFn: async () => ({
      totalModules: 8,
      activeModules: 7,
      healthyModules: 6,
      moduleRestarts: 3,
      averageUptime: 99.5
    })
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="container mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center space-x-3">
              <BarChart3 className="h-8 w-8 text-blue-400" />
              <span>システム分析</span>
            </h1>
            <p className="text-blue-200/80 mt-2">
              Libral Coreシステムのパフォーマンスと使用状況分析
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-[140px] bg-white/5 border-white/20 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1d">過去24時間</SelectItem>
                <SelectItem value="7d">過去7日間</SelectItem>
                <SelectItem value="30d">過去30日間</SelectItem>
                <SelectItem value="90d">過去90日間</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" className="text-white border-white/20 hover:bg-white/10">
              <Download className="h-4 w-4 mr-2" />
              レポート出力
            </Button>
            <Button 
              onClick={() => window.location.href = '/admin-dashboard'}
              variant="outline"
              className="text-white border-white/20 hover:bg-white/10"
            >
              戻る
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <FuturisticCard glowColor="blue" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={systemStats?.totalRequests.toLocaleString() || '0'}
                label="TOTAL REQUESTS"
                icon={<Activity className="h-4 w-4" />}
                color="blue"
                trend="up"
              />
            </CardContent>
          </FuturisticCard>
          
          <FuturisticCard glowColor="green" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={`${systemStats?.uptime || 0}%`}
                label="UPTIME"
                icon={<TrendingUp className="h-4 w-4" />}
                color="green"
                trend="neutral"
              />
            </CardContent>
          </FuturisticCard>
          
          <FuturisticCard glowColor="yellow" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={`${systemStats?.averageResponseTime || 0}ms`}
                label="AVG RESPONSE"
                icon={<Network className="h-4 w-4" />}
                color="yellow"
                trend="down"
              />
            </CardContent>
          </FuturisticCard>
          
          <FuturisticCard glowColor="purple" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={systemStats?.peakConcurrentUsers?.toString() || '0'}
                label="PEAK USERS"
                icon={<Users className="h-4 w-4" />}
                color="purple"
                trend="up"
              />
            </CardContent>
          </FuturisticCard>
          
          <FuturisticCard glowColor="red" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={`${systemStats?.errorRate || 0}%`}
                label="ERROR RATE"
                icon={<Database className="h-4 w-4" />}
                color="red"
                trend="down"
              />
            </CardContent>
          </FuturisticCard>
          
          <FuturisticCard glowColor="blue" active={true}>
            <CardContent className="p-4">
              <MetricDisplay
                value={systemStats?.dataTransferred || '0 GB'}
                label="DATA TRANSFER"
                icon={<HardDrive className="h-4 w-4" />}
                color="blue"
                trend="up"
              />
            </CardContent>
          </FuturisticCard>
        </div>

        {/* Analytics Tabs */}
        <Tabs value={selectedMetric} onValueChange={setSelectedMetric} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white/5 backdrop-blur-sm">
            <TabsTrigger value="performance">パフォーマンス</TabsTrigger>
            <TabsTrigger value="usage">使用状況</TabsTrigger>
            <TabsTrigger value="users">ユーザー</TabsTrigger>
            <TabsTrigger value="modules">モジュール</TabsTrigger>
          </TabsList>

          {/* Performance Analytics */}
          <TabsContent value="performance" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              <FuturisticCard glowColor="blue" active={true}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-white">
                    <Cpu className="h-5 w-5" />
                    <span>システムパフォーマンス</span>
                  </CardTitle>
                  <CardDescription className="text-blue-200/80">
                    CPU、メモリ、ネットワークの使用状況
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={systemPerformanceData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="time" stroke="#9ca3af" />
                      <YAxis stroke="#9ca3af" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1f2937', 
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                      />
                      <Line type="monotone" dataKey="cpu" stroke="#3b82f6" strokeWidth={2} name="CPU %" />
                      <Line type="monotone" dataKey="memory" stroke="#10b981" strokeWidth={2} name="Memory %" />
                      <Line type="monotone" dataKey="network" stroke="#f59e0b" strokeWidth={2} name="Network %" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </FuturisticCard>
              
              <FuturisticCard glowColor="green" active={true}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-white">
                    <Activity className="h-5 w-5" />
                    <span>API使用状況</span>
                  </CardTitle>
                  <CardDescription className="text-green-200/80">
                    エンドポイント別の呼び出し回数と応答時間
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {apiUsageData.map((api, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div className="flex-1">
                          <div className="font-mono text-sm text-white">{api.endpoint}</div>
                          <div className="text-xs text-gray-400">{api.calls.toLocaleString()} calls</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-white">{api.avgTime}ms</div>
                          <div className="text-xs text-gray-400">平均応答時間</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </FuturisticCard>
            </div>
          </TabsContent>

          {/* Usage Analytics */}
          <TabsContent value="usage" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              <FuturisticCard glowColor="purple" active={true}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-white">
                    <BarChart3 className="h-5 w-5" />
                    <span>モジュール使用率</span>
                  </CardTitle>
                  <CardDescription className="text-purple-200/80">
                    各モジュールの使用状況分布
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={moduleUsageData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}%`}
                      >
                        {moduleUsageData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1f2937', 
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </FuturisticCard>
              
              <FuturisticCard glowColor="yellow" active={true}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-white">
                    <Database className="h-5 w-5" />
                    <span>データベース統計</span>
                  </CardTitle>
                  <CardDescription className="text-yellow-200/80">
                    データベースの使用状況とパフォーマンス
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-3 bg-white/5 rounded-lg">
                        <div className="text-2xl font-bold text-white">156</div>
                        <div className="text-sm text-gray-400">クエリ/秒</div>
                      </div>
                      <div className="p-3 bg-white/5 rounded-lg">
                        <div className="text-2xl font-bold text-white">94.2%</div>
                        <div className="text-sm text-gray-400">キャッシュヒット率</div>
                      </div>
                      <div className="p-3 bg-white/5 rounded-lg">
                        <div className="text-2xl font-bold text-white">2.5GB</div>
                        <div className="text-sm text-gray-400">データサイズ</div>
                      </div>
                      <div className="p-3 bg-white/5 rounded-lg">
                        <div className="text-2xl font-bold text-white">23/100</div>
                        <div className="text-sm text-gray-400">接続数</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </FuturisticCard>
            </div>
          </TabsContent>

          {/* User Analytics */}
          <TabsContent value="users" className="space-y-6">
            <FuturisticCard glowColor="blue" active={true}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Users className="h-5 w-5" />
                  <span>ユーザーアクティビティ</span>
                </CardTitle>
                <CardDescription className="text-cyan-200/80">
                  ユーザーの活動状況とセッション情報
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={userActivityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="date" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1f2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#fff'
                      }}
                    />
                    <Area type="monotone" dataKey="sessions" stackId="1" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.6} name="セッション数" />
                    <Area type="monotone" dataKey="activeUsers" stackId="2" stroke="#10b981" fill="#10b981" fillOpacity={0.6} name="アクティブユーザー" />
                    <Area type="monotone" dataKey="newUsers" stackId="3" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.6} name="新規ユーザー" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </FuturisticCard>
          </TabsContent>

          {/* Module Analytics */}
          <TabsContent value="modules" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              <FuturisticCard glowColor="red" active={true}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-white">
                    <MemoryStick className="h-5 w-5" />
                    <span>モジュール統計</span>
                  </CardTitle>
                  <CardDescription className="text-red-200/80">
                    モジュールの稼働状況とパフォーマンス
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-white/5 rounded-lg">
                      <div className="text-3xl font-bold text-white">{moduleStats?.totalModules || 0}</div>
                      <div className="text-sm text-gray-400">総モジュール数</div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg">
                      <div className="text-3xl font-bold text-green-400">{moduleStats?.activeModules || 0}</div>
                      <div className="text-sm text-gray-400">稼働中</div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg">
                      <div className="text-3xl font-bold text-blue-400">{moduleStats?.healthyModules || 0}</div>
                      <div className="text-sm text-gray-400">正常稼働</div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg">
                      <div className="text-3xl font-bold text-yellow-400">{moduleStats?.averageUptime || 0}%</div>
                      <div className="text-sm text-gray-400">平均稼働率</div>
                    </div>
                  </div>
                </CardContent>
              </FuturisticCard>
              
              <FuturisticCard glowColor="green" active={true}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-white">
                    <Calendar className="h-5 w-5" />
                    <span>モジュール可用性</span>
                  </CardTitle>
                  <CardDescription className="text-green-200/80">
                    過去7日間のモジュール稼働状況
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {['aegis-pgp', 'communication-gateway', 'user-management', 'event-management', 'payment-management'].map((module, index) => (
                      <div key={module} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div className="font-medium text-white capitalize">
                          {module.replace('-', ' ')}
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="text-sm text-green-400">99.{9 - index}%</div>
                          <div className="flex space-x-1">
                            {[...Array(7)].map((_, day) => (
                              <div 
                                key={day} 
                                className={`w-3 h-3 rounded-sm ${Math.random() > 0.1 ? 'bg-green-500' : 'bg-red-500'}`}
                                title={`Day ${day + 1}`}
                              />
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </FuturisticCard>
            </div>
          </TabsContent>
        </Tabs>

      </div>
    </div>
  );
}
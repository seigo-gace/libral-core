import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FuturisticCard } from "@/components/ui/futuristic-card";
import { Badge } from "@/components/ui/badge";
import { 
  Settings as SettingsIcon, 
  Save, 
  RefreshCw, 
  Shield, 
  Database, 
  Network, 
  Bell, 
  User, 
  Palette, 
  Globe,
  Key,
  Download,
  Upload,
  Trash2
} from "lucide-react";
import { apiRequest } from "@/lib/queryClient";

interface SystemSettings {
  general: {
    systemName: string;
    adminEmail: string;
    maintenanceMode: boolean;
    debugMode: boolean;
    logLevel: string;
  };
  security: {
    sessionTimeout: number;
    maxLoginAttempts: number;
    passwordPolicy: string;
    twoFactorRequired: boolean;
    encryptionLevel: string;
  };
  notifications: {
    emailNotifications: boolean;
    telegramNotifications: boolean;
    webhookNotifications: boolean;
    notificationThreshold: string;
  };
  performance: {
    cacheEnabled: boolean;
    cacheTTL: number;
    maxConcurrentUsers: number;
    rateLimitEnabled: boolean;
    rateLimitPerMinute: number;
  };
}

const defaultSettings: SystemSettings = {
  general: {
    systemName: 'Libral Core',
    adminEmail: 'admin@libral.core',
    maintenanceMode: false,
    debugMode: false,
    logLevel: 'info'
  },
  security: {
    sessionTimeout: 24,
    maxLoginAttempts: 3,
    passwordPolicy: 'strong',
    twoFactorRequired: true,
    encryptionLevel: 'aes-256'
  },
  notifications: {
    emailNotifications: true,
    telegramNotifications: true,
    webhookNotifications: false,
    notificationThreshold: 'medium'
  },
  performance: {
    cacheEnabled: true,
    cacheTTL: 3600,
    maxConcurrentUsers: 1000,
    rateLimitEnabled: true,
    rateLimitPerMinute: 100
  }
};

export default function Settings() {
  const [settings, setSettings] = useState<SystemSettings>(defaultSettings);
  const [isDirty, setIsDirty] = useState(false);
  const [activeTab, setActiveTab] = useState('general');

  const queryClient = useQueryClient();

  const { data: currentSettings } = useQuery<SystemSettings>({
    queryKey: ['/api/settings'],
    queryFn: async () => {
      // Mock API call - in real implementation, this would fetch from backend
      return defaultSettings;
    }
  });

  const saveSettingsMutation = useMutation({
    mutationFn: async (newSettings: SystemSettings) => {
      return apiRequest('/api/settings', 'PUT', newSettings);
    },
    onSuccess: () => {
      setIsDirty(false);
      queryClient.invalidateQueries({ queryKey: ['/api/settings'] });
    }
  });

  const exportSettingsMutation = useMutation({
    mutationFn: async () => {
      return apiRequest('/api/settings/export', 'GET');
    },
    onSuccess: (data) => {
      // Download settings as JSON file
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `libral-core-settings-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  });

  const updateSetting = (category: keyof SystemSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
    setIsDirty(true);
  };

  const handleSave = () => {
    saveSettingsMutation.mutate(settings);
  };

  const handleExport = () => {
    exportSettingsMutation.mutate();
  };

  const handleReset = () => {
    setSettings(defaultSettings);
    setIsDirty(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="container mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center space-x-3">
              <SettingsIcon className="h-8 w-8 text-blue-400" />
              <span>システム設定</span>
            </h1>
            <p className="text-blue-200/80 mt-2">
              Libral Coreシステムの設定を管理します
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {isDirty && (
              <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                未保存の変更があります
              </Badge>
            )}
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={exportSettingsMutation.isPending}
              className="text-white border-white/20 hover:bg-white/10"
            >
              <Download className="h-4 w-4 mr-2" />
              設定をエクスポート
            </Button>
            <Button
              onClick={handleSave}
              disabled={!isDirty || saveSettingsMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700"
              data-testid="button-save-settings"
            >
              <Save className="h-4 w-4 mr-2" />
              {saveSettingsMutation.isPending ? '保存中...' : '設定を保存'}
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

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white/5 backdrop-blur-sm">
            <TabsTrigger value="general">一般</TabsTrigger>
            <TabsTrigger value="security">セキュリティ</TabsTrigger>
            <TabsTrigger value="notifications">通知</TabsTrigger>
            <TabsTrigger value="performance">パフォーマンス</TabsTrigger>
          </TabsList>

          {/* General Settings */}
          <TabsContent value="general" className="space-y-6">
            <FuturisticCard glowColor="blue" active={true}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Globe className="h-5 w-5" />
                  <span>基本設定</span>
                </CardTitle>
                <CardDescription className="text-blue-200/80">
                  システムの基本的な設定を管理します
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="systemName" className="text-white">システム名</Label>
                    <Input
                      id="systemName"
                      value={settings.general.systemName}
                      onChange={(e) => updateSetting('general', 'systemName', e.target.value)}
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="adminEmail" className="text-white">管理者メールアドレス</Label>
                    <Input
                      id="adminEmail"
                      type="email"
                      value={settings.general.adminEmail}
                      onChange={(e) => updateSetting('general', 'adminEmail', e.target.value)}
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="logLevel" className="text-white">ログレベル</Label>
                    <Select value={settings.general.logLevel} onValueChange={(value) => updateSetting('general', 'logLevel', value)}>
                      <SelectTrigger className="bg-white/5 border-white/20 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="debug">Debug</SelectItem>
                        <SelectItem value="info">Info</SelectItem>
                        <SelectItem value="warn">Warning</SelectItem>
                        <SelectItem value="error">Error</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="maintenanceMode" className="text-white">メンテナンスモード</Label>
                      <Switch
                        id="maintenanceMode"
                        checked={settings.general.maintenanceMode}
                        onCheckedChange={(checked) => updateSetting('general', 'maintenanceMode', checked)}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label htmlFor="debugMode" className="text-white">デバッグモード</Label>
                      <Switch
                        id="debugMode"
                        checked={settings.general.debugMode}
                        onCheckedChange={(checked) => updateSetting('general', 'debugMode', checked)}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </FuturisticCard>
          </TabsContent>

          {/* Security Settings */}
          <TabsContent value="security" className="space-y-6">
            <FuturisticCard glowColor="red" active={true}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Shield className="h-5 w-5" />
                  <span>セキュリティ設定</span>
                </CardTitle>
                <CardDescription className="text-red-200/80">
                  システムのセキュリティポリシーを設定します
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="sessionTimeout" className="text-white">セッションタイムアウト（時間）</Label>
                    <Input
                      id="sessionTimeout"
                      type="number"
                      value={settings.security.sessionTimeout}
                      onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="maxLoginAttempts" className="text-white">最大ログイン試行回数</Label>
                    <Input
                      id="maxLoginAttempts"
                      type="number"
                      value={settings.security.maxLoginAttempts}
                      onChange={(e) => updateSetting('security', 'maxLoginAttempts', parseInt(e.target.value))}
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label className="text-white">パスワードポリシー</Label>
                    <Select value={settings.security.passwordPolicy} onValueChange={(value) => updateSetting('security', 'passwordPolicy', value)}>
                      <SelectTrigger className="bg-white/5 border-white/20 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="basic">基本（8文字以上）</SelectItem>
                        <SelectItem value="standard">標準（8文字+数字+記号）</SelectItem>
                        <SelectItem value="strong">強力（12文字+複雑な条件）</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-white">暗号化レベル</Label>
                    <Select value={settings.security.encryptionLevel} onValueChange={(value) => updateSetting('security', 'encryptionLevel', value)}>
                      <SelectTrigger className="bg-white/5 border-white/20 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="aes-128">AES-128</SelectItem>
                        <SelectItem value="aes-256">AES-256</SelectItem>
                        <SelectItem value="aegis-pgp">Aegis-PGP (推奨)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="twoFactorRequired" className="text-white">二要素認証を必須にする</Label>
                    <p className="text-sm text-gray-400">全ユーザーに二要素認証を要求します</p>
                  </div>
                  <Switch
                    id="twoFactorRequired"
                    checked={settings.security.twoFactorRequired}
                    onCheckedChange={(checked) => updateSetting('security', 'twoFactorRequired', checked)}
                  />
                </div>
              </CardContent>
            </FuturisticCard>
          </TabsContent>

          {/* Notification Settings */}
          <TabsContent value="notifications" className="space-y-6">
            <FuturisticCard glowColor="yellow" active={true}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Bell className="h-5 w-5" />
                  <span>通知設定</span>
                </CardTitle>
                <CardDescription className="text-yellow-200/80">
                  システム通知の設定を管理します
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="emailNotifications" className="text-white">メール通知</Label>
                      <p className="text-sm text-gray-400">重要なイベントをメールで通知します</p>
                    </div>
                    <Switch
                      id="emailNotifications"
                      checked={settings.notifications.emailNotifications}
                      onCheckedChange={(checked) => updateSetting('notifications', 'emailNotifications', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="telegramNotifications" className="text-white">Telegram通知</Label>
                      <p className="text-sm text-gray-400">Telegramボットで通知を送信します</p>
                    </div>
                    <Switch
                      id="telegramNotifications"
                      checked={settings.notifications.telegramNotifications}
                      onCheckedChange={(checked) => updateSetting('notifications', 'telegramNotifications', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="webhookNotifications" className="text-white">Webhook通知</Label>
                      <p className="text-sm text-gray-400">外部システムにWebhookで通知します</p>
                    </div>
                    <Switch
                      id="webhookNotifications"
                      checked={settings.notifications.webhookNotifications}
                      onCheckedChange={(checked) => updateSetting('notifications', 'webhookNotifications', checked)}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-white">通知しきい値</Label>
                  <Select value={settings.notifications.notificationThreshold} onValueChange={(value) => updateSetting('notifications', 'notificationThreshold', value)}>
                    <SelectTrigger className="bg-white/5 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">低（全ての通知）</SelectItem>
                      <SelectItem value="medium">中（重要な通知のみ）</SelectItem>
                      <SelectItem value="high">高（緊急時のみ）</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </FuturisticCard>
          </TabsContent>

          {/* Performance Settings */}
          <TabsContent value="performance" className="space-y-6">
            <FuturisticCard glowColor="green" active={true}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Network className="h-5 w-5" />
                  <span>パフォーマンス設定</span>
                </CardTitle>
                <CardDescription className="text-green-200/80">
                  システムのパフォーマンスを最適化します
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="cacheTTL" className="text-white">キャッシュ有効期間（秒）</Label>
                    <Input
                      id="cacheTTL"
                      type="number"
                      value={settings.performance.cacheTTL}
                      onChange={(e) => updateSetting('performance', 'cacheTTL', parseInt(e.target.value))}
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="maxConcurrentUsers" className="text-white">最大同時接続ユーザー数</Label>
                    <Input
                      id="maxConcurrentUsers"
                      type="number"
                      value={settings.performance.maxConcurrentUsers}
                      onChange={(e) => updateSetting('performance', 'maxConcurrentUsers', parseInt(e.target.value))}
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="rateLimitPerMinute" className="text-white">レート制限（分当たり）</Label>
                    <Input
                      id="rateLimitPerMinute"
                      type="number"
                      value={settings.performance.rateLimitPerMinute}
                      onChange={(e) => updateSetting('performance', 'rateLimitPerMinute', parseInt(e.target.value))}
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="cacheEnabled" className="text-white">キャッシュを有効にする</Label>
                      <Switch
                        id="cacheEnabled"
                        checked={settings.performance.cacheEnabled}
                        onCheckedChange={(checked) => updateSetting('performance', 'cacheEnabled', checked)}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label htmlFor="rateLimitEnabled" className="text-white">レート制限を有効にする</Label>
                      <Switch
                        id="rateLimitEnabled"
                        checked={settings.performance.rateLimitEnabled}
                        onCheckedChange={(checked) => updateSetting('performance', 'rateLimitEnabled', checked)}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </FuturisticCard>
          </TabsContent>
        </Tabs>

        {/* Actions */}
        <div className="flex justify-center space-x-4">
          <Button
            variant="outline"
            onClick={handleReset}
            className="text-white border-white/20 hover:bg-white/10"
            data-testid="button-reset-settings"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            デフォルトに戻す
          </Button>
          <Button
            variant="outline"
            className="text-red-400 border-red-400 hover:bg-red-400/10"
            data-testid="button-danger-settings"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            危険な操作
          </Button>
        </div>

      </div>
    </div>
  );
}
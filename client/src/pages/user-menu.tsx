import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Package, 
  Star, 
  Download, 
  Settings, 
  Shield, 
  Zap, 
  Users, 
  MessageSquare, 
  Image,
  Video,
  Bot,
  Palette,
  Music,
  BookOpen,
  ChevronRight,
  Info,
  Play,
  Pause,
  HelpCircle
} from "lucide-react";

interface UserPackage {
  id: string;
  name: string;
  description: string;
  category: 'ai' | 'creative' | 'social' | 'utility' | 'entertainment';
  icon: React.ReactNode;
  status: 'active' | 'inactive' | 'installing' | 'error';
  version: string;
  price: number;
  currency: string;
  features: string[];
  userCount?: number;
}

const availablePackages: UserPackage[] = [
  {
    id: 'libral-ai',
    name: 'Libral AI Assistant',
    description: 'あなた専用のAIアシスタント。チャット、画像生成、文書作成をサポート',
    category: 'ai',
    icon: <Bot className="h-6 w-6" />,
    status: 'active',
    version: '2.1.0',
    price: 0,
    currency: 'STARS',
    features: ['自然な日本語対話', 'コード生成', '文書作成支援', 'リアルタイム翻訳'],
    userCount: 15420
  },
  {
    id: 'stamp-creator',
    name: 'TxT WORLD Creator\'s',
    description: 'オリジナルスタンプとステッカーを簡単作成。Telegram直接投稿対応',
    category: 'creative',
    icon: <Image className="h-6 w-6" />,
    status: 'active',
    version: '1.5.2',
    price: 150,
    currency: 'STARS',
    features: ['AI画像生成', 'テンプレート豊富', 'Telegram連携', 'バッチ処理'],
    userCount: 8930
  },
  {
    id: 'live-video-chat',
    name: 'LIVE VIDEO CHAT',
    description: 'プライベートなライブストリーミングとビデオチャットプラットフォーム',
    category: 'social',
    icon: <Video className="h-6 w-6" />,
    status: 'installing',
    version: '3.0.1',
    price: 300,
    currency: 'STARS',
    features: ['最大100人同時配信', 'エンドツーエンド暗号化', 'スーパーチャット', 'レコーディング'],
    userCount: 5680
  },
  {
    id: 'music-studio',
    name: 'Libral Music Studio',
    description: 'AI作曲とオーディオ編集機能を統合した音楽制作スタジオ',
    category: 'creative',
    icon: <Music className="h-6 w-6" />,
    status: 'inactive',
    version: '1.2.0',
    price: 250,
    currency: 'STARS',
    features: ['AI作曲', 'マルチトラック編集', 'エフェクト豊富', 'VST対応'],
    userCount: 3240
  },
  {
    id: 'theme-designer',
    name: 'Libral Theme Designer',
    description: 'Telegramテーマとカスタムデザインを作成・共有',
    category: 'creative',
    icon: <Palette className="h-6 w-6" />,
    status: 'active',
    version: '2.3.1',
    price: 100,
    currency: 'STARS',
    features: ['カラーパレット生成', 'プレビュー機能', 'コミュニティ共有', 'ダークモード対応'],
    userCount: 12100
  }
];

export default function UserMenu() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedPackage, setSelectedPackage] = useState<UserPackage | null>(null);

  const categories = [
    { id: 'all', name: '全て', icon: <Package className="h-4 w-4" /> },
    { id: 'ai', name: 'AI', icon: <Bot className="h-4 w-4" /> },
    { id: 'creative', name: 'クリエイティブ', icon: <Palette className="h-4 w-4" /> },
    { id: 'social', name: 'ソーシャル', icon: <Users className="h-4 w-4" /> },
    { id: 'utility', name: 'ユーティリティ', icon: <Settings className="h-4 w-4" /> },
    { id: 'entertainment', name: 'エンターテイメント', icon: <Music className="h-4 w-4" /> }
  ];

  const filteredPackages = selectedCategory === 'all' 
    ? availablePackages 
    : availablePackages.filter(pkg => pkg.category === selectedCategory);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'inactive': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
      case 'installing': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Play className="h-4 w-4" />;
      case 'inactive': return <Pause className="h-4 w-4" />;
      case 'installing': return <Download className="h-4 w-4" />;
      case 'error': return <HelpCircle className="h-4 w-4" />;
      default: return <Package className="h-4 w-4" />;
    }
  };

  const formatPrice = (price: number, currency: string) => {
    if (price === 0) return '無料';
    return currency === 'STARS' ? `${price} ⭐` : `¥${price}`;
  };

  const renderPackageDetail = (pkg: UserPackage) => (
    <Card className="mt-4">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            {pkg.icon}
            <div>
              <CardTitle>{pkg.name}</CardTitle>
              <CardDescription>v{pkg.version}</CardDescription>
            </div>
          </div>
          <Badge className={getStatusColor(pkg.status)}>
            <div className="flex items-center space-x-1">
              {getStatusIcon(pkg.status)}
              <span>{pkg.status}</span>
            </div>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{pkg.description}</p>
        
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">価格:</span>
          <span className="font-bold text-lg">{formatPrice(pkg.price, pkg.currency)}</span>
        </div>

        {pkg.userCount && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">利用者数:</span>
            <span>{pkg.userCount.toLocaleString()}人</span>
          </div>
        )}

        <div>
          <h4 className="font-medium mb-2">主な機能:</h4>
          <ul className="space-y-1">
            {pkg.features.map((feature, index) => (
              <li key={index} className="flex items-center space-x-2 text-sm">
                <Star className="h-3 w-3 text-yellow-500" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="flex space-x-2">
          {pkg.status === 'active' ? (
            <>
              <Button variant="outline" className="flex-1" data-testid={`button-pause-${pkg.id}`}>
                <Pause className="h-4 w-4 mr-2" />
                一時停止
              </Button>
              <Button className="flex-1" data-testid={`button-open-${pkg.id}`}>
                開く
              </Button>
            </>
          ) : pkg.status === 'inactive' ? (
            <Button className="w-full" data-testid={`button-activate-${pkg.id}`}>
              <Play className="h-4 w-4 mr-2" />
              アクティベート
            </Button>
          ) : pkg.status === 'installing' ? (
            <Button disabled className="w-full">
              <Download className="h-4 w-4 mr-2 animate-pulse" />
              インストール中...
            </Button>
          ) : (
            <Button variant="outline" className="w-full" data-testid={`button-reinstall-${pkg.id}`}>
              <Download className="h-4 w-4 mr-2" />
              再インストール
            </Button>
          )}
        </div>

        <Alert>
          <Shield className="h-4 w-4" />
          <AlertDescription>
            このパッケージはLibral Coreの安全な実行環境で動作します。
            プライバシーとセキュリティが完全に保護されています。
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">パッケージ & サービス</h1>
          <p className="text-muted-foreground">
            利用可能なLibral Coreパッケージとサービス一覧
          </p>
        </div>
        <Button data-testid="button-package-store">
          <Package className="h-4 w-4 mr-2" />
          ストア
        </Button>
      </div>

      <Tabs defaultValue="packages" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="packages">パッケージ</TabsTrigger>
          <TabsTrigger value="services">サービス</TabsTrigger>
          <TabsTrigger value="settings">設定</TabsTrigger>
        </TabsList>

        <TabsContent value="packages" className="space-y-4">
          {/* カテゴリ選択 */}
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(category.id)}
                className="flex items-center space-x-2 whitespace-nowrap"
                data-testid={`button-category-${category.id}`}
              >
                {category.icon}
                <span>{category.name}</span>
              </Button>
            ))}
          </div>

          {/* パッケージ一覧 */}
          <div className="grid gap-4">
            {filteredPackages.map((pkg) => (
              <Card key={pkg.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1">
                      {pkg.icon}
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium truncate">{pkg.name}</h3>
                        <p className="text-sm text-muted-foreground truncate">
                          {pkg.description}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge className={getStatusColor(pkg.status)} data-testid={`status-${pkg.id}`}>
                            {pkg.status}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatPrice(pkg.price, pkg.currency)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedPackage(selectedPackage?.id === pkg.id ? null : pkg)}
                      data-testid={`button-info-${pkg.id}`}
                    >
                      <ChevronRight className={`h-4 w-4 transition-transform ${selectedPackage?.id === pkg.id ? 'rotate-90' : ''}`} />
                    </Button>
                  </div>
                </CardContent>
                {selectedPackage?.id === pkg.id && renderPackageDetail(pkg)}
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Libral Core サービス</CardTitle>
              <CardDescription>
                プラットフォーム全体で利用できるコアサービス
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Shield className="h-5 w-5 text-green-500" />
                    <div>
                      <h4 className="font-medium">Aegis-PGP暗号化</h4>
                      <p className="text-sm text-muted-foreground">エンタープライズ級暗号化サービス</p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800">稼働中</Badge>
                </div>

                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <MessageSquare className="h-5 w-5 text-blue-500" />
                    <div>
                      <h4 className="font-medium">Telegram統合</h4>
                      <p className="text-sm text-muted-foreground">個人ログサーバーとボット機能</p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800">稼働中</Badge>
                </div>

                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Zap className="h-5 w-5 text-yellow-500" />
                    <div>
                      <h4 className="font-medium">リアルタイム処理</h4>
                      <p className="text-sm text-muted-foreground">イベント処理とWebSocket通信</p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800">稼働中</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>パッケージ設定</CardTitle>
              <CardDescription>
                パッケージの自動更新とセキュリティ設定
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <Settings className="h-4 w-4" />
                <AlertDescription>
                  <strong>管理者機能:</strong> パッケージの設定とトラブルシューティング機能は
                  開発ダッシュボードからアクセスできます。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
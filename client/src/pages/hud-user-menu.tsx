import { useState } from "react";
import { HudCard, HudButton, HexPanel, MetricPanel } from "@/components/ui/hud-elements";
import { 
  Package, 
  Star, 
  Download, 
  Play,
  Pause,
  Settings,
  Shield,
  Bot,
  Image,
  Video,
  Music,
  Palette,
  Users,
  ChevronRight,
  Zap
} from "lucide-react";

interface UserPackage {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: 'active' | 'inactive' | 'installing';
  price: number;
  userCount: number;
}

const packages: UserPackage[] = [
  {
    id: 'libral-ai',
    name: 'Libral AI',
    description: 'AI アシスタント',
    icon: <Bot className="w-5 h-5" />,
    status: 'active',
    price: 0,
    userCount: 15420
  },
  {
    id: 'stamp-creator',
    name: 'TxT WORLD',
    description: 'スタンプ作成',
    icon: <Image className="w-5 h-5" />,
    status: 'active',
    price: 150,
    userCount: 8930
  },
  {
    id: 'live-video',
    name: 'LIVE VIDEO',
    description: 'ビデオチャット',
    icon: <Video className="w-5 h-5" />,
    status: 'installing',
    price: 300,
    userCount: 5680
  },
  {
    id: 'music-studio',
    name: 'Music Studio',
    description: 'AI作曲スタジオ',
    icon: <Music className="w-5 h-5" />,
    status: 'inactive',
    price: 250,
    userCount: 3240
  }
];

export default function HudUserMenu() {
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#00ff41';
      case 'inactive': return '#ffa500';
      case 'installing': return '#00bcd4';
      default: return '#666';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Play className="w-3 h-3" />;
      case 'inactive': return <Pause className="w-3 h-3" />;
      case 'installing': return <Download className="w-3 h-3 animate-pulse" />;
      default: return <Package className="w-3 h-3" />;
    }
  };

  const formatPrice = (price: number) => {
    return price === 0 ? '無料' : `${price} ⭐`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-gray-900 text-white overflow-hidden">
      <div className="p-4 space-y-4 max-w-md mx-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold text-cyan-400 font-mono">PACKAGE CENTER</h1>
            <p className="text-xs text-gray-400">利用可能なサービス</p>
          </div>
          <HudButton variant="primary" size="sm" data-testid="button-store">
            <Package className="w-4 h-4" />
          </HudButton>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <HudCard variant="primary">
            <MetricPanel
              title="ACTIVE"
              value="2"
              color="#00ff41"
              icon={<Play className="w-4 h-4" />}
            />
          </HudCard>
          <HudCard variant="secondary">
            <MetricPanel
              title="TOTAL"
              value="4"
              color="#00bcd4"
              icon={<Package className="w-4 h-4" />}
            />
          </HudCard>
          <HudCard variant="info">
            <MetricPanel
              title="STARS"
              value="850"
              color="#ffa500"
              icon={<Star className="w-4 h-4" />}
            />
          </HudCard>
        </div>

        {/* Package Grid */}
        <div className="space-y-3">
          {packages.map((pkg) => (
            <div key={pkg.id}>
              <HudCard 
                variant={pkg.status === 'active' ? 'primary' : 'secondary'}
                className="cursor-pointer hover:scale-[1.02] transition-transform"
                onClick={() => setSelectedPackage(selectedPackage === pkg.id ? null : pkg.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1">
                    <div className="p-2 rounded bg-white/10">
                      {pkg.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-sm truncate">{pkg.name}</h3>
                      <p className="text-xs text-gray-400 truncate">{pkg.description}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <div 
                          className="flex items-center space-x-1 text-xs"
                          style={{ color: getStatusColor(pkg.status) }}
                        >
                          {getStatusIcon(pkg.status)}
                          <span>{pkg.status}</span>
                        </div>
                        <span className="text-xs text-yellow-400">{formatPrice(pkg.price)}</span>
                      </div>
                    </div>
                  </div>
                  <ChevronRight 
                    className={`w-4 h-4 text-cyan-400 transition-transform ${
                      selectedPackage === pkg.id ? 'rotate-90' : ''
                    }`} 
                  />
                </div>
              </HudCard>

              {/* Package Detail */}
              {selectedPackage === pkg.id && (
                <HudCard variant="info" className="mt-2">
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-gray-400">価格:</span>
                        <div className="text-yellow-400 font-mono">{formatPrice(pkg.price)}</div>
                      </div>
                      <div>
                        <span className="text-gray-400">利用者:</span>
                        <div className="text-cyan-400 font-mono">{pkg.userCount.toLocaleString()}</div>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      {pkg.status === 'active' ? (
                        <>
                          <HudButton 
                            variant="primary" 
                            size="sm" 
                            className="flex-1"
                            data-testid={`button-open-${pkg.id}`}
                          >
                            開く
                          </HudButton>
                          <HudButton 
                            variant="danger" 
                            size="sm"
                            data-testid={`button-stop-${pkg.id}`}
                          >
                            <Pause className="w-3 h-3" />
                          </HudButton>
                        </>
                      ) : pkg.status === 'inactive' ? (
                        <HudButton 
                          variant="primary" 
                          size="sm" 
                          className="w-full"
                          data-testid={`button-start-${pkg.id}`}
                        >
                          <Play className="w-3 h-3 mr-2" />
                          開始
                        </HudButton>
                      ) : (
                        <HudButton 
                          variant="secondary" 
                          size="sm" 
                          className="w-full" 
                          disabled
                        >
                          <Download className="w-3 h-3 mr-2 animate-pulse" />
                          インストール中...
                        </HudButton>
                      )}
                    </div>
                  </div>
                </HudCard>
              )}
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3 mt-6">
          <HudButton variant="primary" data-testid="button-settings-user">
            <Settings className="w-4 h-4 mr-2" />
            設定
          </HudButton>
          <HudButton variant="secondary" data-testid="button-help">
            <Shield className="w-4 h-4 mr-2" />
            ヘルプ
          </HudButton>
        </div>

        {/* Security Info */}
        <HudCard variant="primary" className="mt-4">
          <div className="text-center space-y-2">
            <Shield className="w-8 h-8 text-cyan-400 mx-auto" />
            <h3 className="text-sm font-bold text-cyan-400">完全プライバシー保護</h3>
            <p className="text-xs text-gray-400">
              全データはTelegram個人サーバーに保存<br/>
              Libral Coreが完全に制御
            </p>
          </div>
        </HudCard>

      </div>
    </div>
  );
}
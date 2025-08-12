import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { apiRequest } from "@/lib/queryClient";
import { 
  Sparkles, 
  Type, 
  Palette, 
  Image, 
  Zap, 
  Play, 
  Download,
  Star,
  Wand2,
  ArrowLeft
} from "lucide-react";
import { Link } from "wouter";

interface Asset {
  id: string;
  name: string;
  type: string;
  category: string;
  price: number;
  previewUrl?: string;
}

interface StampPreview {
  id: string;
  text: string;
  fontId: string;
  characterId?: string;
  backgroundId?: string;
  effectId?: string;
  animationId?: string;
  emojis: string[];
  format: string;
  previewUrl?: string;
}

export default function StampCreator() {
  const [currentStep, setCurrentStep] = useState(0);
  const [stampData, setStampData] = useState({
    text: "",
    fontId: "",
    characterId: "",
    backgroundId: "",
    effectId: "", 
    animationId: "",
    emojis: [] as string[],
    format: "TGS"
  });
  const [preview, setPreview] = useState<StampPreview | null>(null);
  const [suggestedEmojis, setSuggestedEmojis] = useState<string[]>([]);

  const queryClient = useQueryClient();

  // Fetch available assets
  const { data: fonts } = useQuery<Asset[]>({
    queryKey: ['/api/assets', 'font'],
  });

  const { data: characters } = useQuery<Asset[]>({
    queryKey: ['/api/assets', 'character'],
  });

  const { data: backgrounds } = useQuery<Asset[]>({
    queryKey: ['/api/assets', 'background'],
  });

  const { data: effects } = useQuery<Asset[]>({
    queryKey: ['/api/assets', 'effect'],
  });

  const { data: animations } = useQuery<Asset[]>({
    queryKey: ['/api/assets', 'animation'],
  });

  // AI suggestions for emojis
  const suggestEmojisMutation = useMutation({
    mutationFn: async (data: { text: string; characterId?: string }) => {
      const response = await apiRequest('/api/ai/suggest-emojis', {
        method: 'POST',
        body: JSON.stringify(data)
      });
      return response.json();
    },
    onSuccess: (data) => {
      setSuggestedEmojis(data.emojis || []);
    }
  });

  // Generate preview
  const generatePreviewMutation = useMutation({
    mutationFn: async (data: typeof stampData) => {
      const response = await apiRequest('/api/stamps/preview', {
        method: 'POST',
        body: JSON.stringify(data)
      });
      return response.json();
    },
    onSuccess: (data) => {
      setPreview(data);
    }
  });

  // Create final stamp
  const createStampMutation = useMutation({
    mutationFn: async (data: typeof stampData) => {
      console.log("Sending stamp creation request:", data);
      const response = await apiRequest('/api/stamps/create', {
        method: 'POST',
        body: JSON.stringify(data)
      });
      const result = await response.json();
      console.log("Stamp creation response:", result);
      return result;
    },
    onSuccess: (data) => {
      console.log("Stamp created successfully:", data);
      queryClient.invalidateQueries({ queryKey: ['/api/stamps'] });
      // Show success message or redirect
      alert(`スタンプが正常に作成されました！ID: ${data.id}`);
    },
    onError: (error) => {
      console.error("Stamp creation failed:", error);
      alert("スタンプの作成に失敗しました。もう一度お試しください。");
    }
  });

  const steps = [
    {
      title: "魔法の言葉を入力",
      subtitle: "あなたのスタンプに込めたいメッセージを教えてください",
      icon: Type
    },
    {
      title: "魔法のアイテムを選択",
      subtitle: "フォント、キャラクター、背景、エフェクトを組み合わせましょう",
      icon: Palette
    },
    {
      title: "魔法の完成確認",
      subtitle: "作成したスタンプをプレビューして仕上げましょう",
      icon: Sparkles
    }
  ];

  const handleTextChange = (text: string) => {
    setStampData({ ...stampData, text });
    
    if (text.length > 2) {
      suggestEmojisMutation.mutate({ text, characterId: stampData.characterId });
    }
  };

  const handleAssetSelect = (type: string, assetId: string) => {
    setStampData({ ...stampData, [type]: assetId });
  };

  const handleEmojiToggle = (emoji: string) => {
    const newEmojis = stampData.emojis.includes(emoji)
      ? stampData.emojis.filter(e => e !== emoji)
      : [...stampData.emojis, emoji];
    setStampData({ ...stampData, emojis: newEmojis });
  };

  const generatePreview = () => {
    if (stampData.text && stampData.fontId) {
      generatePreviewMutation.mutate(stampData);
    }
  };

  const createStamp = () => {
    console.log("Creating stamp with data:", stampData);
    createStampMutation.mutate(stampData);
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return stampData.text.length > 0;
      case 1:
        return stampData.fontId.length > 0;
      case 2:
        return preview !== null;
      default:
        return false;
    }
  };

  useEffect(() => {
    if (currentStep === 2) {
      generatePreview();
    }
  }, [currentStep]);

  const renderAssetGrid = (assets: Asset[], selectedId: string, type: string) => (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {assets?.map((asset) => (
        <Card 
          key={asset.id}
          className={`cursor-pointer transition-all hover:scale-105 ${
            selectedId === asset.id 
              ? 'border-primary bg-primary/10' 
              : 'border-dark-700 bg-dark-800 hover:border-primary/50'
          }`}
          onClick={() => handleAssetSelect(type, asset.id)}
        >
          <CardContent className="p-4">
            {asset.previewUrl && (
              <div className="aspect-square bg-dark-700 rounded-md mb-2 flex items-center justify-center">
                <img 
                  src={asset.previewUrl} 
                  alt={asset.name}
                  className="max-w-full max-h-full object-contain"
                />
              </div>
            )}
            <p className="text-sm font-medium text-dark-50 text-center">{asset.name}</p>
            {asset.category === 'premium' && (
              <div className="flex items-center justify-center mt-2">
                <Badge className="bg-warning/10 text-warning">
                  <Star className="w-3 h-3 mr-1" />
                  {asset.price}円
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-dark-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center mb-6">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm" className="text-dark-400 hover:text-dark-50">
              <ArrowLeft className="w-4 h-4 mr-2" />
              ダッシュボードに戻る
            </Button>
          </Link>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="flex items-center">
                <div className={`
                  w-12 h-12 rounded-full flex items-center justify-center border-2 
                  ${currentStep >= index 
                    ? 'border-primary bg-primary/10 text-primary' 
                    : 'border-dark-600 text-dark-400'
                  }
                `}>
                  <Icon className="w-5 h-5" />
                </div>
                {index < steps.length - 1 && (
                  <div className={`
                    w-16 h-0.5 mx-4 
                    ${currentStep > index ? 'bg-primary' : 'bg-dark-600'}
                  `} />
                )}
              </div>
            );
          })}
        </div>

        {/* Current Step Title */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-dark-50 mb-2">
            {steps[currentStep].title}
          </h1>
          <p className="text-dark-400">
            {steps[currentStep].subtitle}
          </p>
        </div>

        {/* Step Content */}
        <Card className="bg-dark-800 border-dark-700 mb-6">
          <CardContent className="p-6">
            {/* Step 0: Text Input */}
            {currentStep === 0 && (
              <div className="space-y-6">
                <div className="relative">
                  <Textarea
                    placeholder="例: おつかれさま！"
                    value={stampData.text}
                    onChange={(e) => handleTextChange(e.target.value)}
                    className="bg-dark-700 border-dark-600 text-dark-50 placeholder-dark-400 text-lg p-4 min-h-[120px] resize-none"
                    maxLength={50}
                  />
                  <div className="absolute bottom-2 right-2 text-xs text-dark-400">
                    {stampData.text.length}/50
                  </div>
                  
                  {/* Sparkling Animation */}
                  {stampData.text.length > 0 && (
                    <div className="absolute top-2 right-2 animate-pulse">
                      <Sparkles className="w-5 h-5 text-primary" />
                    </div>
                  )}
                </div>

                {/* AI Assistant Popup */}
                {suggestedEmojis.length > 0 && (
                  <Card className="bg-primary/5 border-primary/20">
                    <CardContent className="p-4">
                      <div className="flex items-center mb-3">
                        <Wand2 className="w-4 h-4 text-primary mr-2" />
                        <span className="text-sm font-medium text-primary">
                          この言葉にピッタリの絵文字を見つけました！
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {suggestedEmojis.map((emoji) => (
                          <Button
                            key={emoji}
                            variant={stampData.emojis.includes(emoji) ? "default" : "outline"}
                            size="sm"
                            onClick={() => handleEmojiToggle(emoji)}
                            className="text-lg"
                          >
                            {emoji}
                          </Button>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {/* Step 1: Asset Selection */}
            {currentStep === 1 && (
              <div className="space-y-8">
                {/* Font Selection */}
                <div>
                  <h3 className="text-lg font-semibold text-dark-50 mb-4 flex items-center">
                    <Type className="w-5 h-5 mr-2 text-primary" />
                    フォント選択
                  </h3>
                  {renderAssetGrid(fonts || [], stampData.fontId, 'fontId')}
                </div>

                {/* Character Selection */}
                <div>
                  <h3 className="text-lg font-semibold text-dark-50 mb-4 flex items-center">
                    <Image className="w-5 h-5 mr-2 text-secondary" />
                    キャラクター選択
                  </h3>
                  {renderAssetGrid(characters || [], stampData.characterId, 'characterId')}
                </div>

                {/* Background Selection */}
                <div>
                  <h3 className="text-lg font-semibold text-dark-50 mb-4 flex items-center">
                    <Palette className="w-5 h-5 mr-2 text-warning" />
                    背景選択
                  </h3>
                  {renderAssetGrid(backgrounds || [], stampData.backgroundId, 'backgroundId')}
                </div>

                {/* Effect Selection */}
                <div>
                  <h3 className="text-lg font-semibold text-dark-50 mb-4 flex items-center">
                    <Zap className="w-5 h-5 mr-2 text-error" />
                    エフェクト選択
                  </h3>
                  {renderAssetGrid(effects || [], stampData.effectId, 'effectId')}
                </div>

                {/* Animation Selection */}
                <div>
                  <h3 className="text-lg font-semibold text-dark-50 mb-4 flex items-center">
                    <Play className="w-5 h-5 mr-2 text-success" />
                    アニメーション選択
                  </h3>
                  {renderAssetGrid(animations || [], stampData.animationId, 'animationId')}
                </div>
              </div>
            )}

            {/* Step 2: Preview and Finalize */}
            {currentStep === 2 && (
              <div className="space-y-6">
                {/* Preview Area */}
                <div className="flex justify-center">
                  <div className="relative">
                    <div className="w-64 h-64 bg-dark-700 rounded-xl border-2 border-primary/30 flex items-center justify-center">
                      {generatePreviewMutation.isPending ? (
                        <div className="text-center">
                          <Sparkles className="w-12 h-12 text-primary mx-auto mb-2 animate-spin" />
                          <p className="text-dark-400">魔法を調合中...</p>
                        </div>
                      ) : preview ? (
                        <img 
                          src={preview.previewUrl} 
                          alt="Stamp preview"
                          className="max-w-full max-h-full object-contain rounded-lg"
                        />
                      ) : (
                        <div className="text-center">
                          <Image className="w-12 h-12 text-dark-500 mx-auto mb-2" />
                          <p className="text-dark-500">プレビューを生成中</p>
                        </div>
                      )}
                    </div>
                    
                    {/* Magic Frame Effect */}
                    <div className="absolute -inset-2 bg-gradient-to-r from-primary/20 via-secondary/20 to-warning/20 rounded-xl blur-sm opacity-75 animate-pulse"></div>
                  </div>
                </div>

                {/* Selected Emojis */}
                {stampData.emojis.length > 0 && (
                  <Card className="bg-dark-700 border-dark-600">
                    <CardContent className="p-4">
                      <h4 className="text-sm font-medium text-dark-50 mb-3">選択された絵文字:</h4>
                      <div className="flex flex-wrap gap-2">
                        {stampData.emojis.map((emoji, index) => (
                          <Badge key={index} variant="outline" className="text-lg px-3 py-1">
                            {emoji}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Stamp Details */}
                <Card className="bg-dark-700 border-dark-600">
                  <CardContent className="p-4">
                    <h4 className="text-sm font-medium text-dark-50 mb-3">スタンプの詳細:</h4>
                    <div className="space-y-2 text-sm text-dark-400">
                      <div>テキスト: <span className="text-dark-50">"{stampData.text}"</span></div>
                      <div>フォーマット: <span className="text-dark-50">{stampData.format}</span></div>
                      <div>絵文字: <span className="text-dark-50">{stampData.emojis.join(' ') || 'なし'}</span></div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
            className="border-dark-600 text-dark-50 hover:bg-dark-700"
          >
            戻る
          </Button>

          {currentStep < steps.length - 1 ? (
            <Button
              onClick={() => setCurrentStep(currentStep + 1)}
              disabled={!canProceed()}
              className="bg-primary hover:bg-primary/90"
            >
              次へ
              <Sparkles className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={createStamp}
              disabled={!preview || createStampMutation.isPending}
              className="bg-success hover:bg-success/90"
            >
              {createStampMutation.isPending ? (
                <>
                  <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                  作成中...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  スタンプを作成
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
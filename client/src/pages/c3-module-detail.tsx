import { useLocation, useRoute } from "wouter";
import { ArrowLeft, Database, Brain, Lock, Zap, Globe, FileText, Grid3x3 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

export default function C3ModuleDetail() {
  const [, setLocation] = useLocation();
  const [, params] = useRoute("/c3/apps/:moduleId");
  const moduleId = params?.moduleId || "";

  const moduleConfigs: Record<string, {
    name: string;
    description: string;
    icon: any;
    apiEndpoint?: string;
    features: string[];
    actions: { label: string; path: string; testId: string }[];
  }> = {
    "kb-system": {
      name: "Knowledge Base System",
      description: "多言語知識管理システム - 80+言語対応、GPG暗号化統合",
      icon: Database,
      apiEndpoint: "/api/kb/stats",
      features: [
        "80+言語サポート",
        "GPG暗号化統合",
        "カテゴリ管理",
        "多言語検索",
        "バージョン管理"
      ],
      actions: [
        { label: "KB Editor を開く", path: "/kb-editor", testId: "button-open-kb-editor" },
        { label: "統計を表示", path: "/c3/apps/kb-system/stats", testId: "button-view-stats" }
      ]
    },
    "ai-bridge": {
      name: "AI Bridge Layer",
      description: "AI統合ブリッジ & 自動フォールバックシステム (Gemini→GPT5-mini→OSS)",
      icon: Brain,
      features: [
        "自動フォールバック",
        "非同期キュー処理",
        "リトライ機能",
        "優先度ベース処理",
        "エラーハンドリング"
      ],
      actions: [
        { label: "リクエスト送信", path: "/c3/apps/ai-bridge/request", testId: "button-send-request" }
      ]
    },
    "evaluator": {
      name: "Evaluator 2.0",
      description: "AI品質評価システム - 90点閾値、自動再生成機能",
      icon: Zap,
      apiEndpoint: "/api/evaluator/stats",
      features: [
        "多基準評価 (正確性、一貫性、関連性、倫理性、完全性)",
        "90点閾値判定",
        "自動再生成",
        "評価履歴",
        "KB統合"
      ],
      actions: [
        { label: "評価を実行", path: "/c3/apps/evaluator/evaluate", testId: "button-evaluate" },
        { label: "履歴を表示", path: "/c3/apps/evaluator/history", testId: "button-view-history" }
      ]
    },
    "oss-manager": {
      name: "OSS Manager",
      description: "オープンソースモデル管理 - LLaMA3, Mistral, Falcon, Whisper, CLIP",
      icon: Grid3x3,
      apiEndpoint: "/api/oss/models",
      features: [
        "動的モデルロード/アンロード",
        "メモリ効率化",
        "カテゴリベース管理",
        "優先度制御",
        "自動アンロード"
      ],
      actions: [
        { label: "モデル一覧", path: "/c3/apps/oss-manager/models", testId: "button-view-models" },
        { label: "推論を実行", path: "/c3/apps/oss-manager/infer", testId: "button-infer" }
      ]
    },
    "ai-router": {
      name: "AI Router",
      description: "知的AIルーティングシステム - タスクベース最適化",
      icon: Globe,
      apiEndpoint: "/api/ai-router/stats",
      features: [
        "タスクタイプ認識",
        "自動ルーティング",
        "ロードバランシング",
        "パフォーマンス監視",
        "評価統合"
      ],
      actions: [
        { label: "ルーティング実行", path: "/c3/apps/ai-router/route", testId: "button-route" },
        { label: "統計を表示", path: "/c3/apps/ai-router/stats", testId: "button-router-stats" }
      ]
    },
    "embedding": {
      name: "Embedding Layer",
      description: "ベクトル埋め込み & 検索基盤 - FAISS + ChromaDB ready",
      icon: FileText,
      apiEndpoint: "/api/embedding/stats",
      features: [
        "384次元ベクトル生成",
        "コサイン類似度検索",
        "言語別埋め込み",
        "カテゴリフィルタ",
        "FAISS/ChromaDB統合準備"
      ],
      actions: [
        { label: "埋め込み生成", path: "/c3/apps/embedding/generate", testId: "button-generate" },
        { label: "類似検索", path: "/c3/apps/embedding/search", testId: "button-search" }
      ]
    },
    "aegis-pgp": {
      name: "Aegis-PGP",
      description: "企業級GPG暗号化システム - RSA-4096, ED25519, ECDSA-P256",
      icon: Lock,
      features: [
        "鍵ペア生成 (RSA-4096, ED25519, ECDSA-P256)",
        "Context-Lock署名",
        "暗号化/復号化",
        "WKD統合",
        "Compatibility/Backup/Modern Strong ポリシー"
      ],
      actions: [
        { label: "鍵を生成", path: "/c3/apps/aegis-pgp/generate", testId: "button-generate-key" },
        { label: "暗号化", path: "/c3/apps/aegis-pgp/encrypt", testId: "button-encrypt" }
      ]
    }
  };

  const config = moduleConfigs[moduleId];
  const { data: stats } = useQuery({ 
    queryKey: [config?.apiEndpoint || ""], 
    enabled: !!config?.apiEndpoint 
  });

  if (!config) {
    return (
      <div className="min-h-screen bg-[#080A0F] flex items-center justify-center">
        <div className="text-[#FF3A5B] text-xl">MODULE NOT FOUND</div>
      </div>
    );
  }

  const Icon = config.icon;

  return (
    <div className="relative min-h-screen bg-[#080A0F] overflow-hidden font-mono">
      <div className="absolute inset-0 opacity-10 pointer-events-none" 
           style={{ 
             backgroundImage: `
               linear-gradient(#FFEB00 1px, transparent 1px),
               linear-gradient(90deg, #FFEB00 1px, transparent 1px)
             `,
             backgroundSize: '20px 20px'
           }} 
      />

      <div className="relative z-10 min-h-screen flex flex-col">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#FFEB00] to-transparent" />
        
        <header className="relative px-8 py-6 border-b border-[#FFEB00]/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setLocation("/c3/apps")}
                className="w-10 h-10 border border-[#FFEB00]/50 hover:border-[#FFEB00] hover:bg-[#FFEB00]/10 flex items-center justify-center transition-all"
                data-testid="button-back"
              >
                <ArrowLeft className="text-[#FFEB00]" />
              </button>
              <div className="w-12 h-12 border-2 border-[#FFEB00] flex items-center justify-center"
                   style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' }}>
                <Icon className="text-[#FFEB00] w-6 h-6" />
              </div>
              <div>
                <h1 className="text-[#FFEB00] text-xl font-bold tracking-[0.2em]">{config.name}</h1>
                <p className="text-[#FFEB00]/60 text-xs tracking-[0.3em]">MODULE DETAILS</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#FFEB00] animate-pulse" />
              <span className="text-[#FFEB00] text-sm">ONLINE</span>
            </div>
          </div>
        </header>

        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8 border border-[#FFEB00]/30 p-6"
                 style={{ clipPath: 'polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px)' }}>
              <h2 className="text-white text-lg mb-2">{config.description}</h2>
            </div>

            <div className="grid lg:grid-cols-2 gap-8 mb-8">
              <div>
                <div className="inline-block mb-4 px-4 py-1 border border-[#FFEB00]/50">
                  <h3 className="text-[#FFEB00] text-xs tracking-[0.4em]">FEATURES</h3>
                </div>
                <div className="space-y-3">
                  {config.features.map((feature, index) => (
                    <div key={index} className="flex items-start gap-3 text-white/80">
                      <div className="mt-1 w-2 h-2 bg-[#FFEB00]" style={{ clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)' }} />
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div className="inline-block mb-4 px-4 py-1 border border-[#FFEB00]/50">
                  <h3 className="text-[#FFEB00] text-xs tracking-[0.4em]">ACTIONS</h3>
                </div>
                <div className="space-y-3">
                  {config.actions.map((action, index) => (
                    <button
                      key={index}
                      onClick={() => setLocation(action.path)}
                      className="w-full group px-4 py-3 border border-[#FFEB00]/50 hover:border-[#FFEB00] hover:bg-[#FFEB00]/10 text-left transition-all flex items-center justify-between"
                      data-testid={action.testId}
                    >
                      <span className="text-[#FFEB00]">{action.label}</span>
                      <span className="text-[#FFEB00] group-hover:translate-x-2 transition-transform">▶</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {stats && (
              <div className="border border-[#FFEB00]/30 p-6"
                   style={{ clipPath: 'polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px)' }}>
                <div className="flex items-center gap-2 mb-4">
                  <div className="text-[#FFEB00] text-sm tracking-[0.3em]">STATISTICS</div>
                  <div className="flex-1 h-px bg-[#FFEB00]/30" />
                </div>
                <pre className="text-[#FFEB00] text-sm overflow-auto" data-testid="stats-display">
                  {JSON.stringify(stats, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </main>

        <footer className="relative px-8 py-4 border-t border-[#FFEB00]/30">
          <div className="flex items-center justify-between text-xs text-[#FFEB00]/60">
            <div>MODULE: {moduleId.toUpperCase()} // LIBRAL CORE</div>
            <div>{new Date().toLocaleTimeString()}</div>
          </div>
        </footer>
        
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#FFEB00] to-transparent" />
      </div>
    </div>
  );
}

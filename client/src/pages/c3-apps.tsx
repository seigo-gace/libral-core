import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { ArrowLeft, Grid3x3, Database, Brain, Lock, Zap, Globe, FileText } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

interface ModuleInfo {
  id: string;
  name: string;
  description: string;
  status: "online" | "offline" | "maintenance";
  icon: string;
  category: string;
}

export default function C3Apps() {
  const [, setLocation] = useLocation();
  const [selectedModule, setSelectedModule] = useState<string | null>(null);

  const { data: kbStats } = useQuery({ queryKey: ["/api/kb/stats"] });
  const { data: evaluatorStats } = useQuery({ queryKey: ["/api/evaluator/stats"] });
  const { data: ossModels } = useQuery({ queryKey: ["/api/oss/models"] });
  const { data: aiRouterStats } = useQuery({ queryKey: ["/api/ai-router/stats"] });
  const { data: embeddingStats } = useQuery({ queryKey: ["/api/embedding/stats"] });

  const modules: ModuleInfo[] = [
    {
      id: "kb-system",
      name: "Knowledge Base",
      description: "多言語知識管理システム (80+ languages)",
      status: kbStats ? "online" : "offline",
      icon: "database",
      category: "Core"
    },
    {
      id: "ai-bridge",
      name: "AI Bridge Layer",
      description: "AI統合ブリッジ & フォールバックシステム",
      status: "online",
      icon: "brain",
      category: "AI"
    },
    {
      id: "evaluator",
      name: "Evaluator 2.0",
      description: "AI品質評価システム (90点閾値)",
      status: evaluatorStats ? "online" : "offline",
      icon: "zap",
      category: "AI"
    },
    {
      id: "oss-manager",
      name: "OSS Manager",
      description: "オープンソースモデル管理 (LLaMA3, Mistral)",
      status: ossModels ? "online" : "offline",
      icon: "grid",
      category: "AI"
    },
    {
      id: "ai-router",
      name: "AI Router",
      description: "知的AIルーティングシステム",
      status: aiRouterStats ? "online" : "offline",
      icon: "globe",
      category: "AI"
    },
    {
      id: "embedding",
      name: "Embedding Layer",
      description: "ベクトル埋め込み & 検索基盤",
      status: embeddingStats ? "online" : "offline",
      icon: "file-text",
      category: "AI"
    },
    {
      id: "aegis-pgp",
      name: "Aegis-PGP",
      description: "企業級暗号化システム (GPG/PGP)",
      status: "online",
      icon: "lock",
      category: "Security"
    }
  ];

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case "database": return <Database className="w-6 h-6" />;
      case "brain": return <Brain className="w-6 h-6" />;
      case "zap": return <Zap className="w-6 h-6" />;
      case "grid": return <Grid3x3 className="w-6 h-6" />;
      case "globe": return <Globe className="w-6 h-6" />;
      case "file-text": return <FileText className="w-6 h-6" />;
      case "lock": return <Lock className="w-6 h-6" />;
      default: return <Grid3x3 className="w-6 h-6" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online": return "#00FFD1";
      case "offline": return "#FF3A5B";
      case "maintenance": return "#FFC400";
      default: return "#00FFD1";
    }
  };

  return (
    <div className="relative min-h-screen bg-[#080A0F] overflow-hidden font-mono">
      <div className="absolute inset-0 opacity-10 pointer-events-none" 
           style={{ 
             backgroundImage: `
               linear-gradient(#00FFD1 1px, transparent 1px),
               linear-gradient(90deg, #00FFD1 1px, transparent 1px)
             `,
             backgroundSize: '20px 20px'
           }} 
      />

      <div className="relative z-10 min-h-screen flex flex-col">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#00FFD1] to-transparent" />
        
        <header className="relative px-8 py-6 border-b border-[#00FFD1]/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setLocation("/c3")}
                className="w-10 h-10 border border-[#00FFD1]/50 hover:border-[#00FFD1] hover:bg-[#00FFD1]/10 flex items-center justify-center transition-all"
                data-testid="button-back"
              >
                <ArrowLeft className="text-[#00FFD1]" />
              </button>
              <div>
                <h1 className="text-[#00FFD1] text-xl font-bold tracking-[0.2em]">APPS & FEATURES</h1>
                <p className="text-[#00FFD1]/60 text-xs tracking-[0.3em]">MODULE MANAGEMENT CONSOLE</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-[#00FFD1]/60 text-sm tracking-wider">[D008]</div>
            </div>
          </div>
        </header>

        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <div className="inline-block mb-4 px-4 py-1 border border-[#00FFD1]/50">
                <h2 className="text-[#00FFD1] text-xs tracking-[0.4em]">CONNECTED MODULES</h2>
              </div>
              <p className="text-white/60 text-sm">選択して詳細を表示・操作</p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {modules.map((module) => (
                <button
                  key={module.id}
                  onClick={() => setLocation(`/c3/apps/${module.id}`)}
                  className="group text-left p-6 border-2 border-[#00FFD1]/30 hover:border-[#00FFD1] transition-all duration-300 hover:shadow-[0_0_20px_rgba(0,255,209,0.2)]"
                  style={{ clipPath: 'polygon(0 0, calc(100% - 15px) 0, 100% 15px, 100% 100%, 15px 100%, 0 calc(100% - 15px))' }}
                  data-testid={`card-module-${module.id}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 border border-[#00FFD1] flex items-center justify-center group-hover:bg-[#00FFD1] group-hover:text-[#080A0F] transition-all"
                         style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' }}>
                      {getIcon(module.icon)}
                    </div>
                    <div 
                      className="w-3 h-3 rounded-full animate-pulse"
                      style={{ backgroundColor: getStatusColor(module.status) }}
                    />
                  </div>

                  <h3 className="text-[#00FFD1] text-lg font-bold mb-2 tracking-wide">{module.name}</h3>
                  <p className="text-white/60 text-sm mb-4">{module.description}</p>

                  <div className="flex items-center justify-between">
                    <span className="text-[#00FFD1]/60 text-xs tracking-wider">{module.category}</span>
                    <span className="text-[#00FFD1] text-sm uppercase">{module.status}</span>
                  </div>

                  <div className="absolute bottom-0 left-0 right-0 h-px bg-[#00FFD1]/20 group-hover:bg-[#00FFD1] transition-colors" />
                </button>
              ))}
            </div>

            <div className="mt-12 border border-[#00FFD1]/30 p-6"
                 style={{ clipPath: 'polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px)' }}>
              <div className="flex items-center gap-2 mb-4">
                <div className="text-[#00FFD1] text-sm tracking-[0.3em]">SYSTEM OVERVIEW</div>
                <div className="flex-1 h-px bg-[#00FFD1]/30" />
              </div>
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl text-[#00FFD1] font-bold mb-1">{modules.filter(m => m.status === "online").length}</div>
                  <div className="text-white/60 text-xs">ONLINE</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl text-[#FF3A5B] font-bold mb-1">{modules.filter(m => m.status === "offline").length}</div>
                  <div className="text-white/60 text-xs">OFFLINE</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl text-[#FFC400] font-bold mb-1">{modules.filter(m => m.status === "maintenance").length}</div>
                  <div className="text-white/60 text-xs">MAINTENANCE</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl text-[#00FFD1] font-bold mb-1">{modules.length}</div>
                  <div className="text-white/60 text-xs">TOTAL</div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <footer className="relative px-8 py-4 border-t border-[#00FFD1]/30">
          <div className="flex items-center justify-between text-xs text-[#00FFD1]/60">
            <div>MODULE REGISTRY // LIBRAL CORE</div>
            <div>{new Date().toLocaleTimeString()}</div>
          </div>
        </footer>
        
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#00FFD1] to-transparent" />
      </div>
    </div>
  );
}

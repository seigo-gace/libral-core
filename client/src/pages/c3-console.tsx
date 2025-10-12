import { useState } from "react";
import { useLocation } from "wouter";
import { ArrowLeft, Terminal, AlertTriangle, Power, RefreshCw, Shield, Activity } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

export default function C3Console() {
  const [, setLocation] = useLocation();
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmAction, setConfirmAction] = useState<string>("");
  const [confirmCode, setConfirmCode] = useState("");

  const { data: metrics } = useQuery<{
    cpu_usage?: number;
    memory_usage?: number;
    active_users?: number;
  }>({ queryKey: ["/api/system/metrics"] });

  const handleCriticalAction = (action: string) => {
    setConfirmAction(action);
    setShowConfirmModal(true);
    setConfirmCode("");
  };

  const executeAction = () => {
    if (confirmCode === "CONFIRM") {
      console.log(`Executing critical action: ${confirmAction}`);
      setShowConfirmModal(false);
      setConfirmCode("");
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
                <h1 className="text-[#00FFD1] text-xl font-bold tracking-[0.2em]">CONSOLE MENU</h1>
                <p className="text-[#00FFD1]/60 text-xs tracking-[0.3em]">SYSTEM CONTROL & MONITORING</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-[#00FFD1]/60 text-sm tracking-wider">[D034]</div>
            </div>
          </div>
        </header>

        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-3 gap-6 mb-8">
              <div className="border border-[#00FFD1]/30 p-6"
                   style={{ clipPath: 'polygon(15px 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%, 0 15px)' }}>
                <div className="flex items-center gap-3 mb-4">
                  <Activity className="text-[#00FFD1]" />
                  <h3 className="text-[#00FFD1] tracking-wider">CPU USAGE</h3>
                </div>
                <div className="text-3xl text-white font-bold mb-2">{metrics?.cpu_usage || 0}%</div>
                <div className="h-2 bg-[#00FFD1]/20 relative overflow-hidden">
                  <div 
                    className="absolute inset-y-0 left-0 bg-[#00FFD1]"
                    style={{ width: `${metrics?.cpu_usage || 0}%` }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-[shimmer_2s_infinite]" />
                </div>
              </div>

              <div className="border border-[#00FFD1]/30 p-6"
                   style={{ clipPath: 'polygon(15px 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%, 0 15px)' }}>
                <div className="flex items-center gap-3 mb-4">
                  <Activity className="text-[#00FFD1]" />
                  <h3 className="text-[#00FFD1] tracking-wider">MEMORY</h3>
                </div>
                <div className="text-3xl text-white font-bold mb-2">{metrics?.memory_usage || 0}%</div>
                <div className="h-2 bg-[#00FFD1]/20 relative overflow-hidden">
                  <div 
                    className="absolute inset-y-0 left-0 bg-[#00FFD1]"
                    style={{ width: `${metrics?.memory_usage || 0}%` }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-[shimmer_2s_infinite]" />
                </div>
              </div>

              <div className="border border-[#00FFD1]/30 p-6"
                   style={{ clipPath: 'polygon(15px 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%, 0 15px)' }}>
                <div className="flex items-center gap-3 mb-4">
                  <Shield className="text-[#00FFD1]" />
                  <h3 className="text-[#00FFD1] tracking-wider">ACTIVE USERS</h3>
                </div>
                <div className="text-3xl text-white font-bold mb-2">{metrics?.active_users || 0}</div>
                <div className="text-[#00FFD1]/60 text-sm">CONNECTIONS</div>
              </div>
            </div>

            <div className="mb-8">
              <div className="inline-block mb-4 px-4 py-1 border border-[#FF3A5B]/50">
                <h2 className="text-[#FF3A5B] text-xs tracking-[0.4em]">CRITICAL OPERATIONS</h2>
              </div>
              <p className="text-white/60 text-sm mb-4">⚠ 二重確認が必要な操作</p>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <button
                onClick={() => handleCriticalAction("SYSTEM_RESTART")}
                className="group relative p-6 border-2 border-[#FF3A5B]/50 hover:border-[#FF3A5B] transition-all duration-300"
                style={{ clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))' }}
                data-testid="button-restart"
              >
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 border-2 border-[#FF3A5B] flex items-center justify-center group-hover:bg-[#FF3A5B] group-hover:text-[#080A0F] transition-all"
                       style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' }}>
                    <RefreshCw className="w-6 h-6" />
                  </div>
                  <div className="text-left flex-1">
                    <h3 className="text-[#FF3A5B] text-lg font-bold tracking-wider mb-1">SYSTEM RESTART</h3>
                    <p className="text-white/60 text-sm">システム全体を再起動</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => handleCriticalAction("EMERGENCY_STOP")}
                className="group relative p-6 border-2 border-[#FF3A5B]/50 hover:border-[#FF3A5B] transition-all duration-300"
                style={{ clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))' }}
                data-testid="button-emergency"
              >
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 border-2 border-[#FF3A5B] flex items-center justify-center group-hover:bg-[#FF3A5B] group-hover:text-[#080A0F] transition-all"
                       style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' }}>
                    <Power className="w-6 h-6" />
                  </div>
                  <div className="text-left flex-1">
                    <h3 className="text-[#FF3A5B] text-lg font-bold tracking-wider mb-1">EMERGENCY STOP</h3>
                    <p className="text-white/60 text-sm">緊急停止プロトコル</p>
                  </div>
                </div>
              </button>
            </div>

            <div className="border border-[#00FFD1]/30 p-6"
                 style={{ clipPath: 'polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px)' }}>
              <div className="flex items-center gap-3 mb-4">
                <Terminal className="text-[#00FFD1]" />
                <h3 className="text-[#00FFD1] tracking-wider">SYSTEM LOG</h3>
              </div>
              <div className="space-y-2 font-mono text-sm">
                <div className="flex gap-3 text-[#00FFD1]/60">
                  <span>[{new Date().toLocaleTimeString()}]</span>
                  <span>System initialized successfully</span>
                </div>
                <div className="flex gap-3 text-[#00FFD1]/60">
                  <span>[{new Date().toLocaleTimeString()}]</span>
                  <span>All modules online</span>
                </div>
                <div className="flex gap-3 text-[#00FFD1]/60">
                  <span>[{new Date().toLocaleTimeString()}]</span>
                  <span>Security protocols active</span>
                </div>
              </div>
            </div>
          </div>
        </main>

        <footer className="relative px-8 py-4 border-t border-[#00FFD1]/30">
          <div className="flex items-center justify-between text-xs text-[#00FFD1]/60">
            <div>CONSOLE MENU // LIBRAL CORE</div>
            <div>{new Date().toLocaleTimeString()}</div>
          </div>
        </footer>
        
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#00FFD1] to-transparent" />
      </div>

      {showConfirmModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" data-testid="modal-confirm">
          <div className="bg-[#080A0F] border-2 border-[#FF3A5B] p-8 max-w-md w-full"
               style={{ clipPath: 'polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px)' }}>
            <div className="flex items-center gap-3 mb-6">
              <AlertTriangle className="text-[#FF3A5B] w-8 h-8" />
              <h3 className="text-[#FF3A5B] text-xl font-bold tracking-wider">CRITICAL ACTION</h3>
            </div>
            
            <p className="text-white/80 mb-4">実行しようとしています: <span className="text-[#FF3A5B] font-bold">{confirmAction}</span></p>
            <p className="text-white/60 text-sm mb-6">確認のため、"CONFIRM" と入力してください</p>
            
            <input
              type="text"
              value={confirmCode}
              onChange={(e) => setConfirmCode(e.target.value.toUpperCase())}
              className="w-full bg-[#080A0F] border border-[#00FFD1]/50 text-[#00FFD1] px-4 py-3 mb-6 font-mono focus:outline-none focus:border-[#00FFD1]"
              placeholder="CONFIRM"
              data-testid="input-confirm"
            />
            
            <div className="flex gap-4">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="flex-1 px-4 py-3 border border-[#00FFD1]/50 text-[#00FFD1] hover:bg-[#00FFD1]/10 transition-all"
                data-testid="button-cancel"
              >
                CANCEL
              </button>
              <button
                onClick={executeAction}
                disabled={confirmCode !== "CONFIRM"}
                className={`flex-1 px-4 py-3 border-2 transition-all ${
                  confirmCode === "CONFIRM"
                    ? "border-[#FF3A5B] text-[#FF3A5B] hover:bg-[#FF3A5B] hover:text-[#080A0F]"
                    : "border-[#FF3A5B]/30 text-[#FF3A5B]/30 cursor-not-allowed"
                }`}
                data-testid="button-execute"
              >
                EXECUTE
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}

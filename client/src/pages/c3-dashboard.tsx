import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Terminal, Grid3x3, Shield, Settings, Activity } from "lucide-react";

export default function C3Dashboard() {
  const [, setLocation] = useLocation();
  const [doorOpen, setDoorOpen] = useState(false);
  const [transitioning, setTransitioning] = useState(false);

  useEffect(() => {
    setTimeout(() => setDoorOpen(true), 100);
  }, []);

  const navigateWithTransition = (path: string) => {
    setTransitioning(true);
    setDoorOpen(false);
    setTimeout(() => {
      setLocation(path);
    }, 400);
  };

  return (
    <div className="relative min-h-screen bg-[#080A0F] overflow-hidden" style={{ fontFamily: 'Share Tech Mono, monospace' }}>
      <div className="absolute inset-0 opacity-10 pointer-events-none" 
           style={{ 
             backgroundImage: `
               linear-gradient(#00FFD1 1px, transparent 1px),
               linear-gradient(90deg, #00FFD1 1px, transparent 1px)
             `,
             backgroundSize: '20px 20px'
           }} 
      />
      
      <div className="absolute inset-0 opacity-5 pointer-events-none"
           style={{
             backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' /%3E%3C/svg%3E")`
           }}
      />

      <div 
        className={`door-left absolute left-0 top-0 h-full w-1/2 bg-[#080A0F] z-50 transition-transform duration-[400ms] ease-[cubic-bezier(0.25,1,0.5,1)] ${
          doorOpen ? '-translate-x-full' : 'translate-x-0'
        }`}
        style={{
          clipPath: 'polygon(0 0, 85% 0, 100% 50%, 85% 100%, 0 100%)',
          borderRight: '2px solid #00FFD1',
          boxShadow: doorOpen ? 'none' : '0 0 30px #00FFD1'
        }}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-[#00FFD1] text-6xl font-bold animate-pulse">L</div>
        </div>
      </div>

      <div 
        className={`door-right absolute right-0 top-0 h-full w-1/2 bg-[#080A0F] z-50 transition-transform duration-[400ms] ease-[cubic-bezier(0.25,1,0.5,1)] ${
          doorOpen ? 'translate-x-full' : 'translate-x-0'
        }`}
        style={{
          clipPath: 'polygon(15% 0, 100% 0, 100% 100%, 15% 100%, 0% 50%)',
          borderLeft: '2px solid #00FFD1',
          boxShadow: doorOpen ? 'none' : '0 0 30px #00FFD1'
        }}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-[#00FFD1] text-6xl font-bold animate-pulse">C</div>
        </div>
      </div>

      <div className="relative z-10 min-h-screen flex flex-col">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#00FFD1] to-transparent" />
        
        <header className="relative px-8 py-6 border-b border-[#00FFD1]/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 border-2 border-[#00FFD1] flex items-center justify-center"
                   style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' }}>
                <Terminal className="text-[#00FFD1]" />
              </div>
              <div>
                <h1 className="text-[#00FFD1] text-2xl font-bold tracking-[0.2em]" style={{ fontFamily: 'Major Mono Display, monospace' }}>LIBRAL CORE</h1>
                <p className="text-[#00FFD1]/60 text-xs tracking-[0.3em]">C3 CONSOLE - CONTEXT COMMAND CENTER</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-[#00FFD1]/60 text-sm tracking-wider">[系統-連続]</div>
              <div className="flex gap-1">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className={`w-2 h-2 ${i < 4 ? 'bg-[#00FFD1]' : 'bg-[#00FFD1]/20'}`} />
                ))}
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 flex items-center justify-center p-8">
          <div className="w-full max-w-6xl">
            <div className="text-center mb-16">
              <div className="inline-block mb-4 px-6 py-2 border border-[#00FFD1]/50"
                   style={{ clipPath: 'polygon(10% 0%, 90% 0%, 100% 50%, 90% 100%, 10% 100%, 0% 50%)' }}>
                <h2 className="text-[#00FFD1] text-sm tracking-[0.4em]">SYSTEM STATUS</h2>
              </div>
              <div className="text-white/80 text-lg tracking-[0.2em] mb-8">S07.K - メイン制御インターフェース</div>
              
              <div className="flex items-center justify-center gap-8 mb-8">
                <div className="flex flex-col items-center">
                  <div className="w-20 h-1 bg-[#00FFD1] mb-2 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-[shimmer_2s_infinite]" 
                         style={{ animation: 'shimmer 2s infinite' }} />
                  </div>
                  <span className="text-[#00FFD1]/60 text-xs">ONLINE</span>
                </div>
                <div className="text-[#00FFD1] text-4xl">●</div>
                <div className="flex flex-col items-center">
                  <div className="w-20 h-1 bg-[#00FFD1] mb-2 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-[shimmer_2s_infinite]" />
                  </div>
                  <span className="text-[#00FFD1]/60 text-xs">READY</span>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              <button
                onClick={() => navigateWithTransition("/c3/apps")}
                className="group relative p-8 border-2 border-[#00FFD1]/50 hover:border-[#00FFD1] transition-all duration-300 hover:shadow-[0_0_30px_rgba(0,255,209,0.3)]"
                style={{ clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))' }}
                data-testid="button-apps"
              >
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-16 h-16 border-2 border-[#00FFD1] flex items-center justify-center group-hover:bg-[#00FFD1] group-hover:text-[#080A0F] transition-all"
                       style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' }}>
                    <Grid3x3 className="w-8 h-8" />
                  </div>
                  <div className="text-left flex-1">
                    <h3 className="text-[#00FFD1] text-xl font-bold tracking-[0.2em] mb-1">BUTTON 01</h3>
                    <p className="text-[#00FFD1]/60 text-sm">D008</p>
                  </div>
                  <div className="text-[#00FFD1] text-2xl group-hover:translate-x-2 transition-transform">▶</div>
                </div>
                <p className="text-white/70 text-sm tracking-wide">アプリケーション & 機能モジュール管理</p>
                <div className="absolute bottom-4 right-4 text-[#00FFD1]/30 text-xs">/// APPS &amp; FEATURES</div>
              </button>

              <button
                onClick={() => navigateWithTransition("/c3/console")}
                className="group relative p-8 border-2 border-[#00FFD1]/50 hover:border-[#00FFD1] transition-all duration-300 hover:shadow-[0_0_30px_rgba(0,255,209,0.3)]"
                style={{ clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))' }}
                data-testid="button-console"
              >
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-16 h-16 border-2 border-[#00FFD1] flex items-center justify-center group-hover:bg-[#00FFD1] group-hover:text-[#080A0F] transition-all"
                       style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' }}>
                    <Terminal className="w-8 h-8" />
                  </div>
                  <div className="text-left flex-1">
                    <h3 className="text-[#00FFD1] text-xl font-bold tracking-[0.2em] mb-1">BUTTON 02</h3>
                    <p className="text-[#00FFD1]/60 text-sm">D034</p>
                  </div>
                  <div className="text-[#00FFD1] text-2xl group-hover:translate-x-2 transition-transform">▶</div>
                </div>
                <p className="text-white/70 text-sm tracking-wide">コンソールメニュー & システム制御</p>
                <div className="absolute bottom-4 right-4 text-[#00FFD1]/30 text-xs">/// CONSOLE MENU</div>
              </button>
            </div>

            <div className="mt-12 relative">
              <div className="border border-[#00FFD1]/30 p-6"
                   style={{ clipPath: 'polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px)' }}>
                <div className="flex items-center gap-2 mb-4">
                  <div className="text-[#00FFD1] text-sm tracking-[0.3em]">INFO</div>
                  <div className="flex-1 h-px bg-[#00FFD1]/30" />
                  <div className="text-[#00FFD1]/60 text-xs">▶</div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Shield className="text-[#00FFD1] w-4 h-4" />
                    <span className="text-white/60">Security: </span>
                    <span className="text-[#00FFD1]">ACTIVE</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Activity className="text-[#00FFD1] w-4 h-4" />
                    <span className="text-white/60">Modules: </span>
                    <span className="text-[#00FFD1]">6 ONLINE</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Settings className="text-[#00FFD1] w-4 h-4" />
                    <span className="text-white/60">Status: </span>
                    <span className="text-[#00FFD1]">OPERATIONAL</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <footer className="relative px-8 py-4 border-t border-[#00FFD1]/30">
          <div className="flex items-center justify-between text-xs text-[#00FFD1]/60">
            <div className="flex gap-4">
              <span>02/05</span>
              <span>///</span>
              <span>LIBRAL CORE v1.0</span>
            </div>
            <div className="flex gap-4">
              <span>CONTEXT-COMMAND-CENTER</span>
              <span>///</span>
              <span className="font-mono">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </footer>
        
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#00FFD1] to-transparent" />
      </div>

      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}

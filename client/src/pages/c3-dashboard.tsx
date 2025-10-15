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
    <div className="relative min-h-screen bg-black overflow-hidden" style={{ fontFamily: 'Share Tech Mono, monospace' }}>
      {/* グリッドオーバーレイ - 白 */}
      <div className="absolute inset-0 opacity-5 pointer-events-none" 
           style={{ 
             backgroundImage: `
               linear-gradient(white 1px, transparent 1px),
               linear-gradient(90deg, white 1px, transparent 1px)
             `,
             backgroundSize: '20px 20px'
           }} 
      />
      
      {/* ノイズテクスチャ */}
      <div className="absolute inset-0 opacity-3 pointer-events-none"
           style={{
             backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' /%3E%3C/svg%3E")`
           }}
      />

      {/* ドアアニメーション - 白ボーダー */}
      <div 
        className={`door-left absolute left-0 top-0 h-full w-1/2 bg-black z-50 transition-transform duration-[400ms] ease-[cubic-bezier(0.25,1,0.5,1)] ${
          doorOpen ? '-translate-x-full' : 'translate-x-0'
        }`}
        style={{
          clipPath: 'polygon(0 0, 85% 0, 100% 50%, 85% 100%, 0 100%)',
          borderRight: '2px solid white',
          boxShadow: doorOpen ? 'none' : '0 0 20px rgba(255,255,255,0.5)'
        }}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-white text-6xl font-bold">L</div>
        </div>
      </div>

      <div 
        className={`door-right absolute right-0 top-0 h-full w-1/2 bg-black z-50 transition-transform duration-[400ms] ease-[cubic-bezier(0.25,1,0.5,1)] ${
          doorOpen ? 'translate-x-full' : 'translate-x-0'
        }`}
        style={{
          clipPath: 'polygon(15% 0, 100% 0, 100% 100%, 15% 100%, 0% 50%)',
          borderLeft: '2px solid white',
          boxShadow: doorOpen ? 'none' : '0 0 20px rgba(255,255,255,0.5)'
        }}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-white text-6xl font-bold">C</div>
        </div>
      </div>

      <div className="relative z-10 min-h-screen flex flex-col">
        {/* トップライン - 白 */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white to-transparent opacity-50" />
        
        <header className="relative px-8 py-6 border-b border-white/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 border-2 border-white flex items-center justify-center"
                   style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' }}>
                <Terminal className="text-white" />
              </div>
              <div>
                <h1 className="text-white text-2xl font-bold tracking-[0.2em]" style={{ fontFamily: 'Major Mono Display, monospace' }}>LIBRAL CORE</h1>
                <p className="text-white/60 text-xs tracking-[0.3em]">C3 CONSOLE - CONTEXT COMMAND CENTER</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-white/60 text-sm tracking-wider">[2-2]</div>
              <div className="flex gap-1">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className={`w-2 h-2 ${i < 4 ? 'bg-white' : 'bg-white/20'}`} />
                ))}
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 flex items-center justify-center p-4 md:p-8">
          <div className="w-full max-w-5xl space-y-6 md:space-y-8">
            {/* Yellow Stripes - Top Left */}
            <div className="flex gap-1 mb-4">
              <div className="w-2 h-8 bg-[#FFEB00]" style={{ transform: 'skewX(-20deg)' }}></div>
              <div className="w-2 h-8 bg-[#FFEB00]" style={{ transform: 'skewX(-20deg)' }}></div>
              <div className="w-2 h-8 bg-[#FFEB00]" style={{ transform: 'skewX(-20deg)' }}></div>
            </div>

            {/* APP Button */}
            <button
              onClick={() => navigateWithTransition('/c3/apps')}
              className="group relative w-full p-8 md:p-16 bg-gradient-to-br from-[#1a1a1a] to-black transition-all duration-300"
              style={{ 
                clipPath: 'polygon(40px 0, calc(100% - 40px) 0, 100% 40px, 100% calc(100% - 40px), calc(100% - 40px) 100%, 40px 100%, 0 calc(100% - 40px), 0 40px)',
                border: '3px solid white'
              }}
              data-testid="button-apps"
            >
              <div className="flex items-center justify-center gap-6 md:gap-12">
                <div className="text-[#FFEB00] text-5xl md:text-7xl font-bold group-hover:translate-x-2 transition-transform">›</div>
                <h3 className="text-white text-5xl md:text-8xl font-bold tracking-[0.15em]">APP</h3>
              </div>
            </button>

            {/* Yellow Dots Separator */}
            <div className="flex justify-center gap-1.5">
              {[...Array(10)].map((_, i) => (
                <div key={i} className={`w-2 h-2 ${i < 7 ? 'bg-[#FFEB00]' : 'bg-gray-600'}`} />
              ))}
            </div>

            {/* CONSOLE Button */}
            <button
              onClick={() => navigateWithTransition('/c3/console')}
              className="group relative w-full p-8 md:p-16 bg-gradient-to-br from-[#1a1a1a] to-black transition-all duration-300"
              style={{ 
                clipPath: 'polygon(40px 0, calc(100% - 40px) 0, 100% 40px, 100% calc(100% - 40px), calc(100% - 40px) 100%, 40px 100%, 0 calc(100% - 40px), 0 40px)',
                border: '3px solid white'
              }}
              data-testid="button-console"
            >
              <div className="flex items-center justify-center gap-6 md:gap-12">
                <div className="w-14 h-14 md:w-20 md:h-20 border-4 border-[#FFEB00] rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-[#FFEB00] text-3xl md:text-5xl font-bold">!</span>
                </div>
                <h3 className="text-white text-4xl md:text-7xl font-bold tracking-[0.15em]">CONSOLE</h3>
              </div>
            </button>
          </div>
        </main>

        <footer className="relative px-8 py-4 border-t border-white/20">
          <div className="flex items-center justify-between text-xs text-white/60">
            <div>LIBRAL CORE // C3 CONSOLE</div>
            <div>{new Date().toLocaleTimeString()}</div>
          </div>
        </footer>
        
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white to-transparent opacity-50" />
      </div>
    </div>
  );
}

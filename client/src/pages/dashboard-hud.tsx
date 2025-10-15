import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { 
  Activity, 
  Users, 
  Zap, 
  Database, 
  Shield,
  Cpu,
  MemoryStick,
  Wifi,
  Settings,
  ChevronRight,
  X,
  Play,
  Home,
  FileText,
  Image as ImageIcon,
  BarChart3
} from "lucide-react";

interface SystemMetrics {
  cpuUsage: string;
  memoryUsage: string;
  activeUsers: string;
  apiRequestsPerMinute: string;
}

export default function DashboardHud() {
  // VERSION 2.0.1 - YELLOW DESIGN - Force Reload
  const [, setLocation] = useLocation();
  const [showSplash, setShowSplash] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);

  const { data: metrics } = useQuery<SystemMetrics>({
    queryKey: ['/api/system/metrics'],
    refetchInterval: 5000
  });

  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  const menuItems = [
    { id: 'dashboard', icon: <Home className="w-5 h-5" />, label: 'DASHBOARD', desc: 'System overview and monitoring' },
    { id: 'aegis', icon: <Shield className="w-5 h-5" />, label: 'AEGIS-PGP', desc: 'Encryption and security' },
    { id: 'database', icon: <Database className="w-5 h-5" />, label: 'DATABASE', desc: 'Data management system' },
    { id: 'analytics', icon: <BarChart3 className="w-5 h-5" />, label: 'ANALYTICS', desc: 'System metrics and reports' },
    { id: 'users', icon: <Users className="w-5 h-5" />, label: 'USERS', desc: 'User management console' },
  ];

  const metrics_display = [
    { label: 'LOADING...', value: metrics?.cpuUsage || '40', unit: '%' },
    { label: 'PROCESSING...', value: metrics?.memoryUsage || '58', unit: '%' },
    { label: 'NETWORK...', value: metrics?.activeUsers || '70', unit: '%' },
  ];

  if (showSplash) {
    return (
      <div className="min-h-screen bg-black flex items-center overflow-hidden relative px-8 md:px-16" style={{ fontFamily: 'Share Tech Mono, monospace' }}>
        {/* Grid Background */}
        <div className="absolute inset-0 opacity-5" 
             style={{ 
               backgroundImage: `
                 linear-gradient(#333 1px, transparent 1px),
                 linear-gradient(90deg, #333 1px, transparent 1px)
               `,
               backgroundSize: '20px 20px'
             }} 
        />
        
        {/* Yellow Circuit Pattern - Right Side */}
        <svg className="absolute right-0 top-0 h-full w-1/3 md:w-1/2" viewBox="0 0 400 800" fill="none" preserveAspectRatio="xMaxYMid meet">
          <path d="M 250 0 L 250 150 L 300 200 L 300 250 L 350 300 L 350 500 L 300 550 L 300 800" 
                stroke="#FFEB00" strokeWidth="8" fill="none"/>
          <path d="M 350 0 L 350 120 L 400 170 L 400 280 L 350 330 L 350 470 L 300 520 L 300 800" 
                stroke="#FFEB00" strokeWidth="8" fill="none"/>
          <circle cx="300" cy="250" r="30" stroke="#FFEB00" strokeWidth="3" fill="none"/>
          <circle cx="300" cy="250" r="50" stroke="#FFEB00" strokeWidth="2" fill="none" opacity="0.5"/>
          <circle cx="325" cy="500" r="25" stroke="#FFEB00" strokeWidth="3" fill="#FFEB00"/>
          <rect x="240" y="180" width="8" height="40" fill="#FFEB00" transform="rotate(45 244 200)"/>
          <rect x="340" y="560" width="8" height="40" fill="#FFEB00" transform="rotate(-45 344 580)"/>
        </svg>
        
        {/* Content - Left Side */}
        <div className="relative z-10 flex flex-col justify-center max-w-md">
          {/* "00" Large Text */}
          <h1 className="text-[120px] md:text-[160px] lg:text-[200px] font-bold text-white leading-none tracking-tight mb-4">00</h1>
          
          {/* Yellow Stripes */}
          <div className="flex gap-1 mb-6">
            <div className="w-2 h-6 bg-[#FFEB00]" style={{ transform: 'skewX(-20deg)' }}></div>
            <div className="w-2 h-6 bg-[#FFEB00]" style={{ transform: 'skewX(-20deg)' }}></div>
            <div className="w-2 h-6 bg-[#FFEB00]" style={{ transform: 'skewX(-20deg)' }}></div>
            <div className="w-2 h-6 bg-[#FFEB00]" style={{ transform: 'skewX(-20deg)' }}></div>
          </div>
          
          {/* LIBRAL Title */}
          <h2 className="text-4xl md:text-5xl font-bold text-[#FFEB00] tracking-[0.3em] mb-8">LIBRAL</h2>
          
          {/* Description */}
          <p className="text-gray-400 text-sm leading-relaxed max-w-xs">
            Lorem ipsum qrqeieemet, arqs iepsnsequetruee us can un seadia riq no- addir ut tamce tcr ninq aliqn eeiiai netus placentre mek ae unentumlaadi.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white" style={{ fontFamily: 'Share Tech Mono, monospace' }}>
      {/* Grid Background */}
      <div className="fixed inset-0 opacity-5 pointer-events-none" 
           style={{ 
             backgroundImage: `
               linear-gradient(#333 1px, transparent 1px),
               linear-gradient(90deg, #333 1px, transparent 1px)
             `,
             backgroundSize: '20px 20px'
           }} 
      />

      {/* Mobile/Desktop Layout */}
      <div className="relative flex flex-col lg:flex-row min-h-screen">
        
        {/* Main Content Area */}
        <div className="flex-1 p-4 md:p-8 overflow-y-auto">
          
          {/* Header */}
          <div className="mb-8 relative">
            <div className="absolute top-0 left-0 w-16 h-16 border-l-2 border-t-2 border-white opacity-30"></div>
            <div className="absolute top-0 right-0 w-16 h-16 border-r-2 border-t-2 border-white opacity-30"></div>
            
            <div className="flex items-center justify-between py-4 px-2">
              <button 
                onClick={() => window.history.back()}
                className="p-2 hover:bg-white/10 transition-colors"
                data-testid="button-back"
              >
                <ChevronRight className="w-6 h-6 rotate-180" />
              </button>
              
              <div className="text-center">
                <div className="text-sm text-gray-500">[ 2-2 ]</div>
              </div>
              
              <button 
                onClick={() => setMenuOpen(!menuOpen)}
                className="lg:hidden p-2 hover:bg-white/10 transition-colors"
                data-testid="button-menu-toggle"
              >
                <Settings className="w-6 h-6" />
              </button>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-center my-8 tracking-[0.3em]">
              LIBRAL
            </h1>
            
            <div className="flex justify-center gap-4 mb-6">
              <div className="flex items-center gap-2">
                <div className="w-8 h-1 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
                <div className="w-8 h-1 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-1 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
                <div className="w-8 h-1 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
              </div>
            </div>
          </div>

          {/* Main Buttons - Mobile: Stack, Desktop: 2-col */}
          <div className="max-w-4xl mx-auto space-y-4 mb-8">
            <button 
              onClick={() => setLocation('/c3/apps')}
              className="group w-full p-6 bg-black border-2 border-white hover:border-[white] transition-all relative overflow-hidden"
              style={{ 
                clipPath: 'polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px)'
              }}
              data-testid="button-apps"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <ChevronRight className="w-6 h-6 text-[white]" />
                  <span className="text-2xl md:text-3xl font-bold tracking-wider">APP</span>
                </div>
              </div>
              <div className="absolute top-2 right-4 flex gap-1">
                <div className="w-1 h-6 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
                <div className="w-1 h-6 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
                <div className="w-1 h-6 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
              </div>
            </button>

            <button 
              onClick={() => setLocation('/c3/console')}
              className="group w-full p-6 bg-black border-2 border-white hover:border-[white] transition-all relative overflow-hidden"
              style={{ 
                clipPath: 'polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px)'
              }}
              data-testid="button-console"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full border-2 border-[white] flex items-center justify-center">
                  <div className="text-[white] text-xl font-bold">!</div>
                </div>
                <span className="text-2xl md:text-3xl font-bold tracking-wider">CONSOLE</span>
              </div>
              <div className="absolute top-2 right-4 flex gap-1">
                <div className="w-1 h-6 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
                <div className="w-1 h-6 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
                <div className="w-1 h-6 bg-[white]" style={{ transform: 'skewX(-20deg)' }}></div>
              </div>
            </button>
          </div>

          {/* Metrics - Mobile: Stack, Desktop: 3-col */}
          <div className="max-w-4xl mx-auto space-y-4 md:grid md:grid-cols-3 md:gap-6 md:space-y-0">
            {metrics_display.map((metric, index) => (
              <div key={index} className="space-y-2" data-testid={`metric-${index}`}>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400">{metric.label}</span>
                  <span className="text-white font-bold">{metric.value}{metric.unit}</span>
                </div>
                <div className="h-6 bg-gray-800 border border-gray-700 relative overflow-hidden">
                  <div 
                    className="h-full bg-[white] transition-all duration-500"
                    style={{ width: `${metric.value}%` }}
                  >
                    <div className="absolute inset-0 flex gap-1 opacity-60">
                      {[...Array(10)].map((_, i) => (
                        <div key={i} className="w-1 h-full bg-black" style={{ transform: 'skewX(-20deg)' }}></div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Visual Elements */}
          <div className="max-w-4xl mx-auto mt-12 space-y-8">
            {/* Circular Gauge */}
            <div className="border-2 border-white p-8 relative" 
                 style={{ clipPath: 'polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px)' }}>
              <div className="flex justify-center mb-6">
                <svg width="200" height="200" viewBox="0 0 200 200">
                  <circle cx="100" cy="100" r="90" stroke="#333" strokeWidth="2" fill="none"/>
                  <circle cx="100" cy="100" r="75" stroke="#333" strokeWidth="1" fill="none"/>
                  <circle cx="100" cy="100" r="60" stroke="#333" strokeWidth="1" fill="none"/>
                  <line x1="100" y1="10" x2="100" y2="190" stroke="#333" strokeWidth="1"/>
                  <line x1="10" y1="100" x2="190" y2="100" stroke="#333" strokeWidth="1"/>
                  <circle cx="100" cy="100" r="5" fill="#333"/>
                  <text x="100" y="170" textAnchor="middle" className="text-xs fill-gray-500" style={{ fontFamily: 'Share Tech Mono, monospace' }}>
                    TARGET COORDS 233-117-351
                  </text>
                </svg>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <button 
                  className="p-4 border-2 border-white hover:border-[white] transition-all flex items-center gap-3"
                  style={{ clipPath: 'polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px)' }}
                  data-testid="button-folder"
                >
                  <X className="w-6 h-6 text-[white]" />
                  <div className="text-left">
                    <div className="text-lg font-bold">FOLDER</div>
                    <div className="text-xs text-gray-500">FCN 2502 305 20</div>
                  </div>
                </button>
                
                <button 
                  className="p-4 border-2 border-white hover:border-[white] transition-all flex items-center gap-3"
                  style={{ clipPath: 'polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px)' }}
                  data-testid="button-media"
                >
                  <Play className="w-6 h-6 text-[white]" />
                  <div className="text-left">
                    <div className="text-lg font-bold">MEDIA</div>
                    <div className="text-xs text-gray-500">FCN 4492 277 08</div>
                  </div>
                </button>
              </div>
            </div>
          </div>

        </div>

        {/* Right Sidebar Menu - PC only */}
        <div className={`
          fixed lg:relative top-0 right-0 h-full w-80 bg-black border-l-2 border-white
          transform transition-transform duration-300 z-50
          ${menuOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}
        `}>
          <div className="p-6 h-full overflow-y-auto">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-xl font-bold tracking-wider">MENU</h2>
              <button 
                onClick={() => setMenuOpen(false)}
                className="lg:hidden p-2 hover:bg-white/10"
                data-testid="button-menu-close"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              {menuItems.map((item, index) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setLocation(`/${item.id}`);
                    setMenuOpen(false);
                  }}
                  className="w-full group hover:bg-white/5 transition-all relative"
                  data-testid={`menu-${item.id}`}
                >
                  <div className="flex items-center gap-4 p-4 border-l-4 border-transparent hover:border-[white]">
                    <div className="w-12 h-12 rounded-full border-2 border-[white] flex items-center justify-center flex-shrink-0">
                      {item.icon}
                    </div>
                    <div className="flex-1 text-left">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-[white]">{String.fromCharCode(65 + index)}</span>
                        <span className="font-bold text-sm">{item.label}</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{item.desc}</div>
                    </div>
                    <div className="w-8 h-8 rotate-45 bg-[white] flex items-center justify-center flex-shrink-0">
                      <span className="text-black font-bold text-sm -rotate-45">0{index + 1}</span>
                    </div>
                  </div>
                  
                  {index < menuItems.length - 1 && (
                    <div className="ml-16 flex items-center gap-1">
                      {[...Array(8)].map((_, i) => (
                        <div key={i} className="w-1 h-1 bg-gray-700"></div>
                      ))}
                    </div>
                  )}
                </button>
              ))}
            </div>

            {/* Data Visualizations */}
            <div className="mt-12 space-y-6">
              <div className="border-2 border-gray-800 p-4">
                <div className="flex items-center justify-center gap-2 mb-4">
                  <div className="w-16 h-16 rounded-full border-4 border-[white] border-t-transparent animate-spin"></div>
                  <div className="text-center">
                    <div className="text-sm text-gray-500">DATA</div>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-2">
                {[60, 34, 70].map((value, i) => (
                  <div key={i} className="text-center">
                    <svg width="60" height="60" viewBox="0 0 60 60">
                      <circle cx="30" cy="30" r="25" stroke="#333" strokeWidth="4" fill="none"/>
                      <circle 
                        cx="30" cy="30" r="25" 
                        stroke="white" 
                        strokeWidth="4" 
                        fill="none"
                        strokeDasharray={`${value * 1.57} ${157 - value * 1.57}`}
                        transform="rotate(-90 30 30)"
                      />
                      <text x="30" y="35" textAnchor="middle" className="text-sm font-bold fill-[white]">
                        {value}
                      </text>
                    </svg>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

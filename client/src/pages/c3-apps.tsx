import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { ArrowLeft, Building2, Play, PieChart, Camera, Image as ImageIcon } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

interface ModuleInfo {
  id: string;
  name: string;
  label: string;
  description: string;
  icon: string;
  number: string;
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
      id: "quam-lacus",
      name: "QUAM LACUS",
      label: "A",
      description: "Tigr man Rocis sitgrat veqrcmo olirsquetrtione cusrtet ea ustarrc depiciutusr",
      icon: "building",
      number: "01"
    },
    {
      id: "natoque-mi",
      name: "NATOQUE MI",
      label: "B",
      description: "Duiblaurun orppe ue us corresquit envetotur bonusus nisldam voltt",
      icon: "play",
      number: "02"
    },
    {
      id: "et-cubilia",
      name: "ET CUBILIA",
      label: "C",
      description: "Blensidunt eicdtum erget ruuc usauam nec trudislis ea nurtrung ulli",
      icon: "chart",
      number: "03"
    },
    {
      id: "dis-rutrum",
      name: "DIS RUTRUM",
      label: "D",
      description: "Suspdiurse conasue ufranes ulstrcs, et line ebel nasmin mun",
      icon: "camera",
      number: "04"
    },
    {
      id: "lacus-duis",
      name: "LACUS DUIS",
      label: "E",
      description: "Cillam solliccstus ruxum volusoatter quamus frinm ellikendonstki",
      icon: "media",
      number: "05"
    }
  ];

  const getIcon = (iconName: string) => {
    const iconClass = "w-10 h-10 text-[#FFEB00]";
    switch (iconName) {
      case "building": return <Building2 className={iconClass} />;
      case "play": return <Play className={iconClass} />;
      case "chart": return <PieChart className={iconClass} />;
      case "camera": return <Camera className={iconClass} />;
      case "media": return <ImageIcon className={iconClass} />;
      default: return <Building2 className={iconClass} />;
    }
  };

  return (
    <div className="relative min-h-screen bg-[black] overflow-hidden font-mono">
      <div className="absolute inset-0 opacity-10 pointer-events-none" 
           style={{ 
             backgroundImage: `
               linear-gradient(white 1px, transparent 1px),
               linear-gradient(90deg, white 1px, transparent 1px)
             `,
             backgroundSize: '20px 20px'
           }} 
      />

      <div className="relative z-10 min-h-screen flex flex-col">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[white] to-transparent" />
        
        <header className="relative px-8 py-6 border-b border-[white]/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setLocation("/c3")}
                className="w-10 h-10 border border-[white]/50 hover:border-[white] hover:bg-[white]/10 flex items-center justify-center transition-all"
                data-testid="button-back"
              >
                <ArrowLeft className="text-[#FFEB00]" />
              </button>
              <div>
                <h1 className="text-[white] text-xl font-bold tracking-[0.2em]">APPS & FEATURES</h1>
                <p className="text-[white]/60 text-xs tracking-[0.3em]">MODULE MANAGEMENT CONSOLE</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-[white]/60 text-sm tracking-wider">[D008]</div>
            </div>
          </div>
        </header>

        <main className="flex-1 p-8 md:p-16">
          <div className="max-w-6xl mx-auto space-y-8">
            {modules.map((module, index) => (
              <button
                key={module.id}
                onClick={() => setLocation(`/c3/apps/${module.id}`)}
                className="group w-full flex items-center gap-6 md:gap-12 p-6 md:p-8 bg-[#0A0A0A] hover:bg-[#151515] transition-all duration-300 border border-white/10 hover:border-white/30"
                data-testid={`card-module-${module.id}`}
              >
                {/* Left: Yellow Circle Icon */}
                <div className="flex-shrink-0 w-20 h-20 border-4 border-[#FFEB00] rounded-full flex items-center justify-center">
                  {getIcon(module.icon)}
                </div>

                {/* Center: Label + Title + Description */}
                <div className="flex-1 text-left">
                  <div className="flex items-center gap-4 mb-2">
                    {/* Dotted Line */}
                    <div className="hidden md:block w-16 border-t-2 border-dotted border-white/30"></div>
                    {/* Label */}
                    <span className="text-white font-bold text-sm tracking-widest">{module.label}</span>
                    <span className="text-white/40 text-xs">DEVELOPMENT</span>
                  </div>
                  <h3 className="text-white text-2xl md:text-3xl font-bold mb-2">{module.name}</h3>
                  <p className="text-white/60 text-sm md:text-base">{module.description}</p>
                </div>

                {/* Right: Yellow Diamond Number */}
                <div className="flex-shrink-0 flex items-center gap-4">
                  {/* Dotted Line */}
                  <div className="hidden md:flex gap-1">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="w-1 h-1 bg-white/30"></div>
                    ))}
                  </div>
                  {/* Diamond Number */}
                  <div className="w-16 h-16 bg-[#FFEB00] flex items-center justify-center transform rotate-45">
                    <span className="text-black text-xl font-bold transform -rotate-45">{module.number}</span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </main>

        <footer className="relative px-8 py-4 border-t border-[white]/30">
          <div className="flex items-center justify-between text-xs text-[white]/60">
            <div>MODULE REGISTRY // LIBRAL CORE</div>
            <div>{new Date().toLocaleTimeString()}</div>
          </div>
        </footer>
        
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[white] to-transparent" />
      </div>
    </div>
  );
}

import { useQuery } from "@tanstack/react-query";
import { Link, useLocation } from "wouter";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Terminal,
  Activity,
  Box,
  Shield,
  Zap,
  Settings,
  Database,
  Network,
} from "lucide-react";

interface ModuleDef {
  id: string;
  name: string;
  active?: boolean;
  category?: string;
}

export function Sidebar() {
  const [location] = useLocation();

  const { data: modules = [] } = useQuery<ModuleDef[]>({
    queryKey: ["/api/modules"],
    initialData: [],
  });
  const list = Array.isArray(modules) ? modules : [];

  const coreItems = [
    { name: "Cockpit", icon: LayoutDashboard, path: "/c3" },
    { name: "Monitor", icon: Activity, path: "/monitor" },
    { name: "Control", icon: Terminal, path: "/control" },
  ];

  const systemItems = [
    { name: "Settings", icon: Settings, path: "/settings" },
    { name: "Database", icon: Database, path: "/database-management" },
    { name: "API Hub", icon: Network, path: "/api-hub" },
  ];

  return (
    <div className="h-full w-64 bg-sidebar border-r border-sidebar-border flex flex-col text-sidebar-foreground relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-purple-500 opacity-50" />

      <div className="p-6 border-b border-sidebar-border/50">
        <h1 className="text-2xl font-black tracking-tighter bg-gradient-to-br from-white to-gray-400 bg-clip-text text-transparent">
          LIBRAL C3
        </h1>
        <p className="text-[10px] uppercase tracking-widest text-primary/80 mt-1 font-mono">
          Sovereign Autarchy
        </p>
      </div>

      <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-8 scrollbar-hide">
        <div>
          <p className="px-3 text-[10px] font-bold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Core Ops
          </p>
          <div className="space-y-1">
            {coreItems.map((item) => (
              <Link key={item.path} href={item.path}>
                <div
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md transition-all cursor-pointer group hover:bg-sidebar-accent/50",
                    location === item.path
                      ? "bg-primary/10 text-primary border-l-2 border-primary"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <item.icon
                    className={cn(
                      "h-4 w-4 transition-colors",
                      location === item.path ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                    )}
                  />
                  <span className="font-medium text-sm">{item.name}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>

        <div>
          <p className="px-3 text-[10px] font-bold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Active Modules
          </p>
          <div className="space-y-1">
            <Link href="/creation">
              <div
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md cursor-pointer hover:bg-sidebar-accent/50 group",
                  location === "/creation" ? "bg-primary/10 text-primary border-l-2 border-primary" : "text-muted-foreground"
                )}
              >
                <Zap className="h-4 w-4 group-hover:text-yellow-400 transition-colors" />
                <span className="font-medium text-sm">AI Engine</span>
              </div>
            </Link>

            <Link href="/c3/apps/aegis-pgp">
              <div
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md cursor-pointer hover:bg-sidebar-accent/50 group",
                  location.includes("aegis-pgp") ? "bg-primary/10 text-primary border-l-2 border-primary" : "text-muted-foreground"
                )}
              >
                <Shield className="h-4 w-4 group-hover:text-emerald-400 transition-colors" />
                <span className="font-medium text-sm">Aegis GPG</span>
              </div>
            </Link>

            {list.map((mod) => (
              <Link key={mod.id} href={`/c3/apps/${mod.id}`}>
                <div
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md transition-all cursor-pointer hover:bg-sidebar-accent/50 group",
                    location.includes(mod.id) ? "bg-primary/10 text-primary border-l-2 border-primary" : "text-muted-foreground"
                  )}
                >
                  <Box className="h-4 w-4 group-hover:text-blue-400 transition-colors" />
                  <span className="font-medium text-sm">{mod.name}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>

        <div>
          <p className="px-3 text-[10px] font-bold text-muted-foreground/60 uppercase tracking-wider mb-2">
            System
          </p>
          <div className="space-y-1">
            {systemItems.map((item) => (
              <Link key={item.path} href={item.path}>
                <div
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md transition-all cursor-pointer group hover:bg-sidebar-accent/50",
                    location === item.path ? "text-foreground" : "text-muted-foreground"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  <span className="font-medium text-sm">{item.name}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </nav>

      <div className="p-4 border-t border-sidebar-border/50 bg-black/20">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse" />
          <span className="text-xs font-mono text-muted-foreground">CORE: ONLINE</span>
        </div>
      </div>
    </div>
  );
}

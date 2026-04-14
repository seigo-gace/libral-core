import { useLocation } from "wouter";
import { Sidebar } from "@/components/dashboard/sidebar";
import C3Dashboard from "@/pages/c3-dashboard";
import C3Apps from "@/pages/c3-apps";
import C3Console from "@/pages/c3-console";
import C3ModuleDetail from "@/pages/c3-module-detail";

/**
 * C3 Console レイアウト: 動的サイドバー + メインコンテンツ。
 * /c3, /c3/apps, /c3/apps/:id, /c3/console で共通表示。
 */
export default function C3Layout() {
  const [location] = useLocation();

  const segment = location.split("/").filter(Boolean);
  const isC3Root = location === "/c3";
  const isC3Apps = location === "/c3/apps";
  const isC3AppsDetail = segment[0] === "c3" && segment[1] === "apps" && segment[2] != null;
  const isC3Console = location === "/c3/console";

  let Child = C3Dashboard;
  if (isC3Console) Child = C3Console;
  else if (isC3AppsDetail) Child = C3ModuleDetail;
  else if (isC3Apps) Child = C3Apps;

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto min-w-0">
        <Child />
      </main>
    </div>
  );
}

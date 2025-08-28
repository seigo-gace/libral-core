import { Sidebar } from "@/components/dashboard/sidebar";
import { SystemHealth } from "@/components/dashboard/system-health";
import { ModuleStatus } from "@/components/dashboard/module-status";
import { RealtimeEvents } from "@/components/dashboard/realtime-events";
import { InfrastructureStatus } from "@/components/dashboard/infrastructure-status";
import { Analytics } from "@/components/dashboard/analytics";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

export default function Dashboard() {
  const queryClient = useQueryClient();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await queryClient.invalidateQueries();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="flex h-screen bg-dark-900">
      <Sidebar />
      
      {/* Main Content */}
      <div className="flex-1 overflow-auto focus:outline-none">
        {/* Header */}
        <header className="bg-dark-800 border-b border-dark-700">
          <div className="mx-auto py-3 px-4 sm:py-4 sm:px-6 lg:px-8">
            <div className="flex flex-col space-y-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
              {/* Title - Mobile optimized */}
              <div className="pt-12 md:pt-0">
                <h1 className="text-xl sm:text-2xl font-bold text-dark-50">システム概要</h1>
                <p className="text-xs sm:text-sm text-dark-400 mt-1">Libral Core マイクロサービス管理コンソール</p>
              </div>
              
              {/* Actions - Mobile optimized */}
              <div className="flex items-center justify-between sm:justify-end space-x-2 sm:space-x-4">
                <Button
                  onClick={handleRefresh}
                  disabled={isRefreshing}
                  variant="secondary"
                  size="sm"
                  className="bg-dark-700 hover:bg-dark-600 text-dark-200"
                  data-testid="button-refresh"
                >
                  <RefreshCw className={`${isRefreshing ? 'animate-spin' : ''} h-4 w-4 sm:mr-2`} />
                  <span className="hidden sm:inline">リフレッシュ</span>
                </Button>
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-white text-xs sm:text-sm font-medium">管</span>
                  </div>
                  <span className="text-xs sm:text-sm font-medium text-dark-50 hidden sm:inline">管理者</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="mx-auto py-4 px-4 sm:py-6 sm:px-6 lg:px-8 max-w-7xl">
          {/* System Health Overview */}
          <SystemHealth />

          {/* Module Status and Real-time Events */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
            <ModuleStatus />
            <RealtimeEvents />
          </div>

          {/* Infrastructure Status */}
          <InfrastructureStatus />

          {/* Analytics */}
          <Analytics />
        </main>
      </div>
    </div>
  );
}

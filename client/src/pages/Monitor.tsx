import { useQuery } from "@tanstack/react-query";
import { Link, useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Activity, Shield, Database, Cpu, Zap, Gauge, Sliders, Sparkles } from "lucide-react";
import { lpoApi } from "@/api/lpo";
import { vaporizationApi } from "@/api/vaporization";
import { selfEvolutionApi } from "@/api/selfevolution";

export default function Monitor() {
  const [location] = useLocation();
  const { data: healthScore, isLoading: healthLoading } = useQuery({
    queryKey: ["/lpo/metrics/health-score"],
    queryFn: lpoApi.getHealthScore,
    refetchInterval: 5000,
  });

  const { data: zkAudit, isLoading: zkLoading } = useQuery({
    queryKey: ["/lpo/zk-audit/status"],
    queryFn: lpoApi.getZKAuditStatus,
    refetchInterval: 10000,
  });

  const { data: vaporizationStats, isLoading: vaporizationLoading } = useQuery({
    queryKey: ["/vaporization/stats"],
    queryFn: vaporizationApi.getStats,
    refetchInterval: 5000,
  });

  const { data: moduleHealth, isLoading: moduleHealthLoading } = useQuery({
    queryKey: ["/selfevolution/module-health"],
    queryFn: selfEvolutionApi.getModuleHealth,
    refetchInterval: 10000,
  });

  const { data: dashboard, isLoading: dashboardLoading } = useQuery({
    queryKey: ["/selfevolution/dashboard"],
    queryFn: selfEvolutionApi.getDashboard,
    refetchInterval: 15000,
  });

  const getHealthColor = (score: number) => {
    if (score >= 90) return "text-green-400";
    if (score >= 75) return "text-yellow-400";
    return "text-red-400";
  };

  const getHealthStatus = (score: number) => {
    if (score >= 90) return "EXCELLENT";
    if (score >= 75) return "GOOD";
    if (score >= 50) return "DEGRADED";
    return "CRITICAL";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <h1 className="text-3xl md:text-4xl font-mono text-cyan-400 glow-cyan" data-testid="text-page-title">
            【監視モード】MONITOR_HUD
          </h1>
          <div className="flex items-center gap-2">
            <Link href="/monitor">
              <Button 
                variant={location === "/monitor" ? "default" : "outline"}
                className={location === "/monitor" ? "neon-button" : "border-cyan-500/50 text-cyan-400"}
                data-testid="link-monitor"
              >
                <Gauge className="w-4 h-4 mr-2" />
                監視
              </Button>
            </Link>
            <Link href="/control">
              <Button 
                variant="outline"
                className="border-cyan-500/50 text-cyan-400"
                data-testid="link-control"
              >
                <Sliders className="w-4 h-4 mr-2" />
                制御
              </Button>
            </Link>
            <Link href="/creation">
              <Button 
                variant="outline"
                className="border-cyan-500/50 text-cyan-400"
                data-testid="link-creation"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                開発
              </Button>
            </Link>
            <Badge className="bg-cyan-900/50 text-cyan-400 border-cyan-500/50" data-testid="badge-mode">
              SURVEILLANCE
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="neon-card" data-testid="card-health-score">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-cyan-400 font-mono">
                <Activity className="w-5 h-5" />
                LPO健全性スコア
              </CardTitle>
            </CardHeader>
            <CardContent>
              {healthLoading ? (
                <div className="text-cyan-400/50" data-testid="text-health-loading">ロード中...</div>
              ) : (
                <div className="space-y-4">
                  <div className="text-center">
                    <div className={`text-6xl font-bold font-mono ${getHealthColor(healthScore?.health_score || 0)}`} data-testid="text-health-score-value">
                      {healthScore?.health_score || 0}
                    </div>
                    <div className="text-sm text-cyan-400/70 mt-2" data-testid="text-health-status">
                      {getHealthStatus(healthScore?.health_score || 0)}
                    </div>
                  </div>
                  <Progress value={healthScore?.health_score || 0} className="h-2" data-testid="progress-health" />
                  <div className="text-xs text-cyan-400/60 font-mono space-y-1">
                    <div data-testid="text-uptime">UPTIME: {healthScore?.metrics?.system_uptime_percentage?.toFixed(2)}%</div>
                    <div data-testid="text-response-time">AVG_RESPONSE: {healthScore?.metrics?.avg_response_time_ms?.toFixed(0)}ms</div>
                    <div data-testid="text-error-rate">ERROR_RATE: {healthScore?.metrics?.error_rate_percentage?.toFixed(3)}%</div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="neon-card" data-testid="card-zk-audit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-cyan-400 font-mono">
                <Shield className="w-5 h-5" />
                ZK監査ステータス
              </CardTitle>
            </CardHeader>
            <CardContent>
              {zkLoading ? (
                <div className="text-cyan-400/50" data-testid="text-zk-loading">ロード中...</div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-center gap-4">
                    <div 
                      className={`w-20 h-20 rounded-full flex items-center justify-center ${
                        zkAudit?.status === "passed" ? "bg-green-500/20 glow-green" : "bg-red-500/20"
                      }`}
                      data-testid={`status-zk-${zkAudit?.status || 'unknown'}`}
                    >
                      <div className={`w-16 h-16 rounded-full ${
                        zkAudit?.status === "passed" ? "bg-green-500" : "bg-red-500"
                      }`}></div>
                    </div>
                  </div>
                  <div className="text-center space-y-2">
                    <Badge 
                      variant={zkAudit?.proof_valid ? "default" : "destructive"}
                      className="font-mono"
                      data-testid="badge-proof-status"
                    >
                      {zkAudit?.proof_valid ? "PROOF_VALID" : "PROOF_INVALID"}
                    </Badge>
                    <div className="text-xs text-cyan-400/60 font-mono" data-testid="text-audit-id">
                      AUDIT_ID: {zkAudit?.audit_id || "N/A"}
                    </div>
                    <div className="text-xs text-cyan-400/60 font-mono" data-testid="text-audit-timestamp">
                      {zkAudit?.timestamp || "N/A"}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="neon-card" data-testid="card-vaporization">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-cyan-400 font-mono">
                <Database className="w-5 h-5" />
                キャッシュ揮発状況
              </CardTitle>
            </CardHeader>
            <CardContent>
              {vaporizationLoading ? (
                <div className="text-cyan-400/50" data-testid="text-vaporization-loading">ロード中...</div>
              ) : (
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-cyan-400 font-mono" data-testid="text-ttl-hours">
                      {vaporizationStats?.max_ttl_hours || 24}h
                    </div>
                    <div className="text-sm text-cyan-400/70" data-testid="text-ttl-label">MAX_TTL</div>
                  </div>
                  <div className="space-y-2 text-xs text-cyan-400/80 font-mono">
                    <div className="flex justify-between" data-testid="row-ttl-enforced">
                      <span>TTL強制実行:</span>
                      <span className="text-green-400">{vaporizationStats?.ttl_enforced_count || 0}</span>
                    </div>
                    <div className="flex justify-between" data-testid="row-flush-executed">
                      <span>FLUSH実行:</span>
                      <span className="text-green-400">{vaporizationStats?.flush_executed_count || 0}</span>
                    </div>
                    <div className="flex justify-between" data-testid="row-vaporization-status">
                      <span>揮発プロトコル:</span>
                      <Badge 
                        variant={vaporizationStats?.vaporization_enabled ? "default" : "destructive"}
                        className="text-xs"
                      >
                        {vaporizationStats?.vaporization_enabled ? "ACTIVE" : "INACTIVE"}
                      </Badge>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="neon-card" data-testid="card-module-health">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-cyan-400 font-mono">
              <Cpu className="w-5 h-5" />
              モジュール健全性
            </CardTitle>
          </CardHeader>
          <CardContent>
            {moduleHealthLoading ? (
              <div className="text-cyan-400/50" data-testid="text-module-loading">ロード中...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {moduleHealth && Object.entries(moduleHealth).map(([module, health]: [string, any]) => (
                  <div key={module} className="hud-panel p-4 space-y-2" data-testid={`module-status-${module}`}>
                    <div className="text-cyan-400 font-mono font-bold uppercase">{module}</div>
                    <Badge 
                      variant={health.status === "operational" ? "default" : "destructive"}
                      className="text-xs"
                      data-testid={`badge-${module}-status`}
                    >
                      {health.status}
                    </Badge>
                    {health.health_score !== undefined && (
                      <div className="text-xs text-cyan-400/70" data-testid={`text-${module}-score`}>
                        SCORE: {health.health_score}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="neon-card" data-testid="card-selfevolution-overview">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-cyan-400 font-mono">
              <Zap className="w-5 h-5" />
              SelfEvolution概要
            </CardTitle>
          </CardHeader>
          <CardContent>
            {dashboardLoading ? (
              <div className="text-cyan-400/50" data-testid="text-dashboard-loading">ロード中...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <div className="text-sm text-cyan-400/70 font-mono">Knowledge Base</div>
                  <div className="text-2xl font-bold text-cyan-400" data-testid="text-kb-records">
                    {dashboard?.knowledge_base?.total_knowledge_records || 0}
                  </div>
                  <div className="text-xs text-cyan-400/60" data-testid="text-kb-contributors">
                    貢献者: {dashboard?.knowledge_base?.unique_contributors || 0}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-sm text-cyan-400/70 font-mono">Evolution Queue</div>
                  <div className="flex gap-2 text-sm">
                    <Badge className="bg-yellow-900/50 text-yellow-400" data-testid="badge-pending-tasks">
                      保留: {dashboard?.evolution_queue?.pending_tasks || 0}
                    </Badge>
                    <Badge className="bg-blue-900/50 text-blue-400" data-testid="badge-in-progress-tasks">
                      進行中: {dashboard?.evolution_queue?.in_progress || 0}
                    </Badge>
                    <Badge className="bg-green-900/50 text-green-400" data-testid="badge-completed-tasks">
                      完了: {dashboard?.evolution_queue?.completed || 0}
                    </Badge>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-sm text-cyan-400/70 font-mono">Privacy Guarantees</div>
                  <div className="text-xs text-cyan-400/80 space-y-1">
                    <div data-testid="text-cache-ttl">Cache TTL: {dashboard?.privacy_guarantees?.max_cache_ttl_hours || 24}h</div>
                    <div data-testid="text-vaporization-enabled">
                      Vaporization: {dashboard?.privacy_guarantees?.vaporization_enabled ? "✓" : "✗"}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

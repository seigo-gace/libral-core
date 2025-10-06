import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { AlertTriangle, Shield, Activity, Ban, Gauge, Sliders, Sparkles } from "lucide-react";
import { governanceApi } from "@/api/governance";
import { lpoApi } from "@/api/lpo";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

export default function Control() {
  const [location] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [cradReason, setCradReason] = useState("");
  const [ammBlockId, setAmmBlockId] = useState("");
  const [ammReason, setAmmReason] = useState("");
  const [rateLimitEnabled, setRateLimitEnabled] = useState(true);
  const [rateLimitThreshold, setRateLimitThreshold] = useState(100);

  const { data: governanceStatus } = useQuery({
    queryKey: ["/governance/status"],
    queryFn: governanceApi.getStatus,
    refetchInterval: 5000,
  });

  const triggerCRADMutation = useMutation({
    mutationFn: governanceApi.triggerCRAD,
    onSuccess: (data) => {
      toast({
        title: "CRADトリガー成功",
        description: `復旧ID: ${data.trigger_id} - ステータス: ${data.status}`,
        variant: "default",
      });
      queryClient.invalidateQueries({ queryKey: ["/governance/status"] });
      setCradReason("");
    },
    onError: (error: Error) => {
      toast({
        title: "CRADトリガー失敗",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const ammUnblockMutation = useMutation({
    mutationFn: governanceApi.unblockAMM,
    onSuccess: (data) => {
      toast({
        title: "AMMブロック解除成功",
        description: data.message,
        variant: "default",
      });
      queryClient.invalidateQueries({ queryKey: ["/governance/status"] });
      setAmmBlockId("");
      setAmmReason("");
    },
    onError: (error: Error) => {
      toast({
        title: "AMMブロック解除失敗",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const updatePolicyMutation = useMutation({
    mutationFn: lpoApi.updatePolicy,
    onSuccess: () => {
      toast({
        title: "ポリシー更新成功",
        description: "レート制限設定が更新されました",
        variant: "default",
      });
      queryClient.invalidateQueries({ queryKey: ["/lpo"] });
    },
    onError: (error: Error) => {
      toast({
        title: "ポリシー更新失敗",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleCRADTrigger = () => {
    if (!cradReason.trim()) {
      toast({
        title: "入力エラー",
        description: "理由を入力してください",
        variant: "destructive",
      });
      return;
    }
    triggerCRADMutation.mutate({
      recovery_type: "manual",
      reason: cradReason,
    });
  };

  const handleAMMUnblock = () => {
    if (!ammBlockId.trim() || !ammReason.trim()) {
      toast({
        title: "入力エラー",
        description: "ブロックIDと理由を入力してください",
        variant: "destructive",
      });
      return;
    }
    ammUnblockMutation.mutate({
      block_id: ammBlockId,
      reason: ammReason,
    });
  };

  const handleRateLimitToggle = () => {
    updatePolicyMutation.mutate({
      policy_type: "rate_limit",
      enabled: !rateLimitEnabled,
      threshold: rateLimitThreshold,
    });
    setRateLimitEnabled(!rateLimitEnabled);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <h1 className="text-3xl md:text-4xl font-mono text-cyan-400 glow-cyan" data-testid="text-page-title">
            【制御モード】CONTROL_PANEL
          </h1>
          <div className="flex items-center gap-2">
            <Link href="/monitor">
              <Button 
                variant="outline"
                className="border-cyan-500/50 text-cyan-400"
                data-testid="link-monitor"
              >
                <Gauge className="w-4 h-4 mr-2" />
                監視
              </Button>
            </Link>
            <Link href="/control">
              <Button 
                variant={location === "/control" ? "default" : "outline"}
                className={location === "/control" ? "neon-button" : "border-cyan-500/50 text-cyan-400"}
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
            <Badge className="bg-red-900/50 text-red-400 border-red-500/50" data-testid="badge-mode">
              EXECUTION
            </Badge>
          </div>
        </div>

        <Card className="neon-card border-yellow-500/50" data-testid="card-governance-status">
          <CardHeader>
            <CardTitle className="text-cyan-400 font-mono">システムステータス</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm font-mono">
              <div className="space-y-1">
                <div className="text-cyan-400/70">AMM</div>
                <Badge variant={governanceStatus?.amm_active ? "default" : "destructive"} data-testid="badge-amm-status">
                  {governanceStatus?.amm_active ? "ACTIVE" : "INACTIVE"}
                </Badge>
              </div>
              <div className="space-y-1">
                <div className="text-cyan-400/70">CRAD</div>
                <Badge variant={governanceStatus?.crad_active ? "default" : "destructive"} data-testid="badge-crad-status">
                  {governanceStatus?.crad_active ? "ACTIVE" : "INACTIVE"}
                </Badge>
              </div>
              <div className="space-y-1">
                <div className="text-cyan-400/70">Blocked IPs</div>
                <div className="text-cyan-400 text-lg" data-testid="text-blocked-ips">{governanceStatus?.blocked_ips_count || 0}</div>
              </div>
              <div className="space-y-1">
                <div className="text-cyan-400/70">Recovery</div>
                <Badge variant={governanceStatus?.recovery_in_progress ? "default" : "secondary"} data-testid="badge-recovery-status">
                  {governanceStatus?.recovery_in_progress ? "IN_PROGRESS" : "IDLE"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="neon-card border-red-500/50" data-testid="card-crad-trigger">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-400 font-mono">
                <AlertTriangle className="w-5 h-5" />
                HAフェイルオーバー (CRAD)
              </CardTitle>
              <CardDescription className="text-cyan-400/70 font-mono text-xs">
                CRITICAL - 高可用性復旧トリガー
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="crad-reason" className="text-cyan-400 font-mono">理由</Label>
                <Textarea
                  id="crad-reason"
                  placeholder="復旧トリガーの理由を入力..."
                  value={cradReason}
                  onChange={(e) => setCradReason(e.target.value)}
                  className="bg-black/50 border-cyan-500/50 text-cyan-400 font-mono"
                  data-testid="textarea-crad-reason"
                />
              </div>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button 
                    className="w-full bg-red-600 hover:bg-red-700 text-white font-mono glow-cyan"
                    disabled={triggerCRADMutation.isPending}
                    data-testid="button-trigger-crad"
                  >
                    {triggerCRADMutation.isPending ? "実行中..." : "🚨 CRAD復旧トリガー"}
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent className="neon-card">
                  <AlertDialogHeader>
                    <AlertDialogTitle className="text-red-400 font-mono">確認</AlertDialogTitle>
                    <AlertDialogDescription className="text-cyan-400/70 font-mono">
                      HAフェイルオーバーをトリガーしますか？この操作は取り消せません。
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel className="font-mono" data-testid="button-cancel-crad">キャンセル</AlertDialogCancel>
                    <AlertDialogAction 
                      onClick={handleCRADTrigger}
                      className="bg-red-600 hover:bg-red-700 font-mono"
                      data-testid="button-confirm-crad"
                    >
                      実行
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </CardContent>
          </Card>

          <Card className="neon-card border-yellow-500/50" data-testid="card-rate-limit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-yellow-400 font-mono">
                <Activity className="w-5 h-5" />
                レート制限制御
              </CardTitle>
              <CardDescription className="text-cyan-400/70 font-mono text-xs">
                WARNING - API呼び出し制限設定
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="rate-limit-switch" className="text-cyan-400 font-mono">
                  レート制限
                </Label>
                <Switch
                  id="rate-limit-switch"
                  checked={rateLimitEnabled}
                  onCheckedChange={handleRateLimitToggle}
                  disabled={updatePolicyMutation.isPending}
                  data-testid="switch-rate-limit"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="rate-threshold" className="text-cyan-400 font-mono">
                  閾値 (req/min)
                </Label>
                <Input
                  id="rate-threshold"
                  type="number"
                  value={rateLimitThreshold}
                  onChange={(e) => setRateLimitThreshold(parseInt(e.target.value))}
                  className="bg-black/50 border-cyan-500/50 text-cyan-400 font-mono"
                  data-testid="input-rate-threshold"
                />
              </div>
              <Badge 
                variant={rateLimitEnabled ? "default" : "secondary"}
                className="font-mono"
                data-testid="badge-rate-limit-status"
              >
                {rateLimitEnabled ? "ENABLED" : "DISABLED"}
              </Badge>
            </CardContent>
          </Card>

          <Card className="neon-card border-yellow-500/50 lg:col-span-2" data-testid="card-amm-unblock">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-yellow-400 font-mono">
                <Ban className="w-5 h-5" />
                AMMブロック解除
              </CardTitle>
              <CardDescription className="text-cyan-400/70 font-mono text-xs">
                WARNING - アクセス管理ミドルウェアブロック解除
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="amm-block-id" className="text-cyan-400 font-mono">ブロックID</Label>
                  <Input
                    id="amm-block-id"
                    placeholder="block_abc123..."
                    value={ammBlockId}
                    onChange={(e) => setAmmBlockId(e.target.value)}
                    className="bg-black/50 border-cyan-500/50 text-cyan-400 font-mono"
                    data-testid="input-amm-block-id"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="amm-reason" className="text-cyan-400 font-mono">理由</Label>
                  <Input
                    id="amm-reason"
                    placeholder="解除理由..."
                    value={ammReason}
                    onChange={(e) => setAmmReason(e.target.value)}
                    className="bg-black/50 border-cyan-500/50 text-cyan-400 font-mono"
                    data-testid="input-amm-reason"
                  />
                </div>
              </div>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button 
                    className="w-full mt-4 bg-yellow-600 hover:bg-yellow-700 text-black font-mono font-bold"
                    disabled={ammUnblockMutation.isPending}
                    data-testid="button-unblock-amm"
                  >
                    {ammUnblockMutation.isPending ? "実行中..." : "⚠️ AMMブロック解除"}
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent className="neon-card">
                  <AlertDialogHeader>
                    <AlertDialogTitle className="text-yellow-400 font-mono">確認</AlertDialogTitle>
                    <AlertDialogDescription className="text-cyan-400/70 font-mono">
                      ブロックID: {ammBlockId} を解除しますか？
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel className="font-mono" data-testid="button-cancel-amm">キャンセル</AlertDialogCancel>
                    <AlertDialogAction 
                      onClick={handleAMMUnblock}
                      className="bg-yellow-600 hover:bg-yellow-700 text-black font-mono"
                      data-testid="button-confirm-amm"
                    >
                      解除実行
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

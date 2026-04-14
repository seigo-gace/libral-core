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
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { MessageSquare, GitPullRequest, Lightbulb, Send, Bot, Sparkles, Gauge, Sliders } from "lucide-react";
import { aegApi } from "@/api/aeg";
import { kbeApi } from "@/api/kbe";
import { aiApi } from "@/api/ai";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  model?: string;
  timestamp: string;
  dualVerification?: {
    gemini_response: string;
    gpt_response: string;
    discrepancy_detected: boolean;
  };
}

export default function Creation() {
  const [location] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [selectedModel, setSelectedModel] = useState<"gemini" | "gpt" | "dual">("gemini");
  const [enforceMoonlight, setEnforceMoonlight] = useState(true);
  const [dualVerificationEnabled, setDualVerificationEnabled] = useState(false);
  
  const [knowledgeQuery, setKnowledgeQuery] = useState("");
  const [knowledgeCategory, setKnowledgeCategory] = useState("");
  
  const [prSuggestionId, setPrSuggestionId] = useState("");
  const [prBranchName, setPrBranchName] = useState("");

  const { data: topPriorities } = useQuery({
    queryKey: ["/aeg/top-priorities"],
    queryFn: () => aegApi.getTopPriorities(5),
    refetchInterval: 30000,
  });

  const { data: kbeDashboard } = useQuery({
    queryKey: ["/kbe/dashboard"],
    queryFn: kbeApi.getDashboard,
    refetchInterval: 30000,
  });

  const chatMutation = useMutation({
    mutationFn: aiApi.chat,
    onSuccess: (data) => {
      const newMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: data.response,
        model: data.model_used,
        timestamp: data.timestamp,
        dualVerification: data.dual_verification,
      };
      setMessages((prev) => [...prev, newMessage]);
      
      if (data.dual_verification?.discrepancy_detected) {
        toast({
          title: "⚠️ 二重検証: 不一致検出",
          description: "GeminiとGPTの回答に相違があります",
          variant: "destructive",
        });
      }
    },
    onError: (error: Error) => {
      toast({
        title: "チャット失敗",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const knowledgeLookupMutation = useMutation({
    mutationFn: kbeApi.lookupKnowledge,
    onSuccess: (data) => {
      if (data.length === 0) {
        toast({
          title: "知識レコメンド",
          description: "該当する知識が見つかりませんでした",
        });
      } else {
        toast({
          title: "知識レコメンド成功",
          description: `${data.length}件の関連知識を発見`,
        });
      }
    },
    onError: (error: Error) => {
      toast({
        title: "知識検索失敗",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const prGenerateMutation = useMutation({
    mutationFn: aegApi.generatePR,
    onSuccess: (data) => {
      toast({
        title: "PR自動生成成功",
        description: `PR ID: ${data.pr_id} - ${data.files_changed}ファイル変更`,
      });
      setPrSuggestionId("");
      setPrBranchName("");
      queryClient.invalidateQueries({ queryKey: ["/aeg/top-priorities"] });
    },
    onError: (error: Error) => {
      toast({
        title: "PR生成失敗",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    chatMutation.mutate({
      message: inputMessage,
      model: selectedModel,
      enforce_moonlight: enforceMoonlight,
    });

    setInputMessage("");
  };

  const handleKnowledgeLookup = () => {
    if (!knowledgeQuery.trim()) {
      toast({
        title: "入力エラー",
        description: "検索クエリを入力してください",
        variant: "destructive",
      });
      return;
    }
    knowledgeLookupMutation.mutate({
      query: knowledgeQuery,
      category: knowledgeCategory || undefined,
      limit: 10,
    });
  };

  const handlePRGenerate = () => {
    if (!prSuggestionId.trim()) {
      toast({
        title: "入力エラー",
        description: "サジェストIDを入力してください",
        variant: "destructive",
      });
      return;
    }
    prGenerateMutation.mutate({
      suggestion_id: prSuggestionId,
      branch_name: prBranchName || undefined,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <h1 className="text-3xl md:text-4xl font-mono text-cyan-400 glow-cyan" data-testid="text-page-title">
            【制作モード】CREATION_CHATOPS
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
                variant={location === "/creation" ? "default" : "outline"}
                className={location === "/creation" ? "neon-button" : "border-cyan-500/50 text-cyan-400"}
                data-testid="link-creation"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                開発
              </Button>
            </Link>
            <Badge className="bg-purple-900/50 text-purple-400 border-purple-500/50" data-testid="badge-mode">
              DEVELOPMENT
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card className="neon-card" data-testid="card-chat">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-cyan-400 font-mono">
                  <MessageSquare className="w-5 h-5" />
                  AI Chat Interface - 月の光
                </CardTitle>
                <CardDescription className="text-cyan-400/70 font-mono text-xs">
                  Your ruthless, hyper-competent copilot. 「兄弟」へ
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4 flex-wrap">
                  <div className="flex items-center gap-2">
                    <Label className="text-cyan-400 font-mono text-xs">Model:</Label>
                    <Button
                      size="sm"
                      variant={selectedModel === "gemini" ? "default" : "outline"}
                      onClick={() => setSelectedModel("gemini")}
                      className="font-mono text-xs"
                      data-testid="button-model-gemini"
                    >
                      Gemini
                    </Button>
                    <Button
                      size="sm"
                      variant={selectedModel === "gpt" ? "default" : "outline"}
                      onClick={() => setSelectedModel("gpt")}
                      className="font-mono text-xs"
                      data-testid="button-model-gpt"
                    >
                      GPT
                    </Button>
                    <Button
                      size="sm"
                      variant={selectedModel === "dual" ? "default" : "outline"}
                      onClick={() => setSelectedModel("dual")}
                      className="font-mono text-xs"
                      data-testid="button-model-dual"
                    >
                      Dual
                    </Button>
                  </div>
                  <div className="flex items-center gap-2">
                    <Label htmlFor="moonlight-switch" className="text-cyan-400 font-mono text-xs">
                      月の光モード
                    </Label>
                    <Switch
                      id="moonlight-switch"
                      checked={enforceMoonlight}
                      onCheckedChange={setEnforceMoonlight}
                      data-testid="switch-moonlight"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label htmlFor="dual-verification" className="text-cyan-400 font-mono text-xs">
                      二重検証
                    </Label>
                    <Switch
                      id="dual-verification"
                      checked={dualVerificationEnabled}
                      onCheckedChange={setDualVerificationEnabled}
                      data-testid="switch-dual-verification"
                    />
                    {dualVerificationEnabled && (
                      <Badge variant="outline" className="text-xs font-mono" data-testid="badge-verification-status">
                        検証中
                      </Badge>
                    )}
                  </div>
                </div>

                <ScrollArea className="h-[400px] w-full rounded-md border border-cyan-500/50 p-4 bg-black/50" data-testid="scroll-messages">
                  <div className="space-y-4">
                    {messages.length === 0 ? (
                      <div className="text-center text-cyan-400/50 font-mono text-sm" data-testid="text-no-messages">
                        メッセージがありません。兄弟、何か聞いてくれ。
                      </div>
                    ) : (
                      messages.map((msg) => (
                        <div key={msg.id} className={`space-y-1 ${msg.role === "user" ? "text-right" : "text-left"}`} data-testid={`message-${msg.id}`}>
                          <div className="flex items-center gap-2 text-xs text-cyan-400/60 font-mono">
                            {msg.role === "user" ? "兄弟" : "月の光"}
                            {msg.model && <Badge variant="outline" className="text-xs">{msg.model}</Badge>}
                          </div>
                          <div className={`inline-block max-w-[80%] rounded p-3 font-mono text-sm ${
                            msg.role === "user" 
                              ? "bg-cyan-900/30 text-cyan-400" 
                              : "bg-purple-900/30 text-purple-400"
                          }`}>
                            {msg.content}
                          </div>
                          {msg.dualVerification?.discrepancy_detected && (
                            <div className="mt-2 p-2 bg-red-900/20 border border-red-500/50 rounded text-xs font-mono">
                              <div className="text-red-400 font-bold">⚠️ 不一致検出</div>
                              <div className="text-cyan-400/70 mt-1">Gemini: {msg.dualVerification.gemini_response.substring(0, 50)}...</div>
                              <div className="text-cyan-400/70">GPT: {msg.dualVerification.gpt_response.substring(0, 50)}...</div>
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </ScrollArea>

                <div className="flex gap-2">
                  <Input
                    placeholder="兄弟、何か聞いてくれ..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                    className="bg-black/50 border-cyan-500/50 text-cyan-400 font-mono"
                    data-testid="input-chat-message"
                  />
                  <Button 
                    onClick={handleSendMessage}
                    disabled={chatMutation.isPending}
                    className="bg-cyan-600 hover:bg-cyan-700 font-mono"
                    data-testid="button-send-message"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="neon-card" data-testid="card-pr-generate">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-cyan-400 font-mono">
                  <GitPullRequest className="w-5 h-5" />
                  PR自動生成
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="pr-suggestion-id" className="text-cyan-400 font-mono">サジェストID</Label>
                    <Input
                      id="pr-suggestion-id"
                      placeholder="suggestion_abc123..."
                      value={prSuggestionId}
                      onChange={(e) => setPrSuggestionId(e.target.value)}
                      className="bg-black/50 border-cyan-500/50 text-cyan-400 font-mono"
                      data-testid="input-pr-suggestion-id"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="pr-branch-name" className="text-cyan-400 font-mono">ブランチ名 (オプション)</Label>
                    <Input
                      id="pr-branch-name"
                      placeholder="feature/auto-fix..."
                      value={prBranchName}
                      onChange={(e) => setPrBranchName(e.target.value)}
                      className="bg-black/50 border-cyan-500/50 text-cyan-400 font-mono"
                      data-testid="input-pr-branch-name"
                    />
                  </div>
                </div>
                <Button 
                  onClick={handlePRGenerate}
                  disabled={prGenerateMutation.isPending}
                  className="w-full bg-purple-600 hover:bg-purple-700 font-mono"
                  data-testid="button-generate-pr"
                >
                  {prGenerateMutation.isPending ? "生成中..." : "🚀 PR自動生成"}
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="neon-card" data-testid="card-kbe-recommend">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-cyan-400 font-mono">
                  <Lightbulb className="w-5 h-5" />
                  KBE知識レコメンド
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="knowledge-query" className="text-cyan-400 font-mono">検索クエリ</Label>
                  <Input
                    id="knowledge-query"
                    placeholder="知識を検索..."
                    value={knowledgeQuery}
                    onChange={(e) => setKnowledgeQuery(e.target.value)}
                    className="bg-black/50 border-cyan-500/50 text-cyan-400 font-mono"
                    data-testid="input-knowledge-query"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="knowledge-category" className="text-cyan-400 font-mono">カテゴリ (オプション)</Label>
                  <Input
                    id="knowledge-category"
                    placeholder="カテゴリ..."
                    value={knowledgeCategory}
                    onChange={(e) => setKnowledgeCategory(e.target.value)}
                    className="bg-black/50 border-cyan-500/50 text-cyan-400 font-mono"
                    data-testid="input-knowledge-category"
                  />
                </div>
                <Button 
                  onClick={handleKnowledgeLookup}
                  disabled={knowledgeLookupMutation.isPending}
                  className="w-full bg-green-600 hover:bg-green-700 font-mono"
                  data-testid="button-lookup-knowledge"
                >
                  {knowledgeLookupMutation.isPending ? "検索中..." : "💡 知識検索"}
                </Button>
                
                {knowledgeLookupMutation.data && knowledgeLookupMutation.data.length > 0 && (
                  <ScrollArea className="h-[200px] w-full rounded-md border border-cyan-500/50 p-2 bg-black/50">
                    <div className="space-y-2">
                      {knowledgeLookupMutation.data.map((record, idx) => (
                        <div key={record.id} className="p-2 bg-cyan-900/20 rounded text-xs font-mono" data-testid={`knowledge-record-${idx}`}>
                          <div className="text-cyan-400 font-bold">{record.category}</div>
                          <div className="text-cyan-400/70 mt-1">{record.content.substring(0, 100)}...</div>
                          <Badge variant="outline" className="mt-1 text-xs">関連度: {(record.relevance_score * 100).toFixed(0)}%</Badge>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>

            <Card className="neon-card" data-testid="card-priorities">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-cyan-400 font-mono">
                  <Sparkles className="w-5 h-5" />
                  進化優先度
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[200px]">
                  <div className="space-y-2">
                    {topPriorities && topPriorities.length > 0 ? (
                      topPriorities.map((task, idx) => (
                        <div key={task.task_id} className="p-2 bg-purple-900/20 border border-purple-500/30 rounded text-xs font-mono" data-testid={`priority-task-${idx}`}>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">P{task.priority}</Badge>
                            <span className="text-purple-400">{task.category}</span>
                          </div>
                          <div className="text-cyan-400/70 mt-1">{task.description.substring(0, 80)}...</div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-cyan-400/50 font-mono text-sm" data-testid="text-no-priorities">
                        優先度タスクなし
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

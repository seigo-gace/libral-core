import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { 
  Shield, 
  Key, 
  Lock, 
  Unlock, 
  FileSignature, 
  CheckCircle, 
  AlertTriangle,
  Copy,
  Download
} from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface GPGHealthResponse {
  status: string;
  version: string;
  available_algorithms: {
    symmetric: string[];
    asymmetric: string[];
    hash: string[];
  };
  active_policy: string;
  policies: {
    [key: string]: {
      cipher: string;
      digest: string;
      compression: string;
    };
  };
}

interface GPGEncryptRequest {
  data: string;
  recipients: string[];
  policy: string;
  context_labels?: Record<string, string>;
}

interface GPGDecryptRequest {
  encrypted_data: string;
}

interface GPGSignRequest {
  data: string;
  context_labels?: Record<string, string>;
}

interface GPGVerifyRequest {
  signed_data: string;
}

interface GPGKeyGenRequest {
  user_id: string;
  key_type: string;
  key_length: number;
}

export default function GPGPage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  // Form states
  const [encryptData, setEncryptData] = useState("");
  const [recipients, setRecipients] = useState("");
  const [selectedPolicy, setSelectedPolicy] = useState("MODERN_STRONG");
  const [decryptData, setDecryptData] = useState("");
  const [signData, setSignData] = useState("");
  const [verifyData, setVerifyData] = useState("");
  const [userId, setUserId] = useState("");
  const [keyType, setKeyType] = useState("RSA");
  const [keyLength, setKeyLength] = useState(4096);
  
  // Results states
  const [encryptResult, setEncryptResult] = useState("");
  const [decryptResult, setDecryptResult] = useState("");
  const [signResult, setSignResult] = useState("");
  const [verifyResult, setVerifyResult] = useState("");

  // Fetch GPG health status
  const { data: healthData, isLoading: healthLoading } = useQuery<GPGHealthResponse>({
    queryKey: ['/api/v1/gpg/health'],
    queryFn: () => apiRequest('/api/v1/gpg/health')
  });

  // Mutations
  const encryptMutation = useMutation({
    mutationFn: (data: GPGEncryptRequest) => apiRequest('/api/v1/gpg/encrypt', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    onSuccess: (result) => {
      setEncryptResult(result.encrypted_data || JSON.stringify(result, null, 2));
      toast({ title: "暗号化完了", description: "データが正常に暗号化されました" });
    },
    onError: () => {
      toast({ title: "暗号化エラー", description: "暗号化に失敗しました", variant: "destructive" });
    }
  });

  const decryptMutation = useMutation({
    mutationFn: (data: GPGDecryptRequest) => apiRequest('/api/v1/gpg/decrypt', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    onSuccess: (result) => {
      setDecryptResult(result.decrypted_data || JSON.stringify(result, null, 2));
      toast({ title: "復号化完了", description: "データが正常に復号化されました" });
    },
    onError: () => {
      toast({ title: "復号化エラー", description: "復号化に失敗しました", variant: "destructive" });
    }
  });

  const signMutation = useMutation({
    mutationFn: (data: GPGSignRequest) => apiRequest('/api/v1/gpg/sign', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    onSuccess: (result) => {
      setSignResult(result.signed_data || JSON.stringify(result, null, 2));
      toast({ title: "署名完了", description: "データが正常に署名されました" });
    },
    onError: () => {
      toast({ title: "署名エラー", description: "署名に失敗しました", variant: "destructive" });
    }
  });

  const verifyMutation = useMutation({
    mutationFn: (data: GPGVerifyRequest) => apiRequest('/api/v1/gpg/verify', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    onSuccess: (result) => {
      setVerifyResult(JSON.stringify(result, null, 2));
      toast({ title: "検証完了", description: "署名の検証が完了しました" });
    },
    onError: () => {
      toast({ title: "検証エラー", description: "署名の検証に失敗しました", variant: "destructive" });
    }
  });

  const keyGenMutation = useMutation({
    mutationFn: (data: GPGKeyGenRequest) => apiRequest('/api/v1/gpg/keys/generate', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    onSuccess: (result) => {
      toast({ title: "キー生成完了", description: "新しいGPGキーが生成されました" });
      queryClient.invalidateQueries({ queryKey: ['/api/v1/gpg/health'] });
    },
    onError: () => {
      toast({ title: "キー生成エラー", description: "キーの生成に失敗しました", variant: "destructive" });
    }
  });

  const handleEncrypt = () => {
    if (!encryptData.trim() || !recipients.trim()) {
      toast({ title: "入力エラー", description: "データと受信者を入力してください", variant: "destructive" });
      return;
    }
    
    encryptMutation.mutate({
      data: encryptData,
      recipients: recipients.split(',').map(r => r.trim()),
      policy: selectedPolicy,
      context_labels: {
        operation: "manual_encrypt",
        source: "libral_dashboard"
      }
    });
  };

  const handleDecrypt = () => {
    if (!decryptData.trim()) {
      toast({ title: "入力エラー", description: "暗号化データを入力してください", variant: "destructive" });
      return;
    }
    
    decryptMutation.mutate({
      encrypted_data: decryptData
    });
  };

  const handleSign = () => {
    if (!signData.trim()) {
      toast({ title: "入力エラー", description: "署名するデータを入力してください", variant: "destructive" });
      return;
    }
    
    signMutation.mutate({
      data: signData,
      context_labels: {
        operation: "manual_sign",
        source: "libral_dashboard"
      }
    });
  };

  const handleVerify = () => {
    if (!verifyData.trim()) {
      toast({ title: "入力エラー", description: "検証する署名データを入力してください", variant: "destructive" });
      return;
    }
    
    verifyMutation.mutate({
      signed_data: verifyData
    });
  };

  const handleKeyGen = () => {
    if (!userId.trim()) {
      toast({ title: "入力エラー", description: "ユーザーIDを入力してください", variant: "destructive" });
      return;
    }
    
    keyGenMutation.mutate({
      user_id: userId,
      key_type: keyType,
      key_length: keyLength
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({ title: "コピー完了", description: "クリップボードにコピーされました" });
  };

  if (healthLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Shield className="h-12 w-12 text-primary mx-auto mb-4 animate-pulse" />
          <p className="text-dark-400">GPGモジュールを読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold text-dark-50">Aegis-PGP 暗号化システム</h1>
          </div>
          <p className="text-dark-400">Enterprise-grade GPG暗号化、署名、キー管理システム</p>
        </div>

        {/* System Status */}
        <Card className="mb-8 bg-dark-800 border-dark-700">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-dark-50">
              <CheckCircle className="h-5 w-5 text-success" />
              <span>システム状態</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {healthData ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <Label className="text-dark-300">ステータス</Label>
                  <Badge variant="secondary" className="mt-1 bg-success/20 text-success">
                    {healthData.status}
                  </Badge>
                </div>
                <div>
                  <Label className="text-dark-300">アクティブポリシー</Label>
                  <Badge variant="outline" className="mt-1 text-dark-200">
                    {healthData.active_policy}
                  </Badge>
                </div>
                <div>
                  <Label className="text-dark-300">バージョン</Label>
                  <p className="text-dark-50 mt-1">{healthData.version}</p>
                </div>
              </div>
            ) : (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  GPGシステムの状態を取得できませんでした。
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Main Operations */}
        <Tabs defaultValue="encrypt" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-dark-800">
            <TabsTrigger value="encrypt" className="data-[state=active]:bg-dark-700">
              <Lock className="h-4 w-4 mr-2" />
              暗号化
            </TabsTrigger>
            <TabsTrigger value="decrypt" className="data-[state=active]:bg-dark-700">
              <Unlock className="h-4 w-4 mr-2" />
              復号化
            </TabsTrigger>
            <TabsTrigger value="sign" className="data-[state=active]:bg-dark-700">
              <FileSignature className="h-4 w-4 mr-2" />
              署名
            </TabsTrigger>
            <TabsTrigger value="verify" className="data-[state=active]:bg-dark-700">
              <CheckCircle className="h-4 w-4 mr-2" />
              検証
            </TabsTrigger>
            <TabsTrigger value="keygen" className="data-[state=active]:bg-dark-700">
              <Key className="h-4 w-4 mr-2" />
              キー生成
            </TabsTrigger>
          </TabsList>

          {/* Encrypt Tab */}
          <TabsContent value="encrypt">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-dark-800 border-dark-700">
                <CardHeader>
                  <CardTitle className="text-dark-50">データ暗号化</CardTitle>
                  <CardDescription className="text-dark-400">
                    テキストデータをGPGで暗号化します
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="encrypt-data" className="text-dark-300">暗号化するデータ</Label>
                    <Textarea
                      id="encrypt-data"
                      value={encryptData}
                      onChange={(e) => setEncryptData(e.target.value)}
                      placeholder="暗号化したいテキストを入力..."
                      className="mt-1 bg-dark-700 border-dark-600 text-dark-50"
                      rows={4}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="recipients" className="text-dark-300">受信者 (カンマ区切り)</Label>
                    <Input
                      id="recipients"
                      value={recipients}
                      onChange={(e) => setRecipients(e.target.value)}
                      placeholder="user@example.com, admin@company.com"
                      className="mt-1 bg-dark-700 border-dark-600 text-dark-50"
                    />
                  </div>

                  <div>
                    <Label className="text-dark-300">暗号化ポリシー</Label>
                    <Select value={selectedPolicy} onValueChange={setSelectedPolicy}>
                      <SelectTrigger className="mt-1 bg-dark-700 border-dark-600 text-dark-50">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-dark-700 border-dark-600">
                        <SelectItem value="MODERN_STRONG">Modern Strong (AES-256-OCB)</SelectItem>
                        <SelectItem value="COMPATIBILITY">Compatibility (AES-128)</SelectItem>
                        <SelectItem value="BACKUP_LONGTERM">Backup Longterm (AES-256)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Button 
                    onClick={handleEncrypt}
                    disabled={encryptMutation.isPending}
                    className="w-full"
                    data-testid="button-encrypt"
                  >
                    <Lock className="h-4 w-4 mr-2" />
                    {encryptMutation.isPending ? "暗号化中..." : "暗号化実行"}
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-dark-800 border-dark-700">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between text-dark-50">
                    暗号化結果
                    {encryptResult && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(encryptResult)}
                        className="border-dark-600 text-dark-300"
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Textarea
                    value={encryptResult}
                    readOnly
                    placeholder="暗号化されたデータがここに表示されます..."
                    className="bg-dark-700 border-dark-600 text-dark-50 min-h-[200px]"
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Decrypt Tab */}
          <TabsContent value="decrypt">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-dark-800 border-dark-700">
                <CardHeader>
                  <CardTitle className="text-dark-50">データ復号化</CardTitle>
                  <CardDescription className="text-dark-400">
                    GPGで暗号化されたデータを復号化します
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="decrypt-data" className="text-dark-300">暗号化されたデータ</Label>
                    <Textarea
                      id="decrypt-data"
                      value={decryptData}
                      onChange={(e) => setDecryptData(e.target.value)}
                      placeholder="GPGで暗号化されたデータを貼り付け..."
                      className="mt-1 bg-dark-700 border-dark-600 text-dark-50"
                      rows={6}
                    />
                  </div>

                  <Button 
                    onClick={handleDecrypt}
                    disabled={decryptMutation.isPending}
                    className="w-full"
                    data-testid="button-decrypt"
                  >
                    <Unlock className="h-4 w-4 mr-2" />
                    {decryptMutation.isPending ? "復号化中..." : "復号化実行"}
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-dark-800 border-dark-700">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between text-dark-50">
                    復号化結果
                    {decryptResult && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(decryptResult)}
                        className="border-dark-600 text-dark-300"
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Textarea
                    value={decryptResult}
                    readOnly
                    placeholder="復号化されたデータがここに表示されます..."
                    className="bg-dark-700 border-dark-600 text-dark-50 min-h-[200px]"
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Sign Tab */}
          <TabsContent value="sign">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-dark-800 border-dark-700">
                <CardHeader>
                  <CardTitle className="text-dark-50">データ署名</CardTitle>
                  <CardDescription className="text-dark-400">
                    データにGPGデジタル署名を追加します
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="sign-data" className="text-dark-300">署名するデータ</Label>
                    <Textarea
                      id="sign-data"
                      value={signData}
                      onChange={(e) => setSignData(e.target.value)}
                      placeholder="署名したいテキストを入力..."
                      className="mt-1 bg-dark-700 border-dark-600 text-dark-50"
                      rows={4}
                    />
                  </div>

                  <Button 
                    onClick={handleSign}
                    disabled={signMutation.isPending}
                    className="w-full"
                    data-testid="button-sign"
                  >
                    <FileSignature className="h-4 w-4 mr-2" />
                    {signMutation.isPending ? "署名中..." : "署名実行"}
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-dark-800 border-dark-700">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between text-dark-50">
                    署名結果
                    {signResult && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(signResult)}
                        className="border-dark-600 text-dark-300"
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Textarea
                    value={signResult}
                    readOnly
                    placeholder="署名されたデータがここに表示されます..."
                    className="bg-dark-700 border-dark-600 text-dark-50 min-h-[200px]"
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Verify Tab */}
          <TabsContent value="verify">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-dark-800 border-dark-700">
                <CardHeader>
                  <CardTitle className="text-dark-50">署名検証</CardTitle>
                  <CardDescription className="text-dark-400">
                    GPGデジタル署名の有効性を検証します
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="verify-data" className="text-dark-300">署名されたデータ</Label>
                    <Textarea
                      id="verify-data"
                      value={verifyData}
                      onChange={(e) => setVerifyData(e.target.value)}
                      placeholder="検証したい署名データを貼り付け..."
                      className="mt-1 bg-dark-700 border-dark-600 text-dark-50"
                      rows={6}
                    />
                  </div>

                  <Button 
                    onClick={handleVerify}
                    disabled={verifyMutation.isPending}
                    className="w-full"
                    data-testid="button-verify"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    {verifyMutation.isPending ? "検証中..." : "署名検証"}
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-dark-800 border-dark-700">
                <CardHeader>
                  <CardTitle className="text-dark-50">検証結果</CardTitle>
                </CardHeader>
                <CardContent>
                  <Textarea
                    value={verifyResult}
                    readOnly
                    placeholder="署名検証結果がここに表示されます..."
                    className="bg-dark-700 border-dark-600 text-dark-50 min-h-[200px]"
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Key Generation Tab */}
          <TabsContent value="keygen">
            <Card className="bg-dark-800 border-dark-700 max-w-2xl mx-auto">
              <CardHeader>
                <CardTitle className="text-dark-50">GPGキー生成</CardTitle>
                <CardDescription className="text-dark-400">
                  新しいGPGキーペアを生成します
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="user-id" className="text-dark-300">ユーザーID (名前 &lt;email@example.com&gt;)</Label>
                  <Input
                    id="user-id"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="John Doe <john@example.com>"
                    className="mt-1 bg-dark-700 border-dark-600 text-dark-50"
                  />
                </div>

                <div>
                  <Label className="text-dark-300">キータイプ</Label>
                  <Select value={keyType} onValueChange={setKeyType}>
                    <SelectTrigger className="mt-1 bg-dark-700 border-dark-600 text-dark-50">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-dark-700 border-dark-600">
                      <SelectItem value="RSA">RSA</SelectItem>
                      <SelectItem value="ED25519">ED25519</SelectItem>
                      <SelectItem value="ECDSA">ECDSA</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-dark-300">キー長</Label>
                  <Select value={keyLength.toString()} onValueChange={(v) => setKeyLength(parseInt(v))}>
                    <SelectTrigger className="mt-1 bg-dark-700 border-dark-600 text-dark-50">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-dark-700 border-dark-600">
                      <SelectItem value="2048">2048 bits</SelectItem>
                      <SelectItem value="4096">4096 bits</SelectItem>
                      <SelectItem value="8192">8192 bits</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  onClick={handleKeyGen}
                  disabled={keyGenMutation.isPending}
                  className="w-full"
                  data-testid="button-keygen"
                >
                  <Key className="h-4 w-4 mr-2" />
                  {keyGenMutation.isPending ? "キー生成中..." : "キーペア生成"}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
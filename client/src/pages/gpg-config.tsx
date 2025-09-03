import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FuturisticCard } from "@/components/ui/futuristic-card";
import { Shield, Key, Lock, Upload, Download, Copy, CheckCircle, AlertCircle } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";

interface GpgKey {
  keyId: string;
  keyType: string;
  userId: string;
  fingerprint: string;
  createdAt: string;
  expiresAt: string;
  status: 'active' | 'expired' | 'revoked';
}

interface EncryptionPolicy {
  name: string;
  description: string;
  algorithms: string[];
  securityLevel: 'high' | 'medium' | 'low';
}

const encryptionPolicies: EncryptionPolicy[] = [
  {
    name: 'Modern Strong',
    description: 'SEIPDv2/AES-256-OCB - 最新の企業級暗号化',
    algorithms: ['AES-256-OCB', 'EdDSA', 'Curve25519'],
    securityLevel: 'high'
  },
  {
    name: 'Compatible',
    description: 'AES-256-GCM - 幅広い互換性',
    algorithms: ['AES-256-GCM', 'RSA-4096', 'SHA-256'],
    securityLevel: 'medium'
  },
  {
    name: 'Backup Longterm',
    description: 'RSA-4096 - 長期保存用',
    algorithms: ['RSA-4096', 'AES-256-CFB', 'SHA-512'],
    securityLevel: 'medium'
  }
];

export default function GpgConfig() {
  const [selectedPolicy, setSelectedPolicy] = useState<string>('Modern Strong');
  const [newKeyData, setNewKeyData] = useState({
    name: '',
    email: '',
    comment: '',
    passphrase: ''
  });

  const queryClient = useQueryClient();

  const { data: keys = [] } = useQuery<GpgKey[]>({
    queryKey: ['/api/aegis/keys'],
    queryFn: async () => {
      // Mock data for now
      return [
        {
          keyId: 'F1B2C3D4E5F6G7H8',
          keyType: 'EdDSA',
          userId: 'Libral Admin <admin@libral.core>',
          fingerprint: 'F1B2 C3D4 E5F6 G7H8 I9J0 K1L2 M3N4 O5P6 Q7R8 S9T0',
          createdAt: '2024-01-01',
          expiresAt: '2026-01-01',
          status: 'active'
        }
      ];
    }
  });

  const encryptMutation = useMutation({
    mutationFn: async (data: { text: string; keyId: string; policy: string }) => {
      return apiRequest(`/api/aegis/encrypt`, 'POST', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/aegis/operations'] });
    }
  });

  const generateKeyMutation = useMutation({
    mutationFn: async (keyData: typeof newKeyData & { policy: string }) => {
      return apiRequest(`/api/aegis/keys/generate`, 'POST', keyData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/aegis/keys'] });
      setNewKeyData({ name: '', email: '', comment: '', passphrase: '' });
    }
  });

  const getPolicyBadge = (policy: string) => {
    const policyObj = encryptionPolicies.find(p => p.name === policy);
    if (!policyObj) return null;
    
    const colorMap = {
      high: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      low: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    };

    return (
      <Badge className={colorMap[policyObj.securityLevel]}>
        {policyObj.securityLevel.toUpperCase()}
      </Badge>
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'expired': return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'revoked': return <AlertCircle className="h-4 w-4 text-red-500" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="container mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-400" />
              <span>Aegis-PGP 暗号化設定</span>
            </h1>
            <p className="text-blue-200/80 mt-2">
              エンタープライズ級GPG暗号化システムの設定と管理
            </p>
          </div>
          <Button 
            onClick={() => window.location.href = '/admin-dashboard'}
            variant="outline"
            className="text-white border-white/20 hover:bg-white/10"
          >
            戻る
          </Button>
        </div>

        <Tabs defaultValue="keys" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white/5 backdrop-blur-sm">
            <TabsTrigger value="keys">キー管理</TabsTrigger>
            <TabsTrigger value="encrypt">暗号化</TabsTrigger>
            <TabsTrigger value="policies">ポリシー</TabsTrigger>
            <TabsTrigger value="settings">設定</TabsTrigger>
          </TabsList>

          {/* Key Management */}
          <TabsContent value="keys" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Existing Keys */}
              <FuturisticCard glowColor="blue" active={true}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-white">
                    <Key className="h-5 w-5" />
                    <span>登録済みキー</span>
                  </CardTitle>
                  <CardDescription className="text-blue-200/80">
                    現在登録されているGPGキー一覧
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {keys.map((key) => (
                    <div key={key.keyId} className="p-4 bg-white/5 rounded-lg border border-white/10">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(key.status)}
                          <span className="font-mono text-sm text-white">{key.keyId}</span>
                        </div>
                        <Badge variant="outline">{key.keyType}</Badge>
                      </div>
                      <div className="text-sm text-gray-300 space-y-1">
                        <div>User: {key.userId}</div>
                        <div className="font-mono text-xs break-all">
                          Fingerprint: {key.fingerprint}
                        </div>
                        <div className="flex justify-between">
                          <span>作成: {key.createdAt}</span>
                          <span>期限: {key.expiresAt}</span>
                        </div>
                      </div>
                      <div className="flex space-x-2 mt-3">
                        <Button variant="outline" size="sm">
                          <Download className="h-3 w-3 mr-1" />
                          エクスポート
                        </Button>
                        <Button variant="outline" size="sm">
                          <Copy className="h-3 w-3 mr-1" />
                          コピー
                        </Button>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </FuturisticCard>

              {/* Generate New Key */}
              <FuturisticCard glowColor="green" active={true}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-white">
                    <Key className="h-5 w-5" />
                    <span>新しいキーの生成</span>
                  </CardTitle>
                  <CardDescription className="text-green-200/80">
                    新しいGPGキーペアを生成します
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-white">名前</Label>
                    <Input
                      id="name"
                      value={newKeyData.name}
                      onChange={(e) => setNewKeyData({ ...newKeyData, name: e.target.value })}
                      placeholder="Your Name"
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-white">メールアドレス</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newKeyData.email}
                      onChange={(e) => setNewKeyData({ ...newKeyData, email: e.target.value })}
                      placeholder="your.email@example.com"
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="comment" className="text-white">コメント（オプション）</Label>
                    <Input
                      id="comment"
                      value={newKeyData.comment}
                      onChange={(e) => setNewKeyData({ ...newKeyData, comment: e.target.value })}
                      placeholder="Key usage description"
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="passphrase" className="text-white">パスフレーズ</Label>
                    <Input
                      id="passphrase"
                      type="password"
                      value={newKeyData.passphrase}
                      onChange={(e) => setNewKeyData({ ...newKeyData, passphrase: e.target.value })}
                      placeholder="Strong passphrase"
                      className="bg-white/5 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-white">暗号化ポリシー</Label>
                    <Select value={selectedPolicy} onValueChange={setSelectedPolicy}>
                      <SelectTrigger className="bg-white/5 border-white/20 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {encryptionPolicies.map((policy) => (
                          <SelectItem key={policy.name} value={policy.name}>
                            <div className="flex items-center justify-between w-full">
                              <span>{policy.name}</span>
                              {getPolicyBadge(policy.name)}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <Button 
                    onClick={() => generateKeyMutation.mutate({ ...newKeyData, policy: selectedPolicy })}
                    disabled={generateKeyMutation.isPending || !newKeyData.name || !newKeyData.email}
                    className="w-full"
                    data-testid="button-generate-key"
                  >
                    {generateKeyMutation.isPending ? '生成中...' : 'キーペアを生成'}
                  </Button>
                </CardContent>
              </FuturisticCard>
            </div>
          </TabsContent>

          {/* Encryption Tool */}
          <TabsContent value="encrypt" className="space-y-6">
            <FuturisticCard glowColor="purple" active={true}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Lock className="h-5 w-5" />
                  <span>暗号化ツール</span>
                </CardTitle>
                <CardDescription className="text-purple-200/80">
                  テキストや文書を暗号化します
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-white">暗号化するテキスト</Label>
                  <Textarea
                    placeholder="暗号化したいテキストを入力してください..."
                    className="bg-white/5 border-white/20 text-white min-h-[150px]"
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-white">受信者のキー</Label>
                    <Select>
                      <SelectTrigger className="bg-white/5 border-white/20 text-white">
                        <SelectValue placeholder="キーを選択" />
                      </SelectTrigger>
                      <SelectContent>
                        {keys.map((key) => (
                          <SelectItem key={key.keyId} value={key.keyId}>
                            {key.userId} ({key.keyId})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-white">暗号化ポリシー</Label>
                    <Select value={selectedPolicy} onValueChange={setSelectedPolicy}>
                      <SelectTrigger className="bg-white/5 border-white/20 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {encryptionPolicies.map((policy) => (
                          <SelectItem key={policy.name} value={policy.name}>
                            {policy.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button 
                  className="w-full"
                  disabled={encryptMutation.isPending}
                  data-testid="button-encrypt-text"
                >
                  {encryptMutation.isPending ? '暗号化中...' : '暗号化'}
                </Button>
              </CardContent>
            </FuturisticCard>
          </TabsContent>

          {/* Policies */}
          <TabsContent value="policies" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {encryptionPolicies.map((policy) => (
                <FuturisticCard 
                  key={policy.name} 
                  glowColor={policy.securityLevel === 'high' ? 'green' : policy.securityLevel === 'medium' ? 'yellow' : 'red'} 
                  active={selectedPolicy === policy.name}
                >
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between text-white">
                      <span>{policy.name}</span>
                      {getPolicyBadge(policy.name)}
                    </CardTitle>
                    <CardDescription className="text-gray-300">
                      {policy.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <h4 className="font-medium text-white mb-2">アルゴリズム:</h4>
                      <div className="flex flex-wrap gap-2">
                        {policy.algorithms.map((algo) => (
                          <Badge key={algo} variant="outline" className="text-xs">
                            {algo}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <Button 
                      variant={selectedPolicy === policy.name ? "default" : "outline"}
                      className="w-full"
                      onClick={() => setSelectedPolicy(policy.name)}
                      data-testid={`button-select-policy-${policy.name.toLowerCase().replace(' ', '-')}`}
                    >
                      {selectedPolicy === policy.name ? '選択中' : '選択'}
                    </Button>
                  </CardContent>
                </FuturisticCard>
              ))}
            </div>
          </TabsContent>

          {/* Settings */}
          <TabsContent value="settings" className="space-y-6">
            <FuturisticCard glowColor="blue" active={true}>
              <CardHeader>
                <CardTitle className="text-white">システム設定</CardTitle>
                <CardDescription className="text-blue-200/80">
                  Aegis-PGPシステムの設定を管理します
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="font-medium text-white">セキュリティ設定</h3>
                    <div className="space-y-2">
                      <Label className="text-white">キーの自動期限切れ</Label>
                      <Select defaultValue="2-years">
                        <SelectTrigger className="bg-white/5 border-white/20 text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1-year">1年</SelectItem>
                          <SelectItem value="2-years">2年</SelectItem>
                          <SelectItem value="5-years">5年</SelectItem>
                          <SelectItem value="never">無期限</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="font-medium text-white">バックアップ設定</h3>
                    <div className="space-y-2">
                      <Button variant="outline" className="w-full">
                        <Download className="h-4 w-4 mr-2" />
                        キーリングをバックアップ
                      </Button>
                      <Button variant="outline" className="w-full">
                        <Upload className="h-4 w-4 mr-2" />
                        バックアップから復元
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </FuturisticCard>
          </TabsContent>
        </Tabs>

      </div>
    </div>
  );
}
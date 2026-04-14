import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { CheckCircle, Clock, AlertCircle, CreditCard, Star, Smartphone, Loader2 } from "lucide-react";

interface PaymentProcessorProps {
  method: string;
  amount: number;
  currency: string;
  onSuccess: (transactionId: string) => void;
  onError: (error: string) => void;
  onCancel: () => void;
}

export default function PaymentProcessor({ method, amount, currency, onSuccess, onError, onCancel }: PaymentProcessorProps) {
  const [processing, setProcessing] = useState(false);
  const [step, setStep] = useState<'input' | 'processing' | 'completed'>('input');
  const [paymentData, setPaymentData] = useState<any>({});

  const formatCurrency = (value: number) => {
    if (currency === 'JPY') {
      return `¥${value.toLocaleString()}`;
    }
    if (currency === 'STARS') {
      return `${value} ⭐`;
    }
    return `$${value.toFixed(2)}`;
  };

  const processPayment = async () => {
    setProcessing(true);
    setStep('processing');

    try {
      // シミュレート決済処理
      await new Promise(resolve => setTimeout(resolve, 2000));

      const transactionId = `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      setStep('completed');
      setTimeout(() => {
        onSuccess(transactionId);
      }, 1500);
    } catch (error) {
      onError('決済処理中にエラーが発生しました。もう一度お試しください。');
    } finally {
      setProcessing(false);
    }
  };

  const renderPaymentForm = () => {
    switch (method) {
      case 'telegram_stars':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Star className="h-5 w-5 text-yellow-500" />
                <span>Telegram Stars決済</span>
              </CardTitle>
              <CardDescription>
                Telegramアプリ内でStarsを使用して決済します
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <Star className="h-4 w-4" />
                <AlertDescription>
                  <strong>ご注意:</strong> この決済はTelegramアプリ内で完了します。
                  決済ボタンをクリックすると、Telegramアプリが開きます。
                </AlertDescription>
              </Alert>
              
              <div className="space-y-2">
                <Label>必要なStars数</Label>
                <div className="flex items-center space-x-2">
                  <Input value={`${amount} ⭐`} readOnly />
                  <Badge>即座決済</Badge>
                </div>
              </div>

              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h4 className="font-medium mb-2">Telegram Stars決済の流れ:</h4>
                <ol className="text-sm space-y-1 list-decimal list-inside">
                  <li>「決済を開始」ボタンをクリック</li>
                  <li>Telegramアプリが自動で開きます</li>
                  <li>Stars残高を確認して決済を承認</li>
                  <li>決済完了後、自動でこちらに戻ります</li>
                </ol>
              </div>
            </CardContent>
          </Card>
        );

      case 'paypay':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Smartphone className="h-5 w-5 text-red-500" />
                <span>PayPay決済</span>
              </CardTitle>
              <CardDescription>
                PayPayアプリまたはQRコードで決済します
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <Smartphone className="h-4 w-4" />
                <AlertDescription>
                  <strong>PayPayアプリ必須:</strong> 決済にはPayPayアプリのインストールが必要です。
                  アプリをお持ちでない場合は、先にダウンロードしてください。
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label>決済金額</Label>
                <Input value={formatCurrency(amount)} readOnly />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 border rounded-lg text-center">
                  <Smartphone className="h-8 w-8 mx-auto mb-2 text-red-500" />
                  <div className="text-sm font-medium">PayPayアプリ</div>
                  <div className="text-xs text-gray-500">アプリ連携</div>
                </div>
                <div className="p-3 border rounded-lg text-center">
                  <div className="w-8 h-8 mx-auto mb-2 bg-gray-200 rounded border-2 border-dashed"></div>
                  <div className="text-sm font-medium">QRコード</div>
                  <div className="text-xs text-gray-500">カメラ読取</div>
                </div>
              </div>

              <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <h4 className="font-medium mb-2">PayPay決済の流れ:</h4>
                <ol className="text-sm space-y-1 list-decimal list-inside">
                  <li>「決済を開始」ボタンをクリック</li>
                  <li>PayPayアプリが開きます（またはQRコード表示）</li>
                  <li>PayPay残高またはクレジットカードを選択</li>
                  <li>決済を承認して完了</li>
                </ol>
              </div>
            </CardContent>
          </Card>
        );

      case 'paypal':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CreditCard className="h-5 w-5 text-blue-600" />
                <span>PayPal決済</span>
              </CardTitle>
              <CardDescription>
                PayPalアカウントまたはクレジットカードで決済
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>決済金額</Label>
                <Input value={formatCurrency(amount)} readOnly />
              </div>

              <Alert>
                <CreditCard className="h-4 w-4" />
                <AlertDescription>
                  PayPalアカウントをお持ちでない場合も、ゲスト決済でクレジットカードが使用できます。
                </AlertDescription>
              </Alert>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 border rounded-lg text-center">
                  <div className="w-8 h-8 mx-auto mb-2 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                    PP
                  </div>
                  <div className="text-sm font-medium">PayPalアカウント</div>
                  <div className="text-xs text-gray-500">ワンクリック決済</div>
                </div>
                <div className="p-3 border rounded-lg text-center">
                  <CreditCard className="h-8 w-8 mx-auto mb-2 text-gray-600" />
                  <div className="text-sm font-medium">ゲスト決済</div>
                  <div className="text-xs text-gray-500">カード直接入力</div>
                </div>
              </div>
            </CardContent>
          </Card>
        );

      case 'credit_card':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CreditCard className="h-5 w-5 text-gray-600" />
                <span>クレジットカード決済</span>
              </CardTitle>
              <CardDescription>
                Visa、Mastercard、JCB、American Express対応
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cardNumber">カード番号</Label>
                <Input 
                  id="cardNumber"
                  placeholder="1234 5678 9012 3456"
                  value={paymentData.cardNumber || ''}
                  onChange={(e) => setPaymentData({...paymentData, cardNumber: e.target.value})}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="expiry">有効期限</Label>
                  <Input 
                    id="expiry"
                    placeholder="MM/YY"
                    value={paymentData.expiry || ''}
                    onChange={(e) => setPaymentData({...paymentData, expiry: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cvv">セキュリティコード</Label>
                  <Input 
                    id="cvv"
                    placeholder="123"
                    value={paymentData.cvv || ''}
                    onChange={(e) => setPaymentData({...paymentData, cvv: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="name">カード名義人</Label>
                <Input 
                  id="name"
                  placeholder="TARO YAMADA"
                  value={paymentData.name || ''}
                  onChange={(e) => setPaymentData({...paymentData, name: e.target.value})}
                />
              </div>

              <Alert>
                <CreditCard className="h-4 w-4" />
                <AlertDescription>
                  <strong>安全保証:</strong> カード情報は最高レベルのSSL暗号化で保護され、
                  当サイトには保存されません。
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  const renderProcessingStep = () => (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-8 space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
        <div className="text-center">
          <h3 className="text-lg font-medium">決済処理中...</h3>
          <p className="text-gray-600 mt-1">
            しばらくお待ちください。ページを閉じないでください。
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Clock className="h-4 w-4" />
          <span>通常1-2分で完了します</span>
        </div>
      </CardContent>
    </Card>
  );

  const renderCompletedStep = () => (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-8 space-y-4">
        <CheckCircle className="h-16 w-16 text-green-600" />
        <div className="text-center">
          <h3 className="text-xl font-bold text-green-600">決済完了！</h3>
          <p className="text-gray-600 mt-2">
            お支払いが正常に処理されました。
          </p>
        </div>
        <Badge className="bg-green-100 text-green-800">
          決済成功
        </Badge>
      </CardContent>
    </Card>
  );

  if (step === 'processing') {
    return renderProcessingStep();
  }

  if (step === 'completed') {
    return renderCompletedStep();
  }

  return (
    <div className="space-y-6">
      {renderPaymentForm()}

      <Separator />

      <div className="flex space-x-3">
        <Button
          variant="outline"
          onClick={onCancel}
          className="flex-1"
          data-testid="button-cancel-payment"
        >
          キャンセル
        </Button>
        <Button
          onClick={processPayment}
          disabled={processing}
          className="flex-1"
          data-testid="button-start-payment"
        >
          {processing ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              処理中...
            </>
          ) : (
            '決済を開始'
          )}
        </Button>
      </div>

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          <strong>お困りの際は:</strong> 決済で問題が発生した場合は、
          サポートまでお気軽にお問い合わせください。24時間以内にご対応いたします。
        </AlertDescription>
      </Alert>
    </div>
  );
}
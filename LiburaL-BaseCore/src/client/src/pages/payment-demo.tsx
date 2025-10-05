import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import PaymentSelector from "@/components/payment/PaymentSelector";
import PaymentProcessor from "@/components/payment/PaymentProcessor";
import { ArrowLeft, ShoppingCart, CheckCircle } from "lucide-react";

type DemoStep = 'setup' | 'select' | 'process' | 'completed';

export default function PaymentDemo() {
  const [step, setStep] = useState<DemoStep>('setup');
  const [amount, setAmount] = useState<number>(1000);
  const [currency, setCurrency] = useState<string>('JPY');
  const [selectedMethod, setSelectedMethod] = useState<string>('');
  const [transactionId, setTransactionId] = useState<string>('');

  const handleAmountChange = (value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue > 0) {
      setAmount(numValue);
    }
  };

  const handleMethodSelect = (methodId: string) => {
    setSelectedMethod(methodId);
  };

  const handleProceedToPayment = () => {
    setStep('process');
  };

  const handlePaymentSuccess = (txId: string) => {
    setTransactionId(txId);
    setStep('completed');
  };

  const handlePaymentError = (error: string) => {
    console.error('Payment error:', error);
    alert(`決済エラー: ${error}`);
    setStep('select');
  };

  const handleCancel = () => {
    if (step === 'process') {
      setStep('select');
    } else {
      setStep('setup');
    }
  };

  const resetDemo = () => {
    setStep('setup');
    setAmount(1000);
    setCurrency('JPY');
    setSelectedMethod('');
    setTransactionId('');
  };

  const renderSetupStep = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <ShoppingCart className="h-5 w-5" />
          <span>決済デモ - 商品設定</span>
        </CardTitle>
        <CardDescription>
          決済システムのテストを行います。金額と通貨を設定してください。
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="amount">決済金額</Label>
          <Input
            id="amount"
            type="number"
            value={amount}
            onChange={(e) => handleAmountChange(e.target.value)}
            min="1"
            step="1"
            data-testid="input-demo-amount"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="currency">通貨</Label>
          <Select value={currency} onValueChange={setCurrency}>
            <SelectTrigger data-testid="select-demo-currency">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="JPY">日本円 (¥)</SelectItem>
              <SelectItem value="USD">米ドル ($)</SelectItem>
              <SelectItem value="STARS">Telegram Stars (⭐)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Alert>
          <ShoppingCart className="h-4 w-4" />
          <AlertDescription>
            <strong>デモ環境:</strong> これはテスト環境です。実際の決済は行われません。
            すべての決済方法の動作を安全に確認できます。
          </AlertDescription>
        </Alert>

        <Button 
          onClick={() => setStep('select')} 
          className="w-full"
          data-testid="button-proceed-to-payment"
        >
          決済方法を選択
        </Button>
      </CardContent>
    </Card>
  );

  const renderCompletedStep = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2 text-green-600">
          <CheckCircle className="h-5 w-5" />
          <span>決済完了</span>
        </CardTitle>
        <CardDescription>
          決済が正常に完了しました
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg space-y-2">
          <div className="flex justify-between">
            <span>取引ID:</span>
            <span className="font-mono text-sm">{transactionId}</span>
          </div>
          <div className="flex justify-between">
            <span>決済方法:</span>
            <span className="capitalize">{selectedMethod.replace('_', ' ')}</span>
          </div>
          <div className="flex justify-between">
            <span>金額:</span>
            <span className="font-bold">
              {currency === 'JPY' ? `¥${amount.toLocaleString()}` : 
               currency === 'STARS' ? `${amount} ⭐` : 
               `$${amount.toFixed(2)}`}
            </span>
          </div>
          <div className="flex justify-between">
            <span>ステータス:</span>
            <span className="text-green-600 font-medium">成功</span>
          </div>
        </div>

        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>テスト完了:</strong> 決済システムが正常に動作していることが確認されました。
            実際の決済では、この流れで安全にお支払いが処理されます。
          </AlertDescription>
        </Alert>

        <Button onClick={resetDemo} className="w-full" data-testid="button-reset-demo">
          新しいテストを開始
        </Button>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">決済システムデモ</h1>
          <p className="text-muted-foreground">
            Telegram Stars、PayPay、PayPal対応決済システムのテスト
          </p>
        </div>
        {step !== 'setup' && (
          <Button variant="outline" onClick={handleCancel} data-testid="button-back">
            <ArrowLeft className="h-4 w-4 mr-2" />
            戻る
          </Button>
        )}
      </div>

      {/* ステップインジケーター */}
      <div className="flex items-center space-x-4">
        <div className={`flex items-center space-x-2 ${step === 'setup' ? 'text-blue-600' : step === 'select' || step === 'process' || step === 'completed' ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step === 'setup' ? 'bg-blue-100 text-blue-600' : step === 'select' || step === 'process' || step === 'completed' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
            1
          </div>
          <span className="text-sm font-medium">商品設定</span>
        </div>
        <div className={`w-8 h-0.5 ${step === 'select' || step === 'process' || step === 'completed' ? 'bg-green-600' : 'bg-gray-200'}`}></div>
        <div className={`flex items-center space-x-2 ${step === 'select' ? 'text-blue-600' : step === 'process' || step === 'completed' ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step === 'select' ? 'bg-blue-100 text-blue-600' : step === 'process' || step === 'completed' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
            2
          </div>
          <span className="text-sm font-medium">決済方法選択</span>
        </div>
        <div className={`w-8 h-0.5 ${step === 'process' || step === 'completed' ? 'bg-green-600' : 'bg-gray-200'}`}></div>
        <div className={`flex items-center space-x-2 ${step === 'process' ? 'text-blue-600' : step === 'completed' ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step === 'process' ? 'bg-blue-100 text-blue-600' : step === 'completed' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
            3
          </div>
          <span className="text-sm font-medium">決済処理</span>
        </div>
        <div className={`w-8 h-0.5 ${step === 'completed' ? 'bg-green-600' : 'bg-gray-200'}`}></div>
        <div className={`flex items-center space-x-2 ${step === 'completed' ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step === 'completed' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
            4
          </div>
          <span className="text-sm font-medium">完了</span>
        </div>
      </div>

      {/* ステップコンテンツ */}
      {step === 'setup' && renderSetupStep()}
      
      {step === 'select' && (
        <PaymentSelector
          amount={amount}
          currency={currency}
          onMethodSelect={handleMethodSelect}
          onProceed={handleProceedToPayment}
        />
      )}
      
      {step === 'process' && (
        <PaymentProcessor
          method={selectedMethod}
          amount={amount}
          currency={currency}
          onSuccess={handlePaymentSuccess}
          onError={handlePaymentError}
          onCancel={handleCancel}
        />
      )}
      
      {step === 'completed' && renderCompletedStep()}
    </div>
  );
}
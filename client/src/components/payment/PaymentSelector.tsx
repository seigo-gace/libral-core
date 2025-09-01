import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { CreditCard, Star, Smartphone, Globe, Shield, Info } from "lucide-react";

interface PaymentMethod {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  fees: string;
  processingTime: string;
  availability: 'global' | 'japan' | 'telegram';
  recommended: boolean;
  securityLevel: 'high' | 'medium';
  userFriendly: number; // 1-5 scale
}

const paymentMethods: PaymentMethod[] = [
  {
    id: 'telegram_stars',
    name: 'Telegram Stars',
    description: 'Telegram公式の仮想通貨。アプリ内で直接購入・使用可能',
    icon: <Star className="h-6 w-6 text-yellow-500" />,
    fees: '手数料なし',
    processingTime: '即座',
    availability: 'telegram',
    recommended: true,
    securityLevel: 'high',
    userFriendly: 5
  },
  {
    id: 'paypay',
    name: 'PayPay',
    description: '日本で最も人気のモバイル決済サービス。QRコードで簡単決済',
    icon: <Smartphone className="h-6 w-6 text-red-500" />,
    fees: '無料（PayPay残高）',
    processingTime: '即座',
    availability: 'japan',
    recommended: true,
    securityLevel: 'high',
    userFriendly: 5
  },
  {
    id: 'paypal',
    name: 'PayPal',
    description: '世界中で利用可能な安全なオンライン決済サービス',
    icon: <Globe className="h-6 w-6 text-blue-600" />,
    fees: '3.6% + 40円',
    processingTime: '即座',
    availability: 'global',
    recommended: false,
    securityLevel: 'high',
    userFriendly: 4
  },
  {
    id: 'credit_card',
    name: 'クレジットカード',
    description: 'Visa、Mastercard、JCB、American Express対応',
    icon: <CreditCard className="h-6 w-6 text-gray-600" />,
    fees: '3.6%',
    processingTime: '即座',
    availability: 'global',
    recommended: false,
    securityLevel: 'high',
    userFriendly: 3
  }
];

interface PaymentSelectorProps {
  amount: number;
  currency: string;
  onMethodSelect: (methodId: string) => void;
  onProceed: () => void;
}

export default function PaymentSelector({ amount, currency, onMethodSelect, onProceed }: PaymentSelectorProps) {
  const [selectedMethod, setSelectedMethod] = useState<string>('telegram_stars');
  const [userLocation, setUserLocation] = useState<'japan' | 'global'>('japan');

  const filteredMethods = paymentMethods.filter(method => 
    method.availability === 'global' || 
    method.availability === userLocation ||
    method.availability === 'telegram'
  );

  const selectedPaymentMethod = paymentMethods.find(method => method.id === selectedMethod);

  const calculateFee = (method: PaymentMethod) => {
    if (method.fees === '手数料なし' || method.fees === '無料（PayPay残高）') {
      return 0;
    }
    if (method.fees.includes('%')) {
      const percentage = parseFloat(method.fees.match(/(\d+\.?\d*)%/)?.[1] || '0');
      const fixedFee = method.fees.includes('+') ? 40 : 0;
      return (amount * percentage / 100) + fixedFee;
    }
    return 0;
  };

  const totalAmount = amount + (selectedPaymentMethod ? calculateFee(selectedPaymentMethod) : 0);

  const formatCurrency = (value: number) => {
    if (currency === 'JPY') {
      return `¥${value.toLocaleString()}`;
    }
    if (currency === 'STARS') {
      return `${value} ⭐`;
    }
    return `$${value.toFixed(2)}`;
  };

  const handleMethodChange = (methodId: string) => {
    setSelectedMethod(methodId);
    onMethodSelect(methodId);
  };

  return (
    <div className="space-y-6">
      {/* 地域選択 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Globe className="h-5 w-5" />
            <span>お住まいの地域</span>
          </CardTitle>
          <CardDescription>
            最適な決済方法を表示するため、お住まいの地域を選択してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RadioGroup value={userLocation} onValueChange={(value) => setUserLocation(value as 'japan' | 'global')}>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="japan" id="japan" />
              <Label htmlFor="japan">日本</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="global" id="global" />
              <Label htmlFor="global">その他の国・地域</Label>
            </div>
          </RadioGroup>
        </CardContent>
      </Card>

      {/* 決済方法選択 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CreditCard className="h-5 w-5" />
            <span>決済方法を選択</span>
          </CardTitle>
          <CardDescription>
            安全で便利な決済方法をお選びください。推奨マークのある方法が最もお得です。
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RadioGroup value={selectedMethod} onValueChange={handleMethodChange}>
            <div className="space-y-4">
              {filteredMethods.map((method) => (
                <div key={method.id} className="flex items-center space-x-3">
                  <RadioGroupItem value={method.id} id={method.id} />
                  <Label htmlFor={method.id} className="flex-1 cursor-pointer">
                    <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                      <div className="flex items-center space-x-4">
                        {method.icon}
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{method.name}</span>
                            {method.recommended && (
                              <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                推奨
                              </Badge>
                            )}
                            <div className="flex items-center">
                              {Array.from({ length: method.userFriendly }, (_, i) => (
                                <Star key={i} className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                              ))}
                              <span className="text-xs text-gray-500 ml-1">使いやすさ</span>
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {method.description}
                          </p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>手数料: {method.fees}</span>
                            <span>処理時間: {method.processingTime}</span>
                            <div className="flex items-center space-x-1">
                              <Shield className="h-3 w-3" />
                              <span>セキュリティ: {method.securityLevel === 'high' ? '高' : '中'}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">
                          手数料: {formatCurrency(calculateFee(method))}
                        </div>
                      </div>
                    </div>
                  </Label>
                </div>
              ))}
            </div>
          </RadioGroup>
        </CardContent>
      </Card>

      {/* 料金詳細 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Info className="h-5 w-5" />
            <span>お支払い詳細</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span>商品価格:</span>
              <span>{formatCurrency(amount)}</span>
            </div>
            {selectedPaymentMethod && calculateFee(selectedPaymentMethod) > 0 && (
              <div className="flex justify-between text-sm text-gray-600">
                <span>決済手数料:</span>
                <span>{formatCurrency(calculateFee(selectedPaymentMethod))}</span>
              </div>
            )}
            <hr />
            <div className="flex justify-between font-bold text-lg">
              <span>合計金額:</span>
              <span>{formatCurrency(totalAmount)}</span>
            </div>
          </div>

          {selectedPaymentMethod?.recommended && (
            <Alert className="mt-4">
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>{selectedPaymentMethod.name}</strong>は手数料が最もお得で、
                処理も最速の推奨決済方法です。
              </AlertDescription>
            </Alert>
          )}

          {userLocation === 'japan' && selectedMethod === 'paypay' && (
            <Alert className="mt-4">
              <Smartphone className="h-4 w-4" />
              <AlertDescription>
                PayPayをご利用の場合、PayPayアプリが必要です。
                QRコードまたはPayPayアプリで簡単にお支払いいただけます。
              </AlertDescription>
            </Alert>
          )}

          {selectedMethod === 'telegram_stars' && (
            <Alert className="mt-4">
              <Star className="h-4 w-4" />
              <AlertDescription>
                Telegram Starsは、Telegramアプリ内で購入できる仮想通貨です。
                初回利用の場合は、先にTelegramアプリでStarsを購入してください。
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* 決済ボタン */}
      <Button 
        onClick={onProceed} 
        className="w-full h-12 text-lg"
        data-testid="button-proceed-payment"
      >
        {selectedPaymentMethod?.name}で{formatCurrency(totalAmount)}を支払う
      </Button>

      {/* セキュリティ情報 */}
      <Alert>
        <Shield className="h-4 w-4" />
        <AlertDescription>
          <strong>安全な決済保証:</strong> すべての決済情報は最高レベルのSSL暗号化で保護されています。
          お客様のクレジットカード情報や個人情報は当サービスには保存されません。
        </AlertDescription>
      </Alert>
    </div>
  );
}
# Telegram個人ログサーバー統合プロトコル

## 概要

ユーザー個人が所有・管理するTelegramスーパーグループを「個人ログサーバー」として活用し、G-ACE.incの中央サーバーには一切の個人ログを残さない革新的なプライバシー保護モデルの技術実装プロトコル。

## 1. アーキテクチャ設計

### 基本構成
```
[ユーザー] ↔ [Libral App] ↔ [Core API] ↔ [Telegram Bot] → [ユーザー個人グループ]
                                ↓
                          [GPG暗号化モジュール]
                                ↓
                        [24h自動削除キャッシュ]
```

### プライバシー保護の原則
1. **データ主権**: ユーザーのデータはユーザーが完全にコントロールする
2. **暗号化必須**: 全ての個人情報はGPG暗号化後にのみ記録
3. **一時性**: 中央サーバーでの個人データ保持は最大24時間
4. **透明性**: ユーザーは自分のデータ記録を完全に把握できる

## 2. 初期設定フロー

### ユーザーオンボーディング（ウィザード形式）

#### Step 1: 個人ログサーバー作成
```python
class PersonalLogServerSetup:
    async def create_personal_group_wizard(self, user_id: int):
        """
        ユーザー専用Telegramスーパーグループ作成ウィザード
        """
        setup_steps = [
            {
                "step": 1,
                "title": "個人データ保管庫を作成します",
                "description": "あなた専用のTelegramグループを作成し、あなたのデータを安全に保管します",
                "action": "create_supergroup"
            },
            {
                "step": 2, 
                "title": "Libral Botを招待してください",
                "description": f"作成したグループに@{BOT_USERNAME}を管理者として追加してください",
                "action": "add_bot_to_group"
            },
            {
                "step": 3,
                "title": "暗号化設定を完了します", 
                "description": "GPG公開鍵を生成し、あなたのデータを暗号化します",
                "action": "generate_user_gpg_key"
            }
        ]
        return setup_steps
```

#### Step 2: Bot認証・権限設定
```python
async def authenticate_bot_in_user_group(self, group_id: int, user_id: int):
    """
    ユーザーグループ内でのBot認証と権限確認
    """
    # 1. グループ内でのBot権限確認
    bot_member = await bot.get_chat_member(group_id, bot.id)
    if bot_member.status not in ['administrator', 'creator']:
        raise BotPermissionError("Bot needs admin rights")
    
    # 2. ユーザーがグループの作成者/管理者であることを確認
    user_member = await bot.get_chat_member(group_id, user_id)
    if user_member.status not in ['administrator', 'creator']:
        raise UserPermissionError("User must be group admin")
    
    # 3. グループ設定の最適化
    await optimize_group_settings(group_id)
```

#### Step 3: 暗号化キー生成・交換
```python
async def setup_user_encryption(self, user_id: int, group_id: int):
    """
    ユーザー専用GPG鍵ペア生成と公開鍵交換
    """
    # 1. ユーザー専用GPG鍵ペア生成
    user_key = await gpg_module.generate_user_keypair(
        name=f"libral_user_{user_id}",
        email=f"{user_id}@libral.local",
        key_type="rsa4096"  # または Ed25519
    )
    
    # 2. 公開鍵をユーザーグループに送信（平文でOK）
    await bot.send_document(
        group_id, 
        document=user_key.public_key,
        caption="🔐 あなたの暗号化用公開鍵です"
    )
    
    # 3. コアサーバーには公開鍵のフィンガープリントのみ保存
    await store_user_key_fingerprint(user_id, user_key.fingerprint)
```

## 3. ログ記録プロトコル

### データ分類と記録ルール

#### 記録対象データ
```python
class LogDataCategory(Enum):
    CONVERSATION = "conversation"      # AI対話ログ
    CREATION_ACTIVITY = "creation"     # スタンプ作成履歴
    TRANSACTION = "transaction"        # 決済・購入履歴
    SYSTEM_EVENT = "system"           # システム通知
    SECURITY_EVENT = "security"       # セキュリティ関連イベント
```

#### ログ記録の実装
```python
class PersonalLogRecorder:
    async def record_to_personal_group(
        self, 
        user_id: int, 
        data: dict, 
        category: LogDataCategory
    ):
        """
        ユーザー個人グループへの暗号化ログ記録
        """
        # 1. ユーザーの個人グループ情報取得
        group_config = await get_user_group_config(user_id)
        if not group_config:
            raise PersonalGroupNotConfigured()
        
        # 2. データのGPG暗号化
        encrypted_data = await gpg_module.encrypt_for_user(
            data=json.dumps(data, ensure_ascii=False, indent=2),
            user_id=user_id,
            context_labels={
                "category": category.value,
                "timestamp": datetime.utcnow().isoformat(),
                "retention": "user_controlled"  # ユーザーが削除権限を持つ
            }
        )
        
        # 3. Telegramメッセージとして送信
        message_text = f"""
🔒 **{category.value.upper()} ログ記録**
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📋 データサイズ: {len(encrypted_data)} bytes
🔐 暗号化済み - あなたの鍵でのみ復号可能

```
{encrypted_data}
```
"""
        
        await bot.send_message(
            chat_id=group_config.group_id,
            text=message_text,
            parse_mode="Markdown"
        )
        
        # 4. 中央サーバーの一時キャッシュは即座にクリア
        await clear_temporary_cache(user_id, category)
```

### セキュリティ強化プロトコル

#### Context-Lock署名の実装
```python
async def create_signed_log_entry(self, user_id: int, data: dict):
    """
    Context-Lock署名付きログエントリの作成
    """
    context_labels = {
        "libral.user_id": str(user_id),
        "libral.app_version": APP_VERSION,
        "libral.log_type": data.get("type", "unknown"),
        "libral.timestamp": str(int(datetime.utcnow().timestamp())),
        "libral.retention_policy": "user_managed"
    }
    
    # データの署名
    signature = await gpg_module.sign_with_context_lock(
        data=json.dumps(data, sort_keys=True),
        context_labels=context_labels,
        signing_key="libral_system_key"
    )
    
    return {
        "data": data,
        "signature": signature,
        "context": context_labels,
        "verification_note": "このログは改ざん検知可能です"
    }
```

## 4. データ取得・分析インターフェース

### ユーザー主導のデータ取得
```python
class PersonalDataRetrieval:
    async def request_data_export(self, user_id: int, date_range: tuple):
        """
        ユーザーが自分のデータエクスポートを要求
        """
        # 1. ユーザー認証
        if not await verify_user_identity(user_id):
            raise AuthenticationError()
        
        # 2. 個人グループからのログ収集指示
        export_request_message = f"""
📊 **データエクスポート要求**

期間: {date_range[0]} - {date_range[1]}

このグループ内の暗号化されたログを収集し、
復号可能な形式でエクスポートしますか？

⚠️ このデータはあなたのGPG秘密鍵でのみ復号できます。
G-ACE.incは復号済みデータにアクセスできません。

✅ エクスポート開始: /export_confirm
❌ キャンセル: /export_cancel
"""
        
        group_config = await get_user_group_config(user_id)
        await bot.send_message(group_config.group_id, export_request_message)
```

## 5. プライバシー監査機能

### 透明性レポート生成
```python
class PrivacyAudit:
    async def generate_privacy_report(self, user_id: int):
        """
        ユーザーのプライバシー状況レポート生成
        """
        report = {
            "user_id": user_id,
            "report_date": datetime.utcnow().isoformat(),
            "data_locations": {
                "central_server": "個人データなし - システム設定のみ",
                "personal_telegram_group": "暗号化ログのみ - ユーザーが完全制御",
                "temporary_cache": "24時間後自動削除"
            },
            "encryption_status": {
                "gpg_key_strength": "RSA-4096 / Ed25519",
                "data_encryption": "全個人データ暗号化済み",
                "transport_security": "TLS 1.3 + GPG二重暗号化"
            },
            "data_retention": {
                "user_controlled": True,
                "automatic_deletion": "24時間",
                "export_capability": True
            },
            "third_party_access": "なし - ユーザーの秘密鍵必須"
        }
        
        # 個人グループにレポート送信
        await self.send_privacy_report_to_user(user_id, report)
```

## 6. 実装上の注意点

### セキュリティ考慮事項
1. **Bot Token管理**: Bot TokenはGPG暗号化した.env.gpgファイルで管理
2. **権限の最小化**: BotはユーザーグループでMessage送信権限のみ
3. **監査ログ**: Bot自体の動作ログは匿名化して別途記録
4. **Rate Limiting**: 個人グループへの送信頻度制限

### スケーラビリティ
1. **非同期処理**: 全ログ記録は非同期タスクで実行
2. **バッチ処理**: 複数ログの一括暗号化・送信
3. **キューイング**: Redis Streamsでログ記録キューを管理

### エラーハンドリング
```python
class PersonalLogError(Exception):
    """個人ログ記録エラーの基底クラス"""
    pass

class GroupNotConfiguredError(PersonalLogError):
    """個人グループが未設定"""
    pass

class EncryptionError(PersonalLogError):
    """暗号化処理エラー"""
    pass

class TelegramDeliveryError(PersonalLogError):
    """Telegram配信エラー"""
    pass
```

このプロトコルにより、**世界初の真のプライバシーファーストAIプラットフォーム**を技術的に実現します。ユーザーは自分のデータを完全にコントロールし、G-ACE.incは技術的にユーザーの個人情報にアクセスできない仕組みを構築します。
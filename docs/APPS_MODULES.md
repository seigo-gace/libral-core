# APPS & MODULES ドキュメント

## 概要
Libral Coreのアプリケーションとモジュール管理システムの説明

## 接続されているモジュール

### 1. Knowledge Base System
- **ID**: kb-system
- **名称**: 多言語知識管理システム
- **言語サポート**: 80+ languages
- **ステータス**: Core/Offline
- **説明**: プライバシーファーストの集合知システム

### 2. AI Bridge
- **ID**: ai-bridge  
- **名称**: AIブリッジレイヤー
- **機能**: 非同期キューコントローラー、リトライ・フォールバック、優先度ベースリクエスト処理

### 3. Evaluator 2.0
- **ID**: evaluator
- **名称**: AI出力評価システム
- **機能**: 多基準評価、自動再生成、KB統合

### 4. OSS Manager
- **ID**: oss-manager
- **名称**: OSSモデル管理
- **サポートモデル**: LLaMA3, Mistral, Falcon, Whisper, CLIP

### 5. AI Router
- **ID**: ai-router
- **名称**: インテリジェントルーティング
- **機能**: タスクタイプ別ルーティング、負荷分散、パフォーマンス監視

### 6. Embedding Layer
- **ID**: embedding
- **名称**: ベクトル埋め込み生成
- **次元数**: 384
- **機能**: コサイン類似度検索、FAISS + ChromaDB対応

### 7. Aegis-PGP
- **ID**: aegis-pgp
- **名称**: 暗号化システム
- **暗号化方式**: AES-256-OCB, RSA-4096, ED25519

### 8. Communication Gateway
- **ID**: communication
- **名称**: マルチトランスポート通信システム
- **対応**: Telegram, Email, Webhook

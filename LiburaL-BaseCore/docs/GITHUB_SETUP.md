# GitHub リポジトリ連携手順

## 🚀 セットアップ手順

### 1. GitHubでリポジトリ作成
1. GitHub.comにログイン
2. 「New repository」をクリック
3. リポジトリ名：`libral-core` (推奨)
4. 説明：「Privacy-first microkernel platform with enterprise-grade cryptography」
5. PublicまたはPrivateを選択
6. 「Add a README file」のチェックを**外す**（既に作成済み）
7. 「Create repository」をクリック

### 2. ローカルリポジトリとGitHubを連携

```bash
# リモートリポジトリを追加（<username>は実際のGitHubユーザー名に置換）
git remote add origin https://github.com/<username>/libral-core.git

# 変更をステージング
git add .

# コミット作成
git commit -m "Initial commit: Libral Core v1.0 - Privacy-first platform with GPG module"

# GitHubにプッシュ
git push -u origin main
```

### 3. GitHub設定確認

プッシュ後、以下が自動的に利用可能になります：

#### ✅ CI/CDパイプライン
- `.github/workflows/ci.yml` が自動実行
- フロントエンド・バックエンド・Python モジュールテスト
- セキュリティスキャン
- 自動デプロイ準備

#### ✅ Issue管理
- バグレポートテンプレート（`.github/ISSUE_TEMPLATE/bug_report.md`）
- 機能要求テンプレート（`.github/ISSUE_TEMPLATE/feature_request.md`）

#### ✅ Pull Request管理
- セキュリティチェックリスト付きPRテンプレート
- 自動レビュー項目

#### ✅ ドキュメント
- `README.md` - プロジェクト概要
- `CONTRIBUTING.md` - 開発ガイドライン
- `SECURITY.md` - セキュリティポリシー

## 🔧 追加設定（オプション）

### ブランチ保護ルール
1. GitHubリポジトリ > Settings > Branches
2. 「Add rule」をクリック
3. Branch name pattern: `main`
4. 推奨設定：
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require pull request reviews before merging

### Secrets設定（CI/CD用）
1. Settings > Secrets and variables > Actions
2. 必要に応じて以下を追加：
   - `DATABASE_URL` - 本番データベースURL
   - `GPG_SYSTEM_KEY_ID` - GPGシステムキーID
   - その他環境変数

## 📊 連携完了後の確認項目

### ✅ リポジトリ表示確認
- [ ] README.mdが正常に表示される
- [ ] プロジェクト概要・機能・セットアップ手順が見える
- [ ] ライセンス情報が正確

### ✅ CI/CD確認
- [ ] Actions タブでワークフローが実行される
- [ ] テストが正常にパス（またはスキップ）
- [ ] セキュリティスキャンが完了

### ✅ コラボレーション準備
- [ ] Issue作成時にテンプレートが表示される
- [ ] PR作成時にチェックリストが表示される
- [ ] ブランチ保護ルールが適用される

## 🎯 次のステップ

連携完了後は以下が可能になります：

1. **チーム開発**：Issue/PRベースの協力開発
2. **自動テスト**：コミット時の品質チェック
3. **セキュリティ管理**：脆弱性の自動検出
4. **デプロイ準備**：本番環境への自動展開
5. **ドキュメント管理**：変更履歴の追跡

## 🔗 関連リンク

- [GitHub リポジトリ作成ガイド](https://docs.github.com/en/get-started/quickstart/create-a-repo)
- [GitHub Actions 設定](https://docs.github.com/en/actions)
- [ブランチ保護ルール](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)

---

**準備完了**: Libral Core は GitHub での協力開発に対応しています。
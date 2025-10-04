#!/bin/bash
#
# Libral Core - Automatic Archive Script
# PCGP V1.0準拠 - GitOps自動アーカイブスクリプト
#
# トリガー: Argo CD SYNCED ステータス時に自動実行
# 用途: デプロイ成功時にソースコード、ポリシー、インフラ設定をアーカイブ
#

set -e

# カラー出力
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Libral Core Archive Script (PCGP)  ${NC}"
echo -e "${BLUE}======================================${NC}"

# プロジェクトルート確認
if [ ! -d "libral-core" ]; then
    echo "Error: libral-core directory not found"
    exit 1
fi

cd libral-core

# タイムスタンプとGitコミットハッシュ取得
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# アーカイブファイル名
ARCHIVE_NAME="${TIMESTAMP}_${COMMIT_HASH}.zip"
ARCHIVE_PATH="archive/${ARCHIVE_NAME}"

echo -e "${GREEN}[1/4] アーカイブ作成準備...${NC}"
mkdir -p archive

echo -e "${GREEN}[2/4] Gitアーカイブ実行...${NC}"
echo "  - ソースコード: src/"
echo "  - ポリシー: policies/"
echo "  - インフラ: infra/"

# Git archive実行
git archive \
    --format=zip \
    --output="${ARCHIVE_PATH}" \
    HEAD \
    -- src/ policies/ infra/ 2>/dev/null || {
        echo "Warning: Git archive failed, creating manual zip..."
        zip -r "${ARCHIVE_PATH}" src/ policies/ infra/ >/dev/null 2>&1
    }

echo -e "${GREEN}[3/4] アーカイブ完了${NC}"
echo "  ファイル: ${ARCHIVE_PATH}"
echo "  サイズ: $(du -h "${ARCHIVE_PATH}" | cut -f1)"

# メタデータファイル作成
METADATA_FILE="archive/${TIMESTAMP}_${COMMIT_HASH}.meta.json"
cat > "${METADATA_FILE}" <<EOF
{
  "archive_name": "${ARCHIVE_NAME}",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commit_hash": "${COMMIT_HASH}",
  "trigger": "Argo CD SYNCED",
  "pcgp_version": "1.0",
  "archived_directories": [
    "src/",
    "policies/",
    "infra/"
  ],
  "archive_size_bytes": $(stat -f%z "${ARCHIVE_PATH}" 2>/dev/null || stat -c%s "${ARCHIVE_PATH}" 2>/dev/null || echo 0)
}
EOF

echo -e "${GREEN}[4/4] メタデータ作成完了${NC}"
echo "  メタデータ: ${METADATA_FILE}"

# 古いアーカイブ削除（30日以前）
echo ""
echo -e "${BLUE}古いアーカイブのクリーンアップ...${NC}"
find archive/ -name "*.zip" -mtime +30 -delete 2>/dev/null || true
find archive/ -name "*.meta.json" -mtime +30 -delete 2>/dev/null || true

echo ""
echo -e "${GREEN}✓ アーカイブ完了！${NC}"
echo -e "${BLUE}======================================${NC}"

exit 0

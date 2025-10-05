import os
import shutil
from pathlib import Path

# --- PCGP V1.0 ディレクトリ定義 ---
BASE_DIR = Path(os.getcwd())
PCGP_DIRS = {
    "src": BASE_DIR / "src",
    "docs": BASE_DIR / "docs",
    "infra": BASE_DIR / "infra",
    "policies": BASE_DIR / "policies",
    "archive": BASE_DIR / "archive",
}
# --- 移動対象のファイルとPCGP内の配置先マッピング ---
# 注意: 既存のファイル名と場所に合わせて調整すること
FILE_MAPPING = {
    # 既存のトップレベルファイル
    "README.md": PCGP_DIRS["docs"],
    "SECURITY.md": PCGP_DIRS["docs"],
    "DEPLOYMENT.MD": PCGP_DIRS["docs"], # 推測: 大文字小文字の区別を考慮
    "PRODUCTION_STATUS.MD": PCGP_DIRS["docs"],
    "CONTRIBUTING.MD": PCGP_DIRS["docs"],

    # インフラ設定ファイル (GitOpsソース)
    "docker-compose.yml": PCGP_DIRS["infra"],
    "Dockerfile": PCGP_DIRS["infra"],
    "drizzle.config.ts": PCGP_DIRS["infra"], # 推測: Drizzle ORM設定
    "postcss.config.js": PCGP_DIRS["infra"], # 推測: フロントエンドビルド設定
    "tailwind.config.ts": PCGP_DIRS["infra"], # 推測: フロントエンドビルド設定

    # ルートにあるコード/設定ファイル (srcへ移動すべきもの)
    "main.py": PCGP_DIRS["src"],
    "pyproject.toml": PCGP_DIRS["src"],
    "uv.lock": PCGP_DIRS["src"],
    "package.json": PCGP_DIRS["src"], # フロントエンドの依存関係
    "package-lock.json": PCGP_DIRS["src"],
    "tsconfig.json": PCGP_DIRS["src"],
    "vite.config.ts": PCGP_DIRS["src"],
    "components.json": PCGP_DIRS["src"] # Shadcn/UIのcomponents.jsonもsrcへ

    # その他の設定ファイル (要件外だが整理)
    "replit.md": PCGP_DIRS["docs"],
    ".replit": BASE_DIR / ".config", # 隠しフォルダ.configに移動 (システム設定)
    ".gitignore": BASE_DIR / ".config" # 隠しフォルダ.configに移動
}
# --- 整理実行関数 ---
def enforce_pcgp_v1_0():
    print(f"--- PCGP V1.0 フォルダ作成開始 ---")
    for name, path in PCGP_DIRS.items():
        path.mkdir(exist_ok=True)
        print(f"✅ フォルダ作成: {name}/")
    
    # .configディレクトリの特別処理
    (BASE_DIR / ".config").mkdir(exist_ok=True)
    print(f"✅ フォルダ作成: .config/")

    print(f"\n--- ファイル移動開始 ---")
    moved_count = 0
    
    for filename, target_dir in FILE_MAPPING.items():
        source_path = BASE_DIR / filename
        target_path = target_dir / filename

        if source_path.exists():
            try:
                # 既にファイルがある場合の上書きは行わないが、整理のため移動を試行
                if source_path.is_file():
                    shutil.move(str(source_path), str(target_path))
                    print(f"✅ 移動: {filename} -> {target_dir.name}/")
                    moved_count += 1
                elif source_path.is_dir():
                    # フォルダの移動は手動で確認 (ここでは無視)
                    pass
            except Exception as e:
                print(f"❌ 移動失敗 {filename}: {e}")
        else:
            # print(f"スキップ: {filename} (ファイルが見つかりません)")
            pass

    print(f"\n--- 整理完了 ---")
    print(f"🚀 合計 {moved_count} 個のファイルがPCGP構造に移動されました。")

# --- 実行 ---
if __name__ == "__main__":
    # ⚠️ 実行前にファイルをコミットするか、バックアップを取ることを推奨
    enforce_pcgp_v1_0()
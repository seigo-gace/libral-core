# pcgp_tools/repairer.py
import shutil
from pathlib import Path
import sys

class PCGPRepairer:
    FILE_MAPPING = {
        # docs
        "README.md": "docs",
        "README_PRODUCTION.md": "docs",
        "DEPLOYMENT.md": "docs",
        "PRODUCTION_STATUS.md": "docs",
        "CONTRIBUTING.md": "docs",
        "SECURITY.md": "docs",
        "GITHUB_SETUP.md": "docs",
        "replit.md": "docs",
        # infra
        "Dockerfile": "infra",
        "docker-compose.yml": "infra",
        "drizzle.config.ts": "infra",
        "postcss.config.js": "infra",
        "tailwind.config.ts": "infra",
        "vite.config.ts": "infra",
        # src
        "main.py": "src",
        "pyproject.toml": "src",
        "uv.lock": "src",
        "package.json": "src",
        "package-lock.json": "src",
        "tsconfig.json": "src",
        "components.json": "src",
        # .config
        ".replit": ".config",
        ".replitignore": ".config",
        ".gitignore": ".config",
        ".dockerignore": ".config",
        ".env.example": ".config",
    }
    PCGP_TARGET_DIRS = ["src", "docs", "infra", "policies", "archive"]

    def create_pcgp_directories(self):
        for d in self.PCGP_TARGET_DIRS:
            Path(d).mkdir(parents=True, exist_ok=True)
        Path(".config").mkdir(parents=True, exist_ok=True)
        print("? PCGPディレクトリ作成完了")

    def enforce_structure(self):
        print("?? 小型ファイルの整理開始")
        moved_count = 0
        for src, target in self.FILE_MAPPING.items():
            s = Path(src)
            t = Path(target)
            if target == ".config":
                t = Path(".config")
            final_target = t / src
            if s.exists():
                try:
                    t.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(s), str(final_target))
                    print(f"? {src} -> {target}/")
                    moved_count += 1
                except Exception as e:
                    print(f"? 移動失敗 {src}: {e}")
        print(f"?? 小型ファイル整理完了: {moved_count}個\n")

    def enforce_large_folders(self):
        print("?? 大型フォルダ移動開始")
        FOLDER_MAPPING = {
            "client": "src/client",
            "server": "src/server",
            "shared": "src/library/shared",
            "libral-core": "src/modules/libral_core"
        }
        for src, target in FOLDER_MAPPING.items():
            self._move_folder(src, target)
        print("?? 大型フォルダ移動完了\n")

    def _move_folder(self, src, target):
        s = Path(src)
        t = Path(target)
        if s.exists() and s.is_dir():
            try:
                t.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(s), str(t))
                print(f"? {src}/ -> {target}/")
            except Exception as e:
                print(f"? フォルダ移動失敗 {src} -> {target}: {e}")
                sys.exit(1)
        elif not s.exists():
            print(f"?? スキップ: {src}/ は見つかりません。")

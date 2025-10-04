"""
Libral Core - Main Entry Point (PCGP V1.0)
Professional Grooming Protocol準拠のエントリーポイント

このファイルはsrc/main.pyへのルーティングを行います。
"""

import sys
from pathlib import Path

# PCGP構造対応: src/ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

# メインアプリケーションをインポート
from main import app

if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    uvicorn.run(
        "main:app",
        host=getattr(settings, 'host', '0.0.0.0'),
        port=getattr(settings, 'port', 8000),
        reload=getattr(settings, 'reload', True),
        log_level=getattr(settings, 'log_level', 'INFO').lower()
    )

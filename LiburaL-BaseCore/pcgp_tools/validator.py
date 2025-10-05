# pcgp_tools/validator.py
from pathlib import Path

class PCGPValidator:
    REQUIRED_ROOT_FILES = ["pyproject.toml", "package.json", "main.py", "docker-compose.yml"]

    def check_initial_state(self):
        print("?? 構造チェック開始: 必須ファイルの存在確認")
        all_found = True
        for f in self.REQUIRED_ROOT_FILES:
            if not Path(f).exists():
                print(f"? 欠損: {f} がルートに見つかりません。")
                all_found = False
            else:
                print(f"? 存在確認: {f}")
        if not all_found:
            print("?? チェック失敗: 整理を中断します。")
        else:
            print("?? チェック完了: 初期状態は正常です。")
        return all_found

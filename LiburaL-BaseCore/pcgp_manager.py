# pcgp_manager.py
from pcgp_tools.validator import PCGPValidator
from pcgp_tools.repairer import PCGPRepairer
from pcgp_tools.archiver import PCGPArchiver
import sys

def main():
    print("=== Libral Core PCGP 自律グルーミング開始 ===")
    
    # 1. Validator: 構造チェック (問題あれば即停止)
    validator = PCGPValidator()
    if not validator.check_initial_state():
        print("? 致命的な初期状態の欠損: 処理を中断します。")
        sys.exit(1)

    # 2. Repairer: 構造整理とファイル移動
    try:
        r = PCGPRepairer()
        r.create_pcgp_directories()
        r.enforce_structure()
        r.enforce_large_folders()
    except Exception as e:
        print(f"? 致命的な修復エラー: {e}")
        sys.exit(1)

    # 3. Archiver: 古いファイルをアーカイブ
    PCGPArchiver().archive_old_files()

    print("=== PCGP 自律グルーミング完了: Git コミットの準備完了 ===")
    print("?? Gitパネルに戻り、全ての変更をコミット＆プッシュしてください。")

if __name__ == "__main__":
    main()

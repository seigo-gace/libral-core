"""
Component: Configuration Loader
PCGP Component Layer - 設定読み込みの最小単位部品

全てのモジュールから参照される統一的な設定管理機能
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import os


class ConfigLoader:
    """統一設定ローダー"""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        初期化
        
        Args:
            base_path: 設定ファイルのベースパス（Noneの場合はプロジェクトルート）
        """
        if base_path is None:
            # プロジェクトルートを自動検出
            self.base_path = Path(__file__).parent.parent.parent.parent
        else:
            self.base_path = Path(base_path)
    
    def load_json(self, file_path: str) -> Dict[str, Any]:
        """
        JSONファイル読み込み
        
        Args:
            file_path: ファイルパス（base_pathからの相対パス）
        
        Returns:
            読み込んだ設定辞書
        """
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        YAMLファイル読み込み
        
        Args:
            file_path: ファイルパス（base_pathからの相対パス）
        
        Returns:
            読み込んだ設定辞書
        """
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        環境変数読み込み
        
        Args:
            key: 環境変数名
            default: デフォルト値
        
        Returns:
            環境変数の値
        """
        return os.environ.get(key, default)
    
    def load_policy(self, policy_name: str) -> Dict[str, Any]:
        """
        ポリシーファイル読み込み（policies/ディレクトリ）
        
        Args:
            policy_name: ポリシーファイル名（拡張子なし）
        
        Returns:
            ポリシー設定辞書
        """
        # JSON優先、なければYAML
        json_path = f"policies/{policy_name}.json"
        yaml_path = f"policies/{policy_name}.yaml"
        
        if (self.base_path / json_path).exists():
            return self.load_json(json_path)
        elif (self.base_path / yaml_path).exists():
            return self.load_yaml(yaml_path)
        else:
            raise FileNotFoundError(f"ポリシーファイルが見つかりません: {policy_name}")
    
    def get_bool_env(self, key: str, default: bool = False) -> bool:
        """
        ブール型環境変数読み込み
        
        Args:
            key: 環境変数名
            default: デフォルト値
        
        Returns:
            ブール値
        """
        value = self.load_env(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_int_env(self, key: str, default: int = 0) -> int:
        """
        整数型環境変数読み込み
        
        Args:
            key: 環境変数名
            default: デフォルト値
        
        Returns:
            整数値
        """
        value = self.load_env(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default


# グローバルインスタンス
config_loader = ConfigLoader()

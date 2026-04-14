"""
Component: Validators
PCGP Component Layer - バリデーション機能の最小単位部品

全てのモジュールから参照される統一的なバリデーション機能
"""

import re
from typing import Optional, Any


class ValidationError(Exception):
    """バリデーションエラー"""
    pass


def validate_not_empty(value: str, field_name: str = "Value") -> str:
    """
    空文字列チェック
    
    Args:
        value: チェック対象文字列
        field_name: フィールド名（エラーメッセージ用）
    
    Returns:
        検証済み文字列
    
    Raises:
        ValidationError: 空文字列の場合
    """
    if not value or not value.strip():
        raise ValidationError(f"{field_name}は空にできません")
    return value.strip()


def validate_email(email: str) -> str:
    """
    メールアドレスバリデーション
    
    Args:
        email: メールアドレス
    
    Returns:
        検証済みメールアドレス
    
    Raises:
        ValidationError: 不正な形式の場合
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"不正なメールアドレス形式: {email}")
    return email.lower()


def validate_url(url: str) -> str:
    """
    URL形式バリデーション
    
    Args:
        url: URL文字列
    
    Returns:
        検証済みURL
    
    Raises:
        ValidationError: 不正な形式の場合
    """
    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    if not re.match(pattern, url):
        raise ValidationError(f"不正なURL形式: {url}")
    return url


def validate_length(value: str, min_length: int = 0, max_length: int = 1000, field_name: str = "Value") -> str:
    """
    文字列長バリデーション
    
    Args:
        value: チェック対象文字列
        min_length: 最小文字数
        max_length: 最大文字数
        field_name: フィールド名
    
    Returns:
        検証済み文字列
    
    Raises:
        ValidationError: 長さが範囲外の場合
    """
    length = len(value)
    if length < min_length:
        raise ValidationError(f"{field_name}は{min_length}文字以上である必要があります")
    if length > max_length:
        raise ValidationError(f"{field_name}は{max_length}文字以下である必要があります")
    return value


def validate_range(value: int, min_value: int = 0, max_value: int = 100, field_name: str = "Value") -> int:
    """
    数値範囲バリデーション
    
    Args:
        value: チェック対象数値
        min_value: 最小値
        max_value: 最大値
        field_name: フィールド名
    
    Returns:
        検証済み数値
    
    Raises:
        ValidationError: 範囲外の場合
    """
    if value < min_value:
        raise ValidationError(f"{field_name}は{min_value}以上である必要があります")
    if value > max_value:
        raise ValidationError(f"{field_name}は{max_value}以下である必要があります")
    return value


def validate_enum(value: str, allowed_values: list, field_name: str = "Value") -> str:
    """
    列挙値バリデーション
    
    Args:
        value: チェック対象値
        allowed_values: 許可される値のリスト
        field_name: フィールド名
    
    Returns:
        検証済み値
    
    Raises:
        ValidationError: 許可されていない値の場合
    """
    if value not in allowed_values:
        raise ValidationError(f"{field_name}は{allowed_values}のいずれかである必要があります")
    return value


def validate_pattern(value: str, pattern: str, field_name: str = "Value") -> str:
    """
    正規表現パターンバリデーション
    
    Args:
        value: チェック対象文字列
        pattern: 正規表現パターン
        field_name: フィールド名
    
    Returns:
        検証済み文字列
    
    Raises:
        ValidationError: パターンに一致しない場合
    """
    if not re.match(pattern, value):
        raise ValidationError(f"{field_name}がパターンに一致しません: {pattern}")
    return value


def sanitize_string(value: str, allowed_chars: str = r'a-zA-Z0-9_-') -> str:
    """
    文字列サニタイズ（許可された文字のみ残す）
    
    Args:
        value: サニタイズ対象文字列
        allowed_chars: 許可する文字の正規表現パターン
    
    Returns:
        サニタイズ済み文字列
    """
    pattern = f'[^{allowed_chars}]'
    return re.sub(pattern, '', value)

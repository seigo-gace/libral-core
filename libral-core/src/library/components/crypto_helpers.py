"""
Component: Cryptographic Helpers
PCGP Component Layer - 暗号化ヘルパーの最小単位部品

全てのモジュールから参照される暗号化・ハッシュ機能
"""

import hashlib
import hmac
import secrets
import base64
from typing import Optional


def generate_random_token(length: int = 32) -> str:
    """
    安全なランダムトークン生成
    
    Args:
        length: トークン長（バイト数）
    
    Returns:
        Base64エンコードされたトークン
    """
    token_bytes = secrets.token_bytes(length)
    return base64.urlsafe_b64encode(token_bytes).decode('utf-8').rstrip('=')


def generate_random_id(length: int = 16) -> str:
    """
    安全なランダムID生成（英数字のみ）
    
    Args:
        length: ID長（文字数）
    
    Returns:
        英数字のランダムID
    """
    return secrets.token_hex(length // 2)


def sha256_hash(data: str) -> str:
    """
    SHA-256ハッシュ計算
    
    Args:
        data: ハッシュ対象データ
    
    Returns:
        16進数ハッシュ文字列
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def sha512_hash(data: str) -> str:
    """
    SHA-512ハッシュ計算
    
    Args:
        data: ハッシュ対象データ
    
    Returns:
        16進数ハッシュ文字列
    """
    return hashlib.sha512(data.encode('utf-8')).hexdigest()


def hmac_sha256(data: str, key: str) -> str:
    """
    HMAC-SHA256署名計算
    
    Args:
        data: 署名対象データ
        key: 秘密鍵
    
    Returns:
        16進数HMAC署名
    """
    return hmac.new(
        key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def verify_hmac_sha256(data: str, signature: str, key: str) -> bool:
    """
    HMAC-SHA256署名検証
    
    Args:
        data: 検証対象データ
        signature: 検証する署名
        key: 秘密鍵
    
    Returns:
        署名が正しければTrue
    """
    expected = hmac_sha256(data, key)
    return hmac.compare_digest(signature, expected)


def base64_encode(data: str) -> str:
    """Base64エンコード"""
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')


def base64_decode(encoded: str) -> str:
    """Base64デコード"""
    return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')


def constant_time_compare(a: str, b: str) -> bool:
    """
    タイミング攻撃に安全な文字列比較
    
    Args:
        a: 比較文字列1
        b: 比較文字列2
    
    Returns:
        一致すればTrue
    """
    return secrets.compare_digest(a, b)

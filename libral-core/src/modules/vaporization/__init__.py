"""
Vaporization Protocol
キャッシュ揮発プロトコル

Hetznerキャッシュサーバーに格納される全個人関連データに対し、
最大24時間のTTLと揮発プロトコルを強制的に適用
"""

from .core import VaporizationCore, vaporization_core
from .redis_ttl import RedisTTLEnforcer
from .flush_hook import KBEFlushHook

__all__ = [
    'VaporizationCore',
    'vaporization_core',
    'RedisTTLEnforcer',
    'KBEFlushHook'
]

__version__ = "1.0.0"

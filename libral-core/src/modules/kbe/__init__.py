"""
KBE (Knowledge Booster Engine)
ナレッジ・ブースター・エンジン

ユーザーのプライバシーを保護しつつ、集合知を構築
- フェデレーテッド・ラーニング
- 同型暗号による学習結果集計
"""

from .core import KBECore, kbe_core
from .federated import FederatedLearningInterface
from .homomorphic import HomomorphicAggregator

__all__ = [
    'KBECore',
    'kbe_core',
    'FederatedLearningInterface',
    'HomomorphicAggregator'
]

__version__ = "1.0.0"

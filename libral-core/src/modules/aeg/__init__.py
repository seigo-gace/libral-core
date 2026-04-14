"""
AEG (Auto Evolution Gateway)
自動進化ゲートウェイ

KBEの集合知とLPOの健全性スコアに基づき、
プラットフォームの進化を自律的に行う
"""

from .core import AEGCore, aeg_core
from .prioritization import DevelopmentPrioritizationAI
from .git_pr import GitHubPRGenerator

__all__ = [
    'AEGCore',
    'aeg_core',
    'DevelopmentPrioritizationAI',
    'GitHubPRGenerator'
]

__version__ = "1.0.0"

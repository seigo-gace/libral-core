"""
Component: DateTime Utilities
PCGP Component Layer - 日時処理の最小単位部品

全てのモジュールから参照される統一的な日時処理機能
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import time


def utc_now() -> datetime:
    """UTC現在時刻を取得"""
    return datetime.now(timezone.utc)


def utc_timestamp() -> float:
    """UTCタイムスタンプ（秒）を取得"""
    return time.time()


def utc_timestamp_ms() -> int:
    """UTCタイムスタンプ（ミリ秒）を取得"""
    return int(time.time() * 1000)


def format_iso8601(dt: datetime) -> str:
    """ISO 8601形式の文字列に変換"""
    return dt.isoformat()


def parse_iso8601(iso_string: str) -> datetime:
    """ISO 8601形式の文字列をdatetimeに変換"""
    return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))


def is_business_hours(dt: Optional[datetime] = None, tz: timezone = timezone.utc) -> bool:
    """
    営業時間判定（UTC 7:00-22:00）
    
    Args:
        dt: 判定する日時（Noneの場合は現在時刻）
        tz: タイムゾーン
    
    Returns:
        営業時間内ならTrue
    """
    if dt is None:
        dt = utc_now()
    
    hour = dt.astimezone(tz).hour
    return 7 <= hour < 22


def add_hours(dt: datetime, hours: int) -> datetime:
    """時間を加算"""
    return dt + timedelta(hours=hours)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """分を加算"""
    return dt + timedelta(minutes=minutes)


def add_days(dt: datetime, days: int) -> datetime:
    """日を加算"""
    return dt + timedelta(days=days)


def format_relative_time(dt: datetime) -> str:
    """
    相対時間表示（"3分前", "2時間前"など）
    
    Args:
        dt: 基準となる日時
    
    Returns:
        相対時間文字列
    """
    now = utc_now()
    diff = now - dt
    
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return f"{seconds}秒前"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分前"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}時間前"
    else:
        days = seconds // 86400
        return f"{days}日前"

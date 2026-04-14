"""
DateTime Utilities

Provides unified datetime handling for all Libral Core modules.
Ensures consistent timezone management and date formatting across the platform.
"""

from datetime import datetime, timezone
from typing import Optional
import iso8601


class DateTimeUtils:
    """
    Utility class for consistent datetime processing across all modules.
    
    Design Intent:
    - Eliminate timezone-related bugs through UTC standardization
    - Provide consistent datetime formatting for APIs and storage
    - Support international deployment with timezone-agnostic operations
    """
    
    @staticmethod
    def format_datetime_utc(dt: datetime) -> str:
        """
        Convert datetime object to ISO 8601 UTC string format.
        
        This method ensures all datetime values are stored and transmitted
        in a consistent, timezone-independent format.
        
        Args:
            dt: datetime object to format
            
        Returns:
            ISO 8601 formatted UTC datetime string
            
        Example:
            >>> dt = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
            >>> DateTimeUtils.format_datetime_utc(dt)
            "2024-01-15T12:30:00+00:00"
        """
        if not dt:
            return ""
            
        # Convert to UTC if timezone-aware
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        else:
            # Assume naive datetime is already UTC
            dt = dt.replace(tzinfo=timezone.utc)
            
        return dt.isoformat()
    
    @staticmethod
    def parse_datetime_utc(dt_string: str) -> Optional[datetime]:
        """
        Parse ISO 8601 datetime string to datetime object in UTC.
        
        This method handles various ISO 8601 formats and ensures
        the result is always in UTC timezone.
        
        Args:
            dt_string: ISO 8601 formatted datetime string
            
        Returns:
            datetime object in UTC, or None if parsing fails
            
        Example:
            >>> DateTimeUtils.parse_datetime_utc("2024-01-15T12:30:00+00:00")
            datetime(2024, 1, 15, 12, 30, tzinfo=timezone.utc)
        """
        if not dt_string:
            return None
            
        try:
            # Parse ISO 8601 string with timezone support
            dt = iso8601.parse_date(dt_string)
            
            # Convert to UTC if not already
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc)
            else:
                dt = dt.replace(tzinfo=timezone.utc)
                
            return dt
            
        except (ValueError, TypeError, iso8601.ParseError):
            return None
    
    @staticmethod
    def get_current_utc() -> datetime:
        """
        Get current datetime in UTC timezone.
        
        Returns:
            Current datetime in UTC
        """
        return datetime.now(timezone.utc)
    
    @staticmethod
    def format_relative_time(dt: datetime) -> str:
        """
        Format datetime as relative time for UI display (e.g., "2 hours ago").
        
        Design Intent: Support real-time event display in dashboard
        
        Args:
            dt: datetime to format
            
        Returns:
            Human-readable relative time string
        """
        if not dt:
            return "Unknown"
            
        now = DateTimeUtils.get_current_utc()
        
        # Ensure both datetimes are UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        else:
            dt = dt.replace(tzinfo=timezone.utc)
            
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}日前"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours}時間前"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes}分前"
        else:
            return "たった今"
    
    @staticmethod
    def format_timestamp_for_telegram(dt: datetime) -> str:
        """
        Format datetime for Telegram personal log servers.
        
        Design Intent: Support Telegram topics and personal log protocol
        
        Args:
            dt: datetime to format
            
        Returns:
            Formatted timestamp suitable for Telegram logs
        """
        if not dt:
            return ""
            
        # Convert to UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        else:
            dt = dt.replace(tzinfo=timezone.utc)
            
        # Format for Telegram: YYYY-MM-DD HH:MM:SS UTC
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    @staticmethod
    def is_within_business_hours(dt: datetime, start_hour: int = 9, end_hour: int = 17) -> bool:
        """
        Check if datetime falls within business hours (UTC).
        
        Design Intent: Support API rate limiting and notification scheduling
        
        Args:
            dt: datetime to check
            start_hour: Business day start hour (UTC)
            end_hour: Business day end hour (UTC)
            
        Returns:
            True if within business hours, False otherwise
        """
        if not dt:
            return False
            
        # Convert to UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        else:
            dt = dt.replace(tzinfo=timezone.utc)
            
        # Check if weekday and within business hours
        is_weekday = dt.weekday() < 5  # 0-4 are Monday-Friday
        is_business_hour = start_hour <= dt.hour < end_hour
        
        return is_weekday and is_business_hour
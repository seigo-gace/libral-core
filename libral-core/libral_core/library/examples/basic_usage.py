#!/usr/bin/env python3
"""
Libral Core Library Module - Basic Usage Examples

This script demonstrates how to use the Library Module utilities
in real applications. Run this file to see the Library Module in action.
"""

import sys
import os
from datetime import datetime, timezone

# Add the parent directory to the path so we can import the library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from library.utils.string_utils import StringUtils
from library.utils.datetime_utils import DateTimeUtils


def demo_string_utils():
    """Demonstrate StringUtils functionality."""
    print("=== StringUtils Demo ===")
    
    # 1. Text sanitization for security
    dangerous_input = "<script>alert('XSS')</script>Hello World!"
    safe_text = StringUtils.sanitize_text(dangerous_input)
    print(f"Original: {dangerous_input}")
    print(f"Sanitized: {safe_text}")
    print()
    
    # 2. Text truncation for UI display
    long_text = "This is a very long text that needs to be truncated for display in UI"
    truncated = StringUtils.truncate_text(long_text, 30)
    print(f"Original: {long_text}")
    print(f"Truncated: {truncated}")
    print()
    
    # 3. Hashtag extraction for Telegram topics
    telegram_text = "Check out our #LibralCore platform! It has amazing #privacy features and #AI capabilities"
    hashtags = StringUtils.extract_hashtags(telegram_text)
    print(f"Text: {telegram_text}")
    print(f"Hashtags: {hashtags}")
    print()
    
    # 4. Telegram username validation
    usernames = ["valid_user", "test123", "ab", "user@invalid", "long_valid_username"]
    print("Username validation:")
    for username in usernames:
        is_valid = StringUtils.validate_telegram_username(username)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {username}: {status}")
    print()


def demo_datetime_utils():
    """Demonstrate DateTimeUtils functionality."""
    print("=== DateTimeUtils Demo ===")
    
    # 1. Current UTC time
    current_utc = DateTimeUtils.get_current_utc()
    formatted_utc = DateTimeUtils.format_datetime_utc(current_utc)
    print(f"Current UTC time: {formatted_utc}")
    print()
    
    # 2. Parse datetime from string
    datetime_string = "2024-08-28T12:30:00+00:00"
    parsed_dt = DateTimeUtils.parse_datetime_utc(datetime_string)
    print(f"Parsed datetime: {parsed_dt}")
    print()
    
    # 3. Relative time formatting
    import datetime as dt
    
    # Simulate different times
    now = DateTimeUtils.get_current_utc()
    one_hour_ago = now - dt.timedelta(hours=1)
    yesterday = now - dt.timedelta(days=1)
    
    relative_times = [
        (now, "now"),
        (one_hour_ago, "1 hour ago"),
        (yesterday, "yesterday")
    ]
    
    print("Relative time formatting:")
    for time_obj, description in relative_times:
        relative = DateTimeUtils.format_relative_time(time_obj)
        print(f"  {description}: {relative}")
    print()
    
    # 4. Telegram timestamp formatting
    telegram_format = DateTimeUtils.format_timestamp_for_telegram(current_utc)
    print(f"Telegram format: {telegram_format}")
    print()
    
    # 5. Business hours check
    is_business_hours = DateTimeUtils.is_within_business_hours(current_utc)
    status = "Yes" if is_business_hours else "No"
    print(f"Is business hours (9-17 UTC, weekday): {status}")
    print()


def demo_integrated_usage():
    """Demonstrate how utilities work together in real scenarios."""
    print("=== Integrated Usage Demo ===")
    
    # Scenario: Processing a user message for Telegram personal log
    user_message = "<b>Just logged into #LibralCore!</b> The #privacy features are amazing 🚀"
    
    # 1. Sanitize the message for security
    safe_message = StringUtils.sanitize_text(user_message)
    
    # 2. Extract hashtags for topic organization
    hashtags = StringUtils.extract_hashtags(safe_message)
    
    # 3. Truncate for preview display
    preview = StringUtils.truncate_text(safe_message, 50)
    
    # 4. Generate timestamp for logging
    timestamp = DateTimeUtils.format_timestamp_for_telegram(
        DateTimeUtils.get_current_utc()
    )
    
    # 5. Create structured log entry
    log_entry = {
        "timestamp": timestamp,
        "message": safe_message,
        "preview": preview,
        "hashtags": hashtags,
        "user": "demo_user"
    }
    
    print("Processing user message for Telegram personal log:")
    print(f"Original: {user_message}")
    print(f"Processed log entry:")
    for key, value in log_entry.items():
        print(f"  {key}: {value}")
    print()


def main():
    """Run all demonstrations."""
    print("Libral Core Library Module - Usage Examples")
    print("=" * 50)
    print()
    
    try:
        demo_string_utils()
        demo_datetime_utils()
        demo_integrated_usage()
        
        print("All demonstrations completed successfully!")
        print("\nThe Library Module is working correctly and ready for use.")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        print("Please check that all dependencies are installed.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
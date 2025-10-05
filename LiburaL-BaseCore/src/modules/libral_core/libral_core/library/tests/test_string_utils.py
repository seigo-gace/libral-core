"""
Tests for String Utilities

Unit tests for the StringUtils class to ensure secure and consistent string processing.
"""

import unittest
from libral_core.library.utils.string_utils import StringUtils


class TestStringUtils(unittest.TestCase):
    
    def test_sanitize_text_removes_html_tags(self):
        """Test that HTML tags are properly removed."""
        input_text = "<script>alert('xss')</script>Hello World"
        result = StringUtils.sanitize_text(input_text)
        self.assertEqual(result, "Hello World")
    
    def test_sanitize_text_handles_empty_input(self):
        """Test handling of empty or None input."""
        self.assertEqual(StringUtils.sanitize_text(""), "")
        self.assertEqual(StringUtils.sanitize_text(None), "")
    
    def test_truncate_text_basic_functionality(self):
        """Test basic text truncation."""
        text = "This is a very long text that needs to be truncated"
        result = StringUtils.truncate_text(text, 20)
        self.assertEqual(result, "This is a very lo...")
        self.assertTrue(len(result) <= 20)
    
    def test_truncate_text_no_truncation_needed(self):
        """Test that short text is not truncated."""
        text = "Short text"
        result = StringUtils.truncate_text(text, 20)
        self.assertEqual(result, text)
    
    def test_extract_hashtags(self):
        """Test hashtag extraction functionality."""
        text = "Hello #world this is #test #hashtag"
        hashtags = StringUtils.extract_hashtags(text)
        expected = ['world', 'test', 'hashtag']
        self.assertEqual(sorted(hashtags), sorted(expected))
    
    def test_validate_telegram_username(self):
        """Test Telegram username validation."""
        valid_usernames = ["user123", "test_user", "validuser"]
        invalid_usernames = ["ab", "user@name", "user name", ""]
        
        for username in valid_usernames:
            self.assertTrue(StringUtils.validate_telegram_username(username))
        
        for username in invalid_usernames:
            self.assertFalse(StringUtils.validate_telegram_username(username))


if __name__ == '__main__':
    unittest.main()
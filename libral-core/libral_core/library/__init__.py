"""
Libral Core Library Module

This module provides common functionality shared across all Libral Core apps and modules.
It serves as a centralized "toolbox" for utilities, API clients, and file handlers.

Architecture:
- utils: Common utility functions for string processing, datetime handling, etc.
- api_clients: Unified external API communication clients  
- file_handlers: Media file processing (images, videos)

Design Philosophy:
- Eliminate code duplication across modules
- Provide consistent interfaces for common operations
- Maintain loose coupling with Libral Core
- Enable rapid development of new apps
"""

from .utils import StringUtils, DateTimeUtils
from .api_clients import BaseAPIClient, ExternalSearchClient
from .file_handlers import ImageProcessor, VideoProcessor

__all__ = [
    'StringUtils',
    'DateTimeUtils', 
    'BaseAPIClient',
    'ExternalSearchClient',
    'ImageProcessor',
    'VideoProcessor'
]

__version__ = "1.0.0"
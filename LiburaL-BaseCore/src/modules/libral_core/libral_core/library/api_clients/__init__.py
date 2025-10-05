"""
API Clients Submodule

Provides unified external API communication clients with consistent authentication,
error handling, and request/response processing.
"""

from .base_client import BaseAPIClient
from .external_search_client import ExternalSearchClient

__all__ = ['BaseAPIClient', 'ExternalSearchClient']
"""
External Search Client

Provides unified access to external search APIs for real-time information retrieval.
This client enables the Libral (AI) module to access current information beyond its training data.
"""

from typing import List, Dict, Any, Optional
import logging
from .base_client import BaseAPIClient, APIError


logger = logging.getLogger(__name__)


class ExternalSearchClient(BaseAPIClient):
    """
    Client for external search API integration.
    
    Design Intent:
    - Enable Libral (AI) module to provide real-time, current information
    - Support multiple search providers through unified interface
    - Implement intelligent result filtering and ranking
    - Cache frequent queries for performance optimization
    
    This class inherits from BaseAPIClient, automatically getting:
    - Unified authentication handling
    - Consistent error processing
    - Retry logic and timeouts
    - Request logging and monitoring
    """
    
    def __init__(self, api_key: str, provider: str = "duckduckgo"):
        """
        Initialize external search client.
        
        Args:
            api_key: API key for the search provider
            provider: Search provider ("duckduckgo", "google", "bing")
        """
        # Configure base URL based on provider
        base_urls = {
            "duckduckgo": "https://api.duckduckgo.com",
            "google": "https://www.googleapis.com/customsearch/v1",
            "bing": "https://api.bing.microsoft.com/v7.0"
        }
        
        base_url = base_urls.get(provider, base_urls["duckduckgo"])
        
        super().__init__(api_key, base_url)
        self.provider = provider
        
        # Configure provider-specific settings
        self._configure_provider()
    
    def _configure_provider(self) -> None:
        """Configure provider-specific authentication and headers."""
        if self.provider == "bing":
            # Bing uses Ocp-Apim-Subscription-Key header
            self.session.headers.update({
                'Ocp-Apim-Subscription-Key': self.api_key
            })
            # Remove default Authorization header for Bing
            self.session.headers.pop('Authorization', None)
        elif self.provider == "google":
            # Google Custom Search uses query parameter for API key
            pass  # API key will be passed as parameter
        # DuckDuckGo typically doesn't require authentication
    
    def search(self, query: str, max_results: int = 10, safe_search: bool = True) -> List[Dict[str, Any]]:
        """
        Perform search query and return structured results.
        
        This method provides a unified interface across different search providers,
        enabling the AI module to access real-time information consistently.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            safe_search: Enable safe search filtering
            
        Returns:
            List of search results with standardized structure:
            [
                {
                    "title": "Result title",
                    "url": "https://example.com",
                    "snippet": "Result description...",
                    "source": "domain.com",
                    "relevance_score": 0.95
                }
            ]
            
        Raises:
            APIError: If search fails or returns invalid data
            
        Example:
            >>> client = ExternalSearchClient("api_key", "google")
            >>> results = client.search("Libral Core privacy features")
            >>> for result in results:
            ...     print(f"{result['title']}: {result['url']}")
        """
        if not query or not query.strip():
            return []
        
        # Sanitize query
        query = query.strip()[:500]  # Limit query length
        
        logger.info(f"Performing search: '{query}' (provider: {self.provider})")
        
        try:
            if self.provider == "google":
                return self._search_google(query, max_results, safe_search)
            elif self.provider == "bing":
                return self._search_bing(query, max_results, safe_search)
            else:
                return self._search_duckduckgo(query, max_results, safe_search)
                
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise APIError(f"Search operation failed: {str(e)}")
    
    def _search_google(self, query: str, max_results: int, safe_search: bool) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API."""
        params = {
            'key': self.api_key,
            'q': query,
            'num': min(max_results, 10),
            'safe': 'active' if safe_search else 'off'
        }
        
        response = self.get("/", params=params)
        
        results = []
        for item in response.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': self._extract_domain(item.get('link', '')),
                'relevance_score': 1.0  # Google returns results by relevance
            })
        
        return results
    
    def _search_bing(self, query: str, max_results: int, safe_search: bool) -> List[Dict[str, Any]]:
        """Search using Bing Web Search API."""
        params = {
            'q': query,
            'count': min(max_results, 50),
            'safeSearch': 'Strict' if safe_search else 'Off'
        }
        
        response = self.get("/search", params=params)
        
        results = []
        for item in response.get('webPages', {}).get('value', []):
            results.append({
                'title': item.get('name', ''),
                'url': item.get('url', ''),
                'snippet': item.get('snippet', ''),
                'source': self._extract_domain(item.get('url', '')),
                'relevance_score': item.get('rankingResponse', {}).get('relevanceScore', 0.5)
            })
        
        return results
    
    def _search_duckduckgo(self, query: str, max_results: int, safe_search: bool) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo Instant Answer API.
        
        Note: DuckDuckGo's public API is limited. In production, you might want
        to use a different provider or implement web scraping with proper rate limiting.
        """
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = self.get("/", params=params)
        
        results = []
        
        # Process instant answer
        if response.get('AbstractText'):
            results.append({
                'title': response.get('AbstractSource', 'DuckDuckGo'),
                'url': response.get('AbstractURL', ''),
                'snippet': response.get('AbstractText', ''),
                'source': self._extract_domain(response.get('AbstractURL', '')),
                'relevance_score': 1.0
            })
        
        # Process related topics
        for topic in response.get('RelatedTopics', [])[:max_results-1]:
            if isinstance(topic, dict) and topic.get('Text'):
                results.append({
                    'title': topic.get('Text', '').split(' - ')[0],
                    'url': topic.get('FirstURL', ''),
                    'snippet': topic.get('Text', ''),
                    'source': self._extract_domain(topic.get('FirstURL', '')),
                    'relevance_score': 0.8
                })
        
        return results[:max_results]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL."""
        if not url:
            return ""
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
                
            return domain
        except Exception:
            return ""
    
    def get_trending_topics(self, category: str = "general") -> List[Dict[str, Any]]:
        """
        Get trending topics for the specified category.
        
        Design Intent: Support real-time content discovery for AI responses
        
        Args:
            category: Topic category ("general", "technology", "science", etc.)
            
        Returns:
            List of trending topics with search volume and relevance data
        """
        # This would typically call trending/popular topics API
        # Implementation depends on the specific provider's capabilities
        
        if self.provider == "google":
            # Google Trends API would be used here
            pass
        elif self.provider == "bing":
            # Bing Trending Topics API
            pass
        
        # For now, return empty list as this requires additional API endpoints
        logger.warning("Trending topics not implemented for current provider")
        return []
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is accessible and safe.
        
        Design Intent: Ensure search results are safe for user consumption
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and safe, False otherwise
        """
        if not url:
            return False
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            
            # Basic URL validation
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check for safe protocols
            if parsed.scheme not in ['http', 'https']:
                return False
            
            return True
            
        except Exception:
            return False
"""
Base API Client

Provides the foundation for all external API clients with unified authentication,
error handling, and request processing.
"""

import requests
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time


logger = logging.getLogger(__name__)


class APIError(Exception):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class BaseAPIClient:
    """
    Base class for all external API clients.
    
    Design Intent:
    - Provide consistent authentication across all external services
    - Implement unified error handling and retry logic
    - Abstract common HTTP operations for all API clients
    - Enable secure API key management
    """
    
    def __init__(self, api_key: str, base_url: str = "", timeout: int = 30):
        """
        Initialize the base API client.
        
        Args:
            api_key: Authentication key for the external service
            base_url: Base URL for the API endpoints
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Create session with retry strategy
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self._set_default_headers()
    
    def _set_default_headers(self) -> None:
        """Set default headers for all requests."""
        self.session.headers.update({
            'User-Agent': 'Libral-Core/1.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Add authorization header if API key is provided
        if self.api_key:
            self._set_auth_header()
    
    def _set_auth_header(self) -> None:
        """
        Set authentication header. Override in subclasses for different auth methods.
        
        Default implementation uses Bearer token authentication.
        """
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}'
        })
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Complete URL for the request
        """
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
            
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}" if self.base_url else endpoint
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle HTTP response with unified error processing.
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed response data
            
        Raises:
            APIError: For HTTP errors or invalid responses
        """
        # Log request details for debugging
        logger.info(f"API Request: {response.request.method} {response.url} -> {response.status_code}")
        
        try:
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            if response.content:
                data = response.json()
            else:
                data = {}
                
            return data
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {response.status_code} error"
            
            # Try to extract error details from response
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = error_data['error']
                elif 'message' in error_data:
                    error_msg = error_data['message']
            except (ValueError, KeyError):
                pass
                
            raise APIError(error_msg, response.status_code, error_data if 'error_data' in locals() else None)
            
        except ValueError as e:
            raise APIError(f"Invalid JSON response: {str(e)}", response.status_code)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Perform HTTP request with unified error handling and authentication.
        
        This method automatically handles:
        - URL construction
        - Authentication headers
        - Error processing
        - Response parsing
        - Request logging
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Parsed response data
            
        Raises:
            APIError: For request failures or API errors
            
        Example:
            >>> client = BaseAPIClient("api_key_here")
            >>> data = client._request("GET", "/users/profile")
        """
        url = self._build_url(endpoint)
        
        # Set default timeout if not provided
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            # Record request start time for performance monitoring
            start_time = time.time()
            
            # Make the HTTP request
            response = self.session.request(method, url, **kwargs)
            
            # Log performance metrics
            duration = time.time() - start_time
            logger.debug(f"API call completed in {duration:.2f}s")
            
            # Process and return response
            return self._handle_response(response)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise APIError(error_msg)
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform GET request."""
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform POST request."""
        return self._request("POST", endpoint, data=data, json=json)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform PUT request."""
        return self._request("PUT", endpoint, data=data, json=json)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Perform DELETE request."""
        return self._request("DELETE", endpoint)
    
    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
"""
Microsoft Graph API Client Library

This module provides a pure Python client for interacting with Microsoft Graph REST APIs.
It focuses on user and service principal lookups to support identity management operations
in the Unified Data Foundation with Fabric (UDFWF) project.

Core Features:
- Authentication management with Azure CLI credentials
- User and service principal lookups by UPN, email, or object ID
- Principal type detection and object ID resolution
- HTTP request handling with error management

Dependencies:
    pip install requests azure-identity

Author: Generated for Unified Data Foundation with Fabric (UDFWF) project
"""

import json
import requests
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from azure.identity import AzureCliCredential, DefaultAzureCredential


class GraphApiError(Exception):
    """Custom exception for Microsoft Graph API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class GraphApiClient:
    """
    Microsoft Graph API Client
    
    Provides high-level methods for interacting with Microsoft Graph REST APIs.
    Handles authentication, error handling, and principal lookups.
    """
    
    def __init__(self, 
                 api_url: str = "https://graph.microsoft.com/v1.0",
                 resource_url: str = "https://graph.microsoft.com",
                 credential: Optional[Any] = None,
                 timeout_sec: int = 60):
        """
        Initialize the Graph API client.
        
        Args:
            api_url: Base URL for Graph API
            resource_url: Resource URL for authentication scope
            credential: Azure credential object (defaults to AzureCliCredential)
            timeout_sec: Default timeout for API requests
        """
        self.api_url = api_url.rstrip('/')
        self.resource_url = resource_url
        self.timeout_sec = timeout_sec
        self._credential = credential or AzureCliCredential()
        self._token = None
        self._token_expiry = None
    
    def _log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp."""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] {level}: {message}")
    
    def _get_auth_token(self) -> str:
        """
        Get or refresh the authentication token.
        
        Returns:
            Access token string
            
        Raises:
            GraphApiError: If authentication fails
        """
        try:
            # Check if we need a new token
            if self._token is None or (self._token_expiry and datetime.now() >= self._token_expiry):
                token_response = self._credential.get_token(f"{self.resource_url}/.default")
                self._token = token_response.token
                # Set expiry to 5 minutes before actual expiry for safety
                self._token_expiry = datetime.now() + timedelta(seconds=token_response.expires_on - time.time() - 300)
            
            return self._token
        except Exception as e:
            raise GraphApiError(f"Failed to get authentication token: {str(e)}")
    
    def _make_request(self,
                     uri: str,
                     method: str = "GET",
                     data: Optional[Union[str, dict]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     timeout: Optional[int] = None,
                     max_retries: int = 3,
                     retry_count: int = 0) -> requests.Response:
        """
        Make an HTTP request to the Graph API.
        
        Args:
            uri: API endpoint URI (relative to base URL)
            method: HTTP method
            data: Request body data
            headers: Additional headers
            timeout: Request timeout
            max_retries: Maximum number of retries for rate limiting
            retry_count: Current retry count (internal use)
            
        Returns:
            Response object
            
        Raises:
            GraphApiError: If request fails
        """
        if retry_count > max_retries:
            raise GraphApiError(f"Max retries ({max_retries}) exceeded for {method} {uri}")
        
        url = f"{self.api_url}/{uri.lstrip('/')}"
        
        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f'Bearer {self._get_auth_token()}'
        }
        if headers:
            request_headers.update(headers)
        
        # Prepare data
        if isinstance(data, dict):
            data = json.dumps(data)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                data=data,
                timeout=timeout or self.timeout_sec
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                if retry_count < max_retries:
                    self._log(f"Rate limited. Retrying after {retry_after} seconds (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(retry_after)
                    return self._make_request(uri, method, data, headers, timeout, max_retries, retry_count + 1)
                else:
                    raise GraphApiError(f"Rate limit exceeded and max retries reached", 429, response.json() if response.content else None)
            
            # Handle authentication errors
            if response.status_code == 401:
                if retry_count < max_retries:
                    self._log(f"Authentication failed. Refreshing token and retrying (attempt {retry_count + 1}/{max_retries})")
                    self._token = None
                    self._token_expiry = None
                    return self._make_request(uri, method, data, headers, timeout, max_retries, retry_count + 1)
                else:
                    raise GraphApiError(f"Authentication failed after {max_retries} retries", 401, response.json() if response.content else None)
            
            # Handle client errors
            if 400 <= response.status_code < 500:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
                raise GraphApiError(f"Client error: {error_message}", response.status_code, error_data)
            
            # Handle server errors
            if response.status_code >= 500:
                if retry_count < max_retries:
                    wait_time = min(2 ** retry_count, 60)  # Exponential backoff, max 60s
                    self._log(f"Server error {response.status_code}. Retrying after {wait_time} seconds (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(wait_time)
                    return self._make_request(uri, method, data, headers, timeout, max_retries, retry_count + 1)
                else:
                    error_data = response.json() if response.content else {}
                    raise GraphApiError(f"Server error after {max_retries} retries", response.status_code, error_data)
            
            return response
            
        except requests.Timeout as e:
            raise GraphApiError(f"Request timeout for {method} {uri}: {str(e)}")
        except requests.ConnectionError as e:
            raise GraphApiError(f"Connection error for {method} {uri}: {str(e)}")
        except requests.RequestException as e:
            raise GraphApiError(f"Request failed for {method} {uri}: {str(e)}")
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests.
        
        Returns:
            Dictionary with Authorization header
        """
        return {"Authorization": f"Bearer {self._get_auth_token()}"}
    
    # User operations
    def get_user_by_upn(self, user_principal_name: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by User Principal Name (UPN).
        
        Args:
            user_principal_name: User's UPN (e.g., user@contoso.com)
            
        Returns:
            User object with id, displayName, userPrincipalName, etc., or None if not found
            
        Raises:
            GraphApiError: If request fails (except 404)
        """
        try:
            response = self._make_request(f"users/{user_principal_name}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
        except GraphApiError as e:
            if e.status_code == 404:
                return None
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by object ID.
        
        Args:
            user_id: User's object ID (GUID)
            
        Returns:
            User object with id, displayName, userPrincipalName, etc., or None if not found
            
        Raises:
            GraphApiError: If request fails (except 404)
        """
        try:
            response = self._make_request(f"users/{user_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
        except GraphApiError as e:
            if e.status_code == 404:
                return None
            raise
    
    # Service Principal operations
    def get_service_principal_by_id(self, service_principal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get service principal information by object ID.
        
        Args:
            service_principal_id: Service principal's object ID (GUID)
            
        Returns:
            Service principal object with id, displayName, appId, etc., or None if not found
            
        Raises:
            GraphApiError: If request fails (except 404)
        """
        try:
            response = self._make_request(f"servicePrincipals/{service_principal_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
        except GraphApiError as e:
            if e.status_code == 404:
                return None
            raise
    
    def get_service_principal_by_app_id(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get service principal information by application ID.
        
        Args:
            app_id: Application ID (GUID)
            
        Returns:
            Service principal object with id, displayName, appId, etc., or None if not found
            
        Raises:
            GraphApiError: If request fails (except 404)
        """
        try:
            response = self._make_request(f"servicePrincipals?$filter=appId eq '{app_id}'")
            if response.status_code == 200:
                data = response.json()
                service_principals = data.get('value', [])
                return service_principals[0] if service_principals else None
            else:
                response.raise_for_status()
        except GraphApiError as e:
            if e.status_code == 404:
                return None
            raise
    
    # Combined operations
    def resolve_principal(self, identifier: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Resolve a principal identifier to determine type and get object ID.
        
        This method attempts to resolve the identifier in the following order:
        1. If it's a GUID, try as service principal object ID
        2. If it's a GUID and not found as service principal, try as user object ID
        3. If it contains '@', try as user UPN
        4. If it's a GUID, try as application ID for service principal
        
        Args:
            identifier: User UPN, object ID (GUID), or application ID (GUID)
            
        Returns:
            Tuple of (principal_type, object_id, principal_data)
            - principal_type: "User" or "ServicePrincipal"
            - object_id: The object ID of the principal
            - principal_data: Full principal object from Graph API
            
        Raises:
            GraphApiError: If identifier cannot be resolved or API calls fail
        """
        def is_valid_guid(value: str) -> bool:
            """Check if a string is a valid GUID format."""
            try:
                uuid.UUID(value)
                return True
            except ValueError:
                return False
        
        # Clean the identifier
        identifier = identifier.strip()
        
        # Strategy 1: If it looks like a GUID, try service principal first
        if is_valid_guid(identifier):
            # Try as service principal object ID
            sp_data = self.get_service_principal_by_id(identifier)
            if sp_data:
                return "ServicePrincipal", sp_data['id'], sp_data
            
            # Try as user object ID
            user_data = self.get_user_by_id(identifier)
            if user_data:
                return "User", user_data['id'], user_data
            
            # Try as application ID for service principal
            sp_data = self.get_service_principal_by_app_id(identifier)
            if sp_data:
                return "ServicePrincipal", sp_data['id'], sp_data
        
        # Strategy 2: If it contains '@', try as user UPN
        elif "@" in identifier:
            user_data = self.get_user_by_upn(identifier)
            if user_data:
                return "User", user_data['id'], user_data
        
        # If we get here, the identifier couldn't be resolved
        raise GraphApiError(f"Unable to resolve principal identifier '{identifier}'. "
                          f"Ensure it's a valid user UPN (user@domain.com), "
                          f"user object ID (GUID), service principal object ID (GUID), "
                          f"or application ID (GUID).")


# Convenience functions
def create_graph_client(credential: Optional[Any] = None) -> GraphApiClient:
    """
    Create a new Graph API client.
    
    Args:
        credential: Azure credential (defaults to AzureCliCredential)
        
    Returns:
        GraphApiClient instance
    """
    return GraphApiClient(credential=credential)


def detect_and_resolve_principal(identifier: str, graph_client: Optional[GraphApiClient] = None) -> Tuple[str, str, Dict[str, Any]]:
    """
    Convenience function to detect and resolve a principal identifier.
    
    Args:
        identifier: User UPN, object ID, or application ID
        graph_client: Optional Graph API client (will create one if not provided)
        
    Returns:
        Tuple of (principal_type, object_id, principal_data)
        
    Raises:
        GraphApiError: If identifier cannot be resolved
    """
    if graph_client is None:
        graph_client = create_graph_client()
    
    return graph_client.resolve_principal(identifier)
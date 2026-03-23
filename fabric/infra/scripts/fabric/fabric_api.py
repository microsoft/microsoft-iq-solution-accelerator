"""
Microsoft Fabric API Client Library

This module provides a pure Python client for interacting with Microsoft Fabric REST APIs.
It focuses on core API operations including authentication, request management, and 
low-level methods for Fabric resources (workspaces, folders, notebooks, items).

This library adheres strictly to Fabric API operations and does not contain business logic
or project-specific transformations. For UDFWF-specific functionality, see udfwf_utils.py.

Core Features:
- Authentication management with Azure CLI credentials
- HTTP request handling with error management
- Long Running Operation (LRO) support
- Workspace, folder, notebook, and item operations
- OneLake file system client integration

Dependencies:
    pip install requests azure-identity azure-storage-file-datalake

Author: Generated for Unified Data Foundation with Fabric (UDFWF) project
"""

import time
import json
import requests
from typing import Dict, List, Optional, Union, Any
from azure.identity import AzureCliCredential


class FabricApiError(Exception):
    """Custom exception for Fabric API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class FabricApiClient:
    """
    Microsoft Fabric API Client
    
    Provides high-level methods for interacting with Microsoft Fabric REST APIs.
    Handles authentication, error handling, and long-running operations.
    
    Note: For workspace-specific operations, consider using FabricWorkspaceApiClient
    which provides the same functionality without requiring workspace_id parameters.
    """
    
    def __init__(self, 
                 api_url: str = "https://api.fabric.microsoft.com/v1",
                 resource_url: str = "https://api.fabric.microsoft.com",
                 credential: Optional[Any] = None,
                 timeout_sec: int = 240):
        """
        Initialize the Fabric API client.
        
        Args:
            api_url: Base URL for Fabric API
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
        icon = ""
        if level == "ERROR":
            icon = "❌"
        elif level == "WARNING":
            icon = "⚠️"
        print(f"{icon} {message}")
    
    def _format_duration(self, elapsed_seconds: float) -> str:
        """Format elapsed time consistently in minutes format.
        
        Args:
            elapsed_seconds: Elapsed time in seconds
            
        Returns:
            Formatted duration string (e.g., "5m 30s", "0m 45s")
        """
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)
        return f"{minutes}m {seconds}s"
    
    def _get_auth_token(self) -> str:
        """
        Get or refresh the authentication token.
        
        Returns:
            Access token string
            
        Raises:
            FabricApiError: If authentication fails
        """
        try:
            # Check if we need to refresh the token
            if not self._token or (self._token_expiry and time.time() > self._token_expiry - 300):
                self._log("Getting authentication token")
                token_response = self._credential.get_token(f"{self.resource_url}/.default")
                self._token = token_response.token
                self._token_expiry = token_response.expires_on if hasattr(token_response, 'expires_on') else None
                self._log("Authentication successful")
            
            return self._token
        except Exception as e:
            raise FabricApiError(f"Authentication failed: {str(e)}")
    
    def _make_request(self,
                     uri: str,
                     method: str = "GET",
                     data: Optional[Union[str, dict]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     timeout: Optional[int] = None,
                     wait_for_lro: bool = True,
                     max_retries: int = 3,
                     retry_count: int = 0) -> requests.Response:
        """
        Make an HTTP request to the Fabric API.
        
        Args:
            uri: API endpoint URI (relative to base URL)
            method: HTTP method
            data: Request body data
            headers: Additional headers
            timeout: Request timeout
            wait_for_lro: Whether to wait for long running operations to complete
            max_retries: Maximum number of retries for rate limiting
            retry_count: Current retry count (internal use)
            
        Returns:
            Response object
            
        Raises:
            FabricApiError: If request fails
        """
        if retry_count > max_retries:
            raise FabricApiError(f"Maximum retries ({max_retries}) exceeded for rate limiting")
        
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
            self._log(f"Making {method} request to {url} (attempt {retry_count + 1})")
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                data=data,
                timeout=timeout or self.timeout_sec
            )
            
            # Log request ID if available
            request_id = response.headers.get('requestId', 'N/A')
            self._log(f"Request ID: {request_id}")
            
            # Handle Long Running Operations (LRO)
            if response.status_code == 202 and wait_for_lro:
                location = response.headers.get('Location')
                if location:
                    return self._wait_for_lro_completion(
                        job_url=location,
                        operation_name=f"{method} {uri}",
                        max_wait_time=1800
                    )
                else:
                    self._log("Long-running operation detected but no Location header found", "WARNING")
                
            elif response.status_code == 202 and not wait_for_lro:
                self._log("Long-running operation detected, returning 202 response without waiting")
            
            elif response.status_code == 429:
                # Handle rate limiting with exponential backoff
                retry_after_header = response.headers.get('Retry-After', '60')
                
                # Parse retry-after header (could be seconds or HTTP date)
                try:
                    retry_after = int(retry_after_header)
                except ValueError:
                    # If it's not a number, assume it's an HTTP date (not implemented here)
                    retry_after = min(60, 2 ** retry_count)  # Exponential backoff with cap
                
                # Cap the retry time to reasonable limits
                retry_after = min(retry_after, 300)  # Max 5 minutes
                
                self._log(f"Rate limit exceeded. Retrying in {retry_after} seconds... (attempt {retry_count + 1}/{max_retries})", "WARNING")
                time.sleep(retry_after)
                
                # Recursive call with retry count
                return self._make_request(uri, method, data, headers, timeout, wait_for_lro, max_retries, retry_count + 1)
            
            # Check for errors
            elif response.status_code >= 400:
                error_msg = f"API request failed with status {response.status_code}"
                error_data = None
                
                try:
                    error_response = response.json()
                    if 'error' in error_response:
                        error_data = error_response['error']
                        error_msg += f": {error_data.get('message', 'Unknown error')}"
                except (ValueError, json.JSONDecodeError):
                    error_msg += f": {response.text[:500]}"  # Limit error text length
                
                raise FabricApiError(error_msg, response.status_code, error_data)
            
            self._log("Request completed successfully")
            return response
            
        except requests.Timeout as e:
            raise FabricApiError(f"Request timed out after {timeout or self.timeout_sec} seconds: {str(e)}")
        except requests.ConnectionError as e:
            raise FabricApiError(f"Connection error: {str(e)}")
        except requests.RequestException as e:
            raise FabricApiError(f"Request failed: {str(e)}")
    
    def _wait_for_lro_completion(self, 
                                   job_url: str, 
                                   operation_name: Optional[str] = None,
                                   max_wait_time: int = 1800, 
                                   check_interval: Optional[int] = None) -> requests.Response:
        """
        Wait for Long Running Operation to complete.
        
        This method polls the LRO status endpoint until completion, handling both standard
        HTTP status-based LROs (202 → 200) and Fabric-specific job status responses.
        
        Args:
            job_url: Full URL for monitoring the operation (including base URL)
            operation_name: Optional name for logging purposes only (e.g., "notebook creation")
            max_wait_time: Maximum time to wait in seconds (default: 1800 = 30 minutes)
            check_interval: Check interval in seconds (defaults to Retry-After header or 5s)
            
        Returns:
            Final response object with status 200
            
        Raises:
            FabricApiError: If operation fails, times out, or polling encounters errors
        """
        start_time = time.time()
        default_interval = check_interval or 5
        
        # Log operation start
        operation_display = operation_name if operation_name else "operation"
        self._log(f"Waiting for operation '{operation_display}' to complete...")
        
        while (time.time() - start_time) < max_wait_time:
            time.sleep(default_interval)
            
            try:
                # Make direct HTTP request to the job URL
                headers = {'Authorization': f'Bearer {self._get_auth_token()}'}
                response = requests.get(job_url, headers=headers, timeout=self.timeout_sec)
                
                if response.status_code == 200:
                    # Try to parse response and check for job status field
                    # Some Fabric operations (like notebook jobs) return 200 with a status field
                    try:
                        job_data = response.json()
                        
                        # Check if response contains a status field indicating job state
                        if 'status' in job_data:
                            job_status = job_data['status']
                            
                            # If job is still running, continue polling
                            if job_status in ['InProgress', 'Running', 'Queued', 'NotStarted']:
                                elapsed = time.time() - start_time
                                elapsed_str = self._format_duration(elapsed)
                                self._log(f"Operation '{operation_display}' status: '{job_status}' ({elapsed_str} elapsed)")
                                continue
                            
                            # If job failed, raise error with details
                            elif job_status in ['Failed', 'Cancelled']:
                                error_msg = job_data.get('failureReason', {}).get('message', 'Operation failed')
                                error_code = job_data.get('failureReason', {}).get('errorCode', 'Unknown')
                                error_message = f"Operation '{operation_display}' status: '{job_status}': {error_msg} (Code: {error_code})"
                                self._log(error_message, level="ERROR")
                                raise FabricApiError(
                                    error_message,
                                    status_code=None,
                                    response_data=job_data
                                )
                            
                            # If job completed successfully
                            elif job_status in ['Completed', 'Succeeded']:
                                elapsed_str = self._format_duration(time.time() - start_time)
                                self._log(f"Operation '{operation_display}' completed successfully ({elapsed_str})")
                                return response
                            
                            # Unknown status - log warning but treat as completed
                            else:
                                self._log(f"Operation '{operation_display}' returned unknown status '{job_status}', treating as completed", level="WARNING")
                                return response
                        else:
                            # No status field - standard HTTP LRO (200 means complete)
                            elapsed_str = self._format_duration(time.time() - start_time)
                            self._log(f"Operation '{operation_display}' completed successfully ({elapsed_str})")
                            return response
                            
                    except (ValueError, json.JSONDecodeError):
                        # Response is not JSON - treat 200 as successful completion
                        elapsed_str = self._format_duration(time.time() - start_time)
                        self._log(f"Operation '{operation_display}' completed successfully ({elapsed_str})")
                        return response
                
                elif response.status_code == 202:
                    # Standard LRO - still in progress
                    elapsed = time.time() - start_time
                    elapsed_str = self._format_duration(elapsed)
                    self._log(f"Operation '{operation_display}' still in progress ({elapsed_str} elapsed)")
                    
                    # Update check interval from Retry-After header if not explicitly set
                    if not check_interval:
                        retry_after = response.headers.get('Retry-After')
                        if retry_after:
                            try:
                                default_interval = min(int(retry_after), 60)  # Cap at 60 seconds
                            except ValueError:
                                pass  # Keep current interval if header is not a valid integer
                    continue
                
                elif response.status_code == 404:
                    # Job URL not found - might indicate completion or deletion
                    self._log(f"Operation '{operation_display}' job URL returned 404, operation may have completed", level="WARNING")
                    return response
                
                else:
                    # Unexpected status code
                    error_msg = f"Operation '{operation_display}' failed with HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        if 'error' in error_data:
                            error_msg += f": {error_data['error'].get('message', response.text[:200])}"
                    except:
                        error_msg += f": {response.text[:200]}"
                    
                    self._log(error_msg, level="ERROR")
                    raise FabricApiError(error_msg, status_code=response.status_code)
                    
            except FabricApiError:
                raise
            except requests.RequestException as e:
                error_msg = f"Error polling operation '{operation_display}' status: {str(e)}"
                self._log(error_msg, level="ERROR")
                raise FabricApiError(error_msg)
        
        # Timeout reached
        elapsed_str = self._format_duration(max_wait_time)
        error_msg = f"Operation '{operation_display}' timed out after {elapsed_str}"
        self._log(error_msg, level="ERROR")
        raise FabricApiError(error_msg)
    
    # Capacity operations
    def list_capacities(self) -> List[Dict[str, Any]]:
        """
        Get all capacities accessible to the user.
        
        Returns:
            List of capacity objects containing:
            - id: Capacity ID (GUID)
            - displayName: Capacity display name
            - sku: Capacity SKU (e.g., "F2", "F4", "P1", etc.)
            - state: Capacity state ("Active", "Paused", "Suspended", etc.)
            - region: Azure region where capacity is located
            - admins: List of capacity administrators
            - contributors: List of capacity contributors (if any)
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Capacity.Read.All or Capacity.ReadWrite.All
        """
        self._log("Getting all capacities accessible to user")
        
        try:
            response = self._make_request("capacities")
            capacities = response.json().get('value', [])
            self._log(f"Found {len(capacities)} capacity(ies)")
            return capacities
                
        except FabricApiError:
            raise
        except Exception as e:
            raise FabricApiError(f"Failed to get capacities: {str(e)}")

    def get_capacity(self, capacity_name: str) -> Optional[Dict[str, Any]]:
        """
        Get capacity by name.
        
        Args:
            capacity_name: Name of the capacity
            
        Returns:
            Capacity object if found, None otherwise
            
        Raises:
            FabricApiError: If request fails
        """
        capacities = self.list_capacities()
        capacity = next((c for c in capacities if c['displayName'].lower() == capacity_name.lower()), None)
        
        if not capacity:
            self._log(f"Capacity '{capacity_name}' not found")
            return None
        
        return capacity

    # Workspace operations
    def list_workspaces(self) -> List[Dict[str, Any]]:
        """
        Get all workspaces accessible to the user.
        
        Returns:
            List of workspace objects
            
        Raises:
            FabricApiError: If request fails
        """
        try:
            response = self._make_request("workspaces")
            
            if response.status_code == 200:
                workspaces = response.json().get('value', [])
                self._log(f"Found {len(workspaces)} workspaces")
                return workspaces
            else:
                error_msg = f"Failed to get workspaces: HTTP {response.status_code}"
                self._log(error_msg, level="ERROR")
                raise FabricApiError(error_msg)
                
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error getting workspaces: {e}"
            self._log(error_msg, level="ERROR")
            raise FabricApiError(error_msg)
    
    def get_workspace(self, workspace_name: str) -> Optional[Dict[str, Any]]:
        """
        Get workspace by name.
        
        Args:
            workspace_name: Name of the workspace
            
        Returns:
            Workspace object if found, None otherwise
            
        Raises:
            FabricApiError: If request fails
        """
        workspaces = self.list_workspaces()
        workspace = next((w for w in workspaces if w['displayName'].lower() == workspace_name.lower()), None)
        
        if not workspace:
            self._log(f"Workspace '{workspace_name}' not found")
            return None
        
        return workspace
    
    def create_workspace(self, name: str, capacity_id: Optional[str] = None) -> str:
        """
        Create a new workspace.
        
        Args:
            name: Workspace name
            capacity_id: Optional capacity ID
            
        Returns:
            Workspace ID
        """
        data = {'displayName': name}
        if capacity_id:
            data['capacityId'] = capacity_id
        
        response = self._make_request("workspaces", method="POST", data=data)
        return response.json()['id']
    
    def assign_workspace_to_capacity(self, workspace_id: str, capacity_id: str) -> None:
        """
        Assign a workspace to a capacity.
        
        Args:
            workspace_id: ID of the workspace to assign
            capacity_id: ID of the capacity to assign to
            
        Raises:
            FabricApiError: If assignment fails
            
        Required Scopes:
            Workspace.ReadWrite.All
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/assign-to-capacity
        """
        self._log(f"Assigning workspace {workspace_id} to capacity {capacity_id}")
        
        data = {"capacityId": capacity_id}
        
        response = self._make_request(
            f"workspaces/{workspace_id}/assignToCapacity", 
            method="POST", 
            data=data
        )
        
        if response.status_code == 200 or response.status_code == 202:
            self._log(f"Successfully assigned workspace to capacity")
        else:
            error_msg = f"Failed to assign workspace to capacity: HTTP {response.status_code}"
            self._log(error_msg, level="ERROR")
            raise FabricApiError(error_msg)
    
    def delete_workspace(self, workspace_id: str) -> Optional[str]:
        """
        Delete a workspace.
        
        Args:
            workspace_id: ID of the workspace to delete
            
        Returns:
            Workspace ID if successfully deleted, None if workspace not found
            
        Raises:
            FabricApiError: If deletion fails due to unexpected error
            
        Required Scopes:
            Workspace.ReadWrite.All
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/delete-workspace
        """
        try:
            self._log(f"Deleting workspace {workspace_id}")
            
            response = self._make_request(
                f"workspaces/{workspace_id}", 
                method="DELETE"
            )
            
            if response.status_code == 200:
                self._log(f"Successfully deleted workspace")
                return workspace_id
            elif response.status_code == 404:
                self._log(f"Workspace {workspace_id} not found, nothing to delete")
                return None
            else:
                error_msg = f"Failed to delete workspace: HTTP {response.status_code}"
                self._log(error_msg, level="ERROR")
                raise FabricApiError(error_msg)
                
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error deleting workspace: {e}"
            self._log(error_msg, level="ERROR")
            raise FabricApiError(error_msg)



class FabricWorkspaceApiClient(FabricApiClient):
    """
    Fabric API client scoped to a specific workspace.
    
    This class inherits from FabricApiClient and provides workspace-specific methods
    without requiring workspace_id as a parameter for each method call.
    """
    
    def __init__(self, 
                 workspace_id: str,
                 api_url: str = "https://api.fabric.microsoft.com/v1",
                 resource_url: str = "https://api.fabric.microsoft.com",
                 credential: Optional[Any] = None,
                 timeout_sec: int = 240):
        """
        Initialize the workspace-scoped Fabric API client.
        
        Args:
            workspace_id: Target workspace ID
            api_url: Base URL for Fabric API
            resource_url: Resource URL for authentication scope
            credential: Azure credential object (defaults to AzureCliCredential)
            timeout_sec: Default timeout for API requests
        """
        super().__init__(api_url, resource_url, credential, timeout_sec)
        self.workspace_id = workspace_id
        self._workspace_info = None  # Cache for workspace information
        self._log(f"Initialized FabricWorkspaceApiClient for workspace {workspace_id}")
    
    # Notebook operations
    def get_notebook(self, notebook_id: str) -> Dict[str, Any]:
        """
        Get properties of a specific notebook.
        
        Args:
            notebook_id: Notebook ID
            
        Returns:
            Notebook object containing:
            - id: Notebook ID (GUID)
            - displayName: Notebook display name
            - description: Notebook description
            - type: Item type ("Notebook")
            - workspaceId: Workspace ID (GUID)
            - properties: Notebook properties
            - folderId: Folder ID (if in a folder)
            - definition: Notebook definition (if requested)
            
        Raises:
            FabricApiError: If notebook not found or request fails
            
        Required Scopes:
            Notebook.Read.All or Notebook.ReadWrite.All or Item.Read.All or Item.ReadWrite.All
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/notebook/items/get-notebook
        """
        self._log(f"Getting notebook {notebook_id} from workspace {self.workspace_id}")
        response = self._make_request(f"workspaces/{self.workspace_id}/notebooks/{notebook_id}")
        notebook = response.json()
        self._log(f"Retrieved notebook '{notebook.get('displayName', 'Unknown')}'")
        return notebook
    
    def create_notebook(self, notebook_name: str, notebook_data_base64: str, folder_id: Optional[str] = None, wait_for_lro: bool = True) -> Union[Dict[str, Any], requests.Response]:
        """
        Create a new notebook in the workspace.
        
        Args:
            notebook_name: Display name for the notebook
            notebook_data_base64: Base64-encoded notebook JSON content
            folder_id: Optional ID of the folder to create the notebook in
            wait_for_lro: Whether to wait for long running operations to complete
            
        Returns:
            If wait_for_lro=True: Dictionary with notebook information (may be empty for LROs; use get_notebook_by_name() to retrieve details)
            If wait_for_lro=False: Response object for batch processing
            
        Raises:
            FabricApiError: If creation fails
        """
        try:
            self._log(f"Creating notebook '{notebook_name}' in workspace {self.workspace_id}")
            
            # Construct the notebook data structure
            notebook_data = {
                "displayName": notebook_name,
                "definition": {
                    "format": "ipynb",
                    "parts": [{
                        "path": "notebook-content.ipynb",
                        "payload": notebook_data_base64,
                        "payloadType": "InlineBase64"
                    }]
                }
            }
            
            # Add folder ID if specified
            if folder_id:
                notebook_data["folderId"] = folder_id
            
            response = self._make_request(
                f"workspaces/{self.workspace_id}/notebooks", 
                method="POST", 
                data=notebook_data, 
                wait_for_lro=wait_for_lro
            )
            
            # Return raw response for batch processing
            if not wait_for_lro:
                return response
            
            # Parse and return response content for synchronous operations
            if response.status_code in [200, 201, 202]:
                if response.content and response.content != b'null':
                    return response.json()
                return {}
            else:
                raise FabricApiError(f"Failed to create notebook: HTTP {response.status_code}")
                
        except FabricApiError:
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error creating notebook: {str(e)}")
    
    def update_notebook(self, notebook_id: str, notebook_data_base64: str, wait_for_lro: bool = True) -> Union[Dict[str, Any], requests.Response]:
        """
        Update an existing notebook in the workspace.
        
        Args:
            notebook_id: Notebook ID to update
            notebook_data_base64: Base64-encoded notebook JSON content
            wait_for_lro: Whether to wait for long running operations to complete
            
        Returns:
            If wait_for_lro=True: Dictionary with update result (may be empty for LROs; use get_notebook() to retrieve details)
            If wait_for_lro=False: Response object for batch processing
            
        Raises:
            FabricApiError: If update fails
        """
        try:
            self._log(f"Updating notebook ({notebook_id}) in workspace {self.workspace_id}")
            
            # Construct the notebook data structure
            notebook_data = {
                "definition": {
                    "format": "ipynb",
                    "parts": [{
                        "path": "notebook-content.ipynb",
                        "payload": notebook_data_base64,
                        "payloadType": "InlineBase64"
                    }]
                }
            }
            
            response = self._make_request(
                f"workspaces/{self.workspace_id}/notebooks/{notebook_id}/updateDefinition", 
                method="POST", 
                data=notebook_data,
                wait_for_lro=wait_for_lro
            )
            
            # Return raw response for batch processing
            if not wait_for_lro:
                return response
            
            # Parse and return response content for synchronous operations
            if response.status_code in [200, 202]:
                if response.content and response.content != b'null':
                    return response.json()
                return {}
            else:
                raise FabricApiError(f"Failed to update notebook: HTTP {response.status_code}")
                
        except FabricApiError:
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error updating notebook: {str(e)}")
    
    def get_notebook_by_name(self, notebook_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a notebook by name from the workspace.
        
        Args:
            notebook_name: The name of the notebook to find
            
        Returns:
            Dictionary with notebook information if found, None otherwise
            
        Raises:
            FabricApiError: If listing fails
        """
        try:
            # Validate required parameters
            if not notebook_name or not notebook_name.strip():
                raise FabricApiError("notebook_name is required and cannot be empty")
            
            self._log(f"Searching for notebook '{notebook_name}' in workspace {self.workspace_id}")
            
            # Get all notebooks (raw list)
            response = self._make_request(f"workspaces/{self.workspace_id}/notebooks")
            
            if response.status_code == 200:
                notebooks = response.json().get('value', [])
                
                # Find the notebook by name
                for notebook in notebooks:
                    if notebook.get('displayName', '').strip() == notebook_name.strip():
                        self._log(f"Found notebook '{notebook_name}' with ID: {notebook.get('id', 'N/A')}")
                        return notebook
                
                self._log(f"Notebook '{notebook_name}' not found")
                return None
            else:
                raise FabricApiError(f"Failed to list notebooks: HTTP {response.status_code}")
                
        except FabricApiError:
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error searching for notebook '{notebook_name}': {str(e)}")
    
    # Notebook execution operations
    def schedule_notebook_job(self, notebook_id: str, monitor_interval: int = 20) -> Dict[str, Any]:
        """
        Schedule a single notebook job and monitor its completion.
        
        Args:
            notebook_id: Notebook ID to execute
            monitor_interval: Seconds to wait between status checks (default: 20)
            
        Returns:
            Dictionary with execution results including status, duration, and details
            
        Raises:
            FabricApiError: If execution fails or notebook not found
        """
        
        try:
            job_url = f"workspaces/{self.workspace_id}/items/{notebook_id}/jobs/instances?jobType=RunNotebook"
            start_time = time.time()

            # Verify notebook exists before executing
            notebook_info = self.get_notebook(notebook_id)
            if not notebook_info:
                raise FabricApiError(f"Notebook with ID '{notebook_id}' not found in workspace {self.workspace_id}")
            notebook_name = notebook_info.get('displayName', 'Unknown')
            
            self._log(f"Scheduling execution for notebook '{notebook_name}' (ID: {notebook_id})")
            response = self._make_request(job_url, method="POST", wait_for_lro=False)
            
            # Handle immediate completion (HTTP 200)
            if response.status_code == 200:
                job_data = response.json() if response.content else {}
                duration_str = self._format_duration(time.time() - start_time)
                self._log(f"Notebook '{notebook_name}' (ID: {notebook_id}) completed immediately (synchronous)")
                return {'status': 'Completed', 'duration': duration_str, 'details': job_data}
            
            # Handle Long Running Operation (HTTP 202)
            if response.status_code == 202:
                job_monitoring_url = response.headers.get('location')
                if not job_monitoring_url:
                    error_msg = 'No location header in 202 response'
                    self._log(f"Failed to start notebook {notebook_id}: {error_msg}", "ERROR")
                    return {'status': 'Failed', 'error': error_msg}
                
                # Monitor the long-running operation
                try:
                    lro_response = self._wait_for_lro_completion(
                        job_url=job_monitoring_url,
                        operation_name=f"Run notebook '{notebook_name}' (ID: {notebook_id})",
                        max_wait_time=1800,  # 30 minutes for notebook execution
                        check_interval=monitor_interval
                    )
                    
                    # Calculate duration
                    elapsed_time = time.time() - start_time
                    duration_str = self._format_duration(elapsed_time)
                    
                    # Parse response to extract job status
                    if lro_response.status_code == 200:
                        try:
                            job_data = lro_response.json()
                            job_status = job_data.get('status', 'Completed')
                            
                            return {
                                'status': job_status,
                                'duration': duration_str,
                                'details': job_data
                            }
                        except (ValueError, KeyError):
                            # Response doesn't have JSON or status field - treat as completed
                            return {
                                'status': 'Completed',
                                'duration': duration_str,
                                'details': {}
                            }
                            
                    else:
                        return {
                            'status': 'Failed',
                            'duration': duration_str,
                            'error': f"Unexpected response status: {lro_response.status_code}"
                        }
                        
                except FabricApiError as e:
                    elapsed_time = time.time() - start_time
                    duration_str = self._format_duration(elapsed_time)
                    
                    # Determine if it's a timeout or other error
                    if "timed out" in str(e):
                        return {
                            'status': 'Timeout',
                            'duration': duration_str,
                            'error': str(e)
                        }
                    else:
                        return {
                            'status': 'Failed',
                            'duration': duration_str,
                            'error': str(e)
                        }
            
            # Handle errors (HTTP 4xx/5xx)
            if response.status_code >= 400:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self._log(f"Failed to start notebook {notebook_id}: {error_msg}", "ERROR")
                return {'status': 'Failed', 'error': error_msg}
            
            # Handle unexpected status codes
            error_msg = f"Unexpected HTTP status {response.status_code}: {response.text}"
            self._log(f"Unexpected response for notebook {notebook_id}: {error_msg}", "ERROR")
            return {'status': 'Failed', 'error': error_msg}
            
        except FabricApiError:
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            duration_str = self._format_duration(elapsed_time)
            raise FabricApiError(f"Unexpected error executing notebook {notebook_id}: {str(e)}")

    # Role assignment operations
    def add_role_assignment(self, 
                          principal_id: str, 
                          principal_type: str, 
                          role: str,
                          display_name: Optional[str] = None,
                          user_principal_name: Optional[str] = None,
                          aad_app_id: Optional[str] = None,
                          group_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a workspace role assignment to grant permissions to a user, service principal, or group.
        
        Args:
            principal_id: The principal's ID (user object ID, service principal ID, or group ID)
            principal_type: Type of principal ("User", "ServicePrincipal", "Group", "ServicePrincipalProfile", "EntireTenant")
            role: Workspace role ("Admin", "Member", "Contributor", "Viewer")
            display_name: Optional display name of the principal
            user_principal_name: Optional user principal name (required for User type)
            aad_app_id: Optional Azure AD App ID (required for ServicePrincipal type)
            group_type: Optional group type ("SecurityGroup", "DistributionList", "Unknown") for Group type
            
        Returns:
            WorkspaceRoleAssignment object containing:
            - id: Role assignment ID
            - principal: Principal object with ID, type, and details
            - role: Assigned workspace role
            
        Raises:
            FabricApiError: If role assignment fails
            
        Required Scopes:
            Workspace.ReadWrite.All
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/add-workspace-role-assignment
        """
        valid_principal_types = ["User", "ServicePrincipal", "Group", "ServicePrincipalProfile", "EntireTenant"]
        valid_roles = ["Admin", "Member", "Contributor", "Viewer"]
        valid_group_types = ["SecurityGroup", "DistributionList", "Unknown"]
        
        # Validate inputs
        if principal_type not in valid_principal_types:
            raise FabricApiError(f"Invalid principal_type '{principal_type}'. Must be one of: {valid_principal_types}")
        
        if role not in valid_roles:
            raise FabricApiError(f"Invalid role '{role}'. Must be one of: {valid_roles}")
        
        if group_type and group_type not in valid_group_types:
            raise FabricApiError(f"Invalid group_type '{group_type}'. Must be one of: {valid_group_types}")
        
        self._log(f"Adding {principal_type} role assignment '{role}' for principal {principal_id} to workspace {self.workspace_id}")
        
        # Build principal object
        principal = {
            "id": principal_id,
            "type": principal_type
        }
        
        # Add optional display name
        if display_name:
            principal["displayName"] = display_name
        
        # Add type-specific details
        if principal_type == "User" and user_principal_name:
            principal["userDetails"] = {
                "userPrincipalName": user_principal_name
            }
        elif principal_type == "ServicePrincipal" and aad_app_id:
            principal["servicePrincipalDetails"] = {
                "aadAppId": aad_app_id
            }
        elif principal_type == "Group" and group_type:
            principal["groupDetails"] = {
                "groupType": group_type
            }
        
        # Build request data
        data = {
            "principal": principal,
            "role": role
        }
        
        # Make the API request
        response = self._make_request(
            f"workspaces/{self.workspace_id}/roleAssignments", 
            method="POST", 
            data=data
        )
        
        if response.status_code == 201:
            role_assignment = response.json()
            self._log(f"Successfully added {role} role assignment for {principal_type} {principal_id}")
            return role_assignment
        else:
            error_msg = f"Failed to add workspace role assignment: HTTP {response.status_code}"
            self._log(error_msg, level="ERROR")
            raise FabricApiError(error_msg)
    
    def list_role_assignments(self,
                            continuation_token: Optional[str] = None,
                            get_all: bool = True) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Get workspace role assignments with support for pagination.
        
        Args:
            continuation_token: Optional token for retrieving the next page of results
            get_all: If True, retrieves all role assignments across all pages. 
                    If False, returns a single page with pagination info.
            
        Returns:
            If get_all=True: List of WorkspaceRoleAssignment objects
            If get_all=False: Dictionary containing:
                - value: List of WorkspaceRoleAssignment objects
                - continuationToken: Token for next page (if more results exist)
                - continuationUri: URI for next page (if more results exist)
            
            Each WorkspaceRoleAssignment contains:
            - id: Role assignment ID
            - principal: Principal object with ID, type, display name, and type-specific details
            - role: Workspace role ("Admin", "Member", "Contributor", "Viewer")
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/list-workspace-role-assignments
        """
        self._log(f"Getting workspace role assignments for workspace {self.workspace_id}")
        
        # Build query parameters
        params = []
        if continuation_token:
            params.append(f"continuationToken={continuation_token}")
        
        query_string = f"?{'&'.join(params)}" if params else ""
        uri = f"workspaces/{self.workspace_id}/roleAssignments{query_string}"
        
        # Make the API request
        response = self._make_request(uri)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if get_all:
                # Collect all role assignments across all pages
                all_role_assignments = response_data.get('value', [])
                
                # Continue fetching pages if continuation token exists
                while 'continuationToken' in response_data:
                    next_token = response_data['continuationToken']
                    self._log(f"Fetching next page of role assignments (token: {next_token[:20]}...)")
                    
                    next_params = [f"continuationToken={next_token}"]
                    next_query = f"?{'&'.join(next_params)}"
                    next_uri = f"workspaces/{self.workspace_id}/roleAssignments{next_query}"
                    
                    next_response = self._make_request(next_uri)
                    if next_response.status_code == 200:
                        next_data = next_response.json()
                        all_role_assignments.extend(next_data.get('value', []))
                        response_data = next_data
                    else:
                        error_msg = f"Failed to fetch next page of role assignments: HTTP {next_response.status_code}"
                        self._log(error_msg, level="ERROR")
                        raise FabricApiError(error_msg)
                
                self._log(f"Retrieved {len(all_role_assignments)} total role assignment(s)")
                # Return list directly when fetching all
                return all_role_assignments
            else:
                # Return response with pagination info
                role_assignments = response_data.get('value', [])
                self._log(f"Retrieved {len(role_assignments)} role assignment(s) in current page")
                return response_data
        else:
            error_msg = f"Failed to get workspace role assignments: HTTP {response.status_code}"
            self._log(error_msg, level="ERROR")
            raise FabricApiError(error_msg)
    

# Convenience functions
def create_fabric_client(credential: Optional[Any] = None) -> FabricApiClient:
    """
    Create a new Fabric API client.
    
    Args:
        credential: Azure credential (defaults to AzureCliCredential)
        
    Returns:
        FabricApiClient instance
        
    Note: For workspace-specific operations, consider using create_workspace_fabric_client()
    which provides cleaner APIs without workspace_id parameters.
    """
    return FabricApiClient(credential=credential)


def create_workspace_fabric_client(workspace_id: str, credential: Optional[Any] = None) -> FabricWorkspaceApiClient:
    """
    Create a new workspace-scoped Fabric API client.
    
    Args:
        workspace_id: Target workspace ID
        credential: Azure credential (defaults to AzureCliCredential)
        
    Returns:
        FabricWorkspaceApiClient instance
    """
    return FabricWorkspaceApiClient(workspace_id, credential=credential)

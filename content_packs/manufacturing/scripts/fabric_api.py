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
    pip install requests azure-identity

Author: Generated for Unified Data Foundation with Fabric (UDFWF) project
"""

import time
import json
import base64
import requests
from typing import Dict, List, Optional, Union, Any
from azure.identity import AzureCliCredential
from azure.storage.filedatalake import DataLakeServiceClient, FileSystemClient

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

    @staticmethod
    def _normalize_eventhub_endpoint(namespace_or_endpoint: str) -> str:
        """Normalize Event Hub endpoint to the connector-expected host format.

        Accepts either a bare namespace (e.g. "myns") or a full endpoint
        (e.g. "sb://myns.servicebus.windows.net/") and returns
        "myns.servicebus.windows.net".
        """
        endpoint = (namespace_or_endpoint or "").strip()
        if endpoint.startswith("sb://"):
            endpoint = endpoint[len("sb://"):]
        endpoint = endpoint.rstrip("/")
        if ".servicebus.windows.net" not in endpoint:
            endpoint = f"{endpoint}.servicebus.windows.net"
        return endpoint
    
    def start_long_running_operation(self,
                                   uri: str,
                                   method: str = "POST",
                                   data: Optional[Union[str, dict]] = None,
                                   headers: Optional[Dict[str, str]] = None,
                                   timeout: Optional[int] = None) -> requests.Response:
        """
        Start a long-running operation without waiting for completion.
        
        Args:
            uri: API endpoint URI (relative to base URL)
            method: HTTP method
            data: Request body data
            headers: Additional headers
            timeout: Request timeout
            
        Returns:
            Response object (typically 202 with Location header)
        """
        return self._make_request(uri, method, data, headers, timeout, wait_for_lro=False)
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests.
        
        Returns:
            Dictionary with Authorization header
        """
        return {"Authorization": f"Bearer {self._get_auth_token()}"}
    
    def get_workspace_file_system_client(self, workspace_name: str) -> FileSystemClient:
        """
        Create a Data Lake file system client for a Fabric workspace.
        
        Args:
            workspace_name: Name of the Fabric workspace
            
        Returns:
            FileSystemClient for OneLake operations
        """
        account_url = "https://onelake.dfs.fabric.microsoft.com"
        service_client = DataLakeServiceClient(account_url, credential=self._credential)
        return service_client.get_file_system_client(file_system=workspace_name)
    
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
                    self._log(f"Error response: {json.dumps(error_response, indent=2)}", level="error")

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
                                   max_wait_time: int = 300, 
                                   check_interval: Optional[int] = None) -> requests.Response:
        """
        Wait for Long Running Operation to complete.
        
        Args:
            job_url: Full URL for monitoring the operation (including base URL)
            operation_name: Optional name for logging (e.g., notebook name)
            max_wait_time: Maximum time to wait in seconds
            check_interval: Check interval in seconds (defaults to Retry-After header or 5s)
            
        Returns:
            Final response object
        """
        start_time = time.time()
        default_interval = check_interval or 5
        
        # Log operation start
        operation_display = f"'{operation_name}'" if operation_name else "operation"
        self._log(f"Waiting for {operation_display} to complete...")
        
        while (time.time() - start_time) < max_wait_time:
            time.sleep(default_interval)
            
            try:
                # Make direct HTTP request to the job URL
                headers = {'Authorization': f'Bearer {self._get_auth_token()}'}
                response = requests.get(job_url, headers=headers, timeout=self.timeout_sec)
                
                if response.status_code == 200:
                    # For notebook operations, check if the job status indicates completion
                    if operation_name:  # This indicates it's likely a notebook job
                        try:
                            job_data = response.json()
                            job_status = job_data.get('status', 'Completed')
                            
                            # If job is still running, continue polling
                            if job_status in ['InProgress', 'Running', 'Queued', 'NotStarted']:
                                elapsed = time.time() - start_time
                                elapsed_str = self._format_duration(elapsed)
                                self._log(f"{operation_display} is {job_status.lower()}... ({elapsed_str} elapsed)")
                                continue
                            # If job completed successfully, return response
                            elif job_status in ['Completed', 'Succeeded']:
                                self._log(f"{operation_display} completed successfully")
                                return response
                            # If job failed or was cancelled, raise an exception
                            elif job_status == 'Failed':
                                error_message = f"{operation_display} failed"
                                # Try to extract error details from the response
                                try:
                                    error_details = job_data.get('error', {})
                                    if error_details:
                                        error_code = error_details.get('code', 'Unknown')
                                        error_desc = error_details.get('message', 'No details available')
                                        error_message = f"{operation_display} failed with error {error_code}: {error_desc}"
                                except Exception as e:
                                    self._log(f"Could not extract error details: {e}", "DEBUG")
                                raise FabricApiError(error_message)
                            elif job_status == 'Cancelled':
                                raise FabricApiError(f"{operation_display} was cancelled")
                            else:
                                # Unknown status - log warning and treat as completed
                                self._log(f"{operation_display} has unknown status '{job_status}', treating as completed", "WARNING")
                                return response
                        except (ValueError, KeyError):
                            # No JSON or status field - treat as completed
                            pass
                    
                    self._log(f"{operation_display} completed successfully")
                    return response
                elif response.status_code == 202:
                    self._log(f"{operation_display} still in progress...")
                    # Update check interval from Retry-After header if not explicitly set
                    if not check_interval:
                        default_interval = int(response.headers.get('Retry-After', default_interval))
                    continue
                else:
                    raise FabricApiError(f"{operation_display} failed with status {response.status_code}: {response.text}")
                    
            except requests.RequestException as e:
                raise FabricApiError(f"Error checking {operation_display} status: {str(e)}")
        
        raise FabricApiError(f"{operation_display} timed out after {self._format_duration(max_wait_time)}")
    
    def get_capacities(self) -> List[Dict[str, Any]]:
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
            
            if response.status_code == 200:
                capacities = response.json().get('value', [])
                self._log(f"Found {len(capacities)} capacity(ies)")
                return capacities
            else:
                error_msg = f"Failed to get capacities: HTTP {response.status_code}"
                self._log(error_msg, level="error")
                raise FabricApiError(error_msg)
                
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error getting capacities: {e}"
            self._log(error_msg, level="error")
            raise FabricApiError(error_msg)

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
        capacities = self.get_capacities()
        capacity = next((c for c in capacities if c['displayName'].lower() == capacity_name.lower()), None)
        
        if not capacity:
            self._log(f"Capacity '{capacity_name}' not found")
            return None
        
        return capacity

    def get_workspaces(self) -> List[Dict[str, Any]]:
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
                self._log(error_msg, level="error")
                raise FabricApiError(error_msg)
                
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error getting workspaces: {e}"
            self._log(error_msg, level="error")
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
        workspaces = self.get_workspaces()
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
            workspace_id: ID of the workspace
            capacity_id: ID of the capacity
            
        Raises:
            FabricApiError: If assignment fails
        """
        self._log(f"Assigning workspace {workspace_id} to capacity {capacity_id}")
        
        data = {"capacityId": capacity_id}
        response = self._make_request(
            f"workspaces/{workspace_id}/assignToCapacity", 
            method="POST", 
            data=data
        )
        
        if response.status_code in [200, 202]:
            self._log(f"Successfully assigned workspace to capacity")
        else:
            raise FabricApiError(f"Failed to assign workspace to capacity: {response.status_code}")
    
    def delete_workspace(self, workspace_id: str) -> Optional[str]:
        """
        Delete a workspace.
        
        Args:
            workspace_id: ID of the workspace to delete
            
        Returns:
            Workspace ID if successfully deleted, None if workspace not found
            
        Raises:
            FabricApiError: If deletion fails due to unexpected error
        """
        try:
            self._log(f"Deleting workspace {workspace_id}")
            
            response = self._make_request(f"workspaces/{workspace_id}", method="DELETE")
            
            if response.status_code == 200:
                self._log(f"Successfully deleted workspace")
                return workspace_id
            elif response.status_code == 404:
                self._log(f"Workspace {workspace_id} not found, nothing to delete")
                return None
            else:
                error_msg = f"Failed to delete workspace: {response.status_code}"
                self._log(error_msg, level="error")
                raise FabricApiError(error_msg)
                
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error deleting workspace: {e}"
            self._log(error_msg, level="error")
            raise FabricApiError(error_msg)
    
    def add_workspace_role_assignment(self, 
                                    workspace_id: str, 
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
            workspace_id: Workspace ID
            principal_id: The principal's ID (user object ID, service principal ID, or group ID)
            principal_type: Type of principal ("User", "ServicePrincipal", "Group", "ServicePrincipalProfile", "EntireTenant")
            role: Workspace role ("Admin", "Member", "Contributor", "Viewer")
            display_name: Optional display name of the principal
            user_principal_name: Optional user principal name (required for User type)
            aad_app_id: Optional Azure AD App ID (required for ServicePrincipal type)
            group_type: Optional group type ("SecurityGroup", "DistributionList", "Unknown") for Group type
            
        Returns:
            WorkspaceRoleAssignment object
            
        Raises:
            FabricApiError: If role assignment fails
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
        
        self._log(f"Adding {principal_type} role assignment '{role}' for principal {principal_id} to workspace {workspace_id}")
        
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
            f"workspaces/{workspace_id}/roleAssignments", 
            method="POST", 
            data=data
        )
        
        if response.status_code == 201:
            role_assignment = response.json()
            self._log(f"Successfully added {role} role assignment for {principal_type} {principal_id}")
            return role_assignment
        else:
            raise FabricApiError(f"Failed to add workspace role assignment: {response.status_code}")
    
    def get_workspace_role_assignments(self, 
                                     workspace_id: str,
                                     continuation_token: Optional[str] = None,
                                     get_all: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get workspace role assignments with support for pagination.
        
        Args:
            workspace_id: Workspace ID
            continuation_token: Optional token for retrieving the next page of results
            get_all: If True, retrieves all role assignments across all pages. 
                    If False, returns the raw API response with pagination info.
            
        Returns:
            If get_all=True: List of WorkspaceRoleAssignment objects
            If get_all=False: Raw API response with pagination info
            
        Raises:
            FabricApiError: If request fails
        """
        self._log(f"Getting workspace role assignments for workspace {workspace_id}")
        
        # Build query parameters
        params = []
        if continuation_token:
            params.append(f"continuationToken={continuation_token}")
        
        query_string = f"?{'&'.join(params)}" if params else ""
        uri = f"workspaces/{workspace_id}/roleAssignments{query_string}"
        
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
                    next_uri = f"workspaces/{workspace_id}/roleAssignments{next_query}"
                    
                    next_response = self._make_request(next_uri)
                    if next_response.status_code == 200:
                        next_data = next_response.json()
                        all_role_assignments.extend(next_data.get('value', []))
                        response_data = next_data
                    else:
                        raise FabricApiError(f"Failed to fetch next page of role assignments: {next_response.status_code}")
                
                self._log(f"Retrieved {len(all_role_assignments)} total role assignment(s)")
                return all_role_assignments
            else:
                # Return raw response with pagination info
                role_assignments = response_data.get('value', [])
                self._log(f"Retrieved {len(role_assignments)} role assignment(s) in current page")
                return response_data
        else:
            raise FabricApiError(f"Failed to get workspace role assignments: {response.status_code}")
    
    def get_workspace_role_assignment_by_principal(self, 
                                                  workspace_id: str, 
                                                  principal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific workspace role assignment by principal ID.
        
        Args:
            workspace_id: Workspace ID
            principal_id: Principal ID to search for
            
        Returns:
            WorkspaceRoleAssignment object if found, None otherwise
            
        Raises:
            FabricApiError: If request fails
        """
        self._log(f"Searching for role assignment for principal {principal_id} in workspace {workspace_id}")
        
        role_assignments = self.get_workspace_role_assignments(workspace_id, get_all=True)
        
        # Search for the specific principal
        for assignment in role_assignments:
            if assignment.get('principal', {}).get('id') == principal_id:
                self._log(f"Found role assignment: {assignment.get('role')} for principal {principal_id}")
                return assignment
        
        self._log(f"No role assignment found for principal {principal_id}")
        return None

    def create_eventhub_connection(self, name: str, namespace_name: str, event_hub_name: str, shared_access_policy_name: str, shared_access_key: str) -> Optional[Dict[str, Any]]:
        """
        Create an Event Hub connection in Microsoft Fabric.
        
        Args:
            name: Display name for the connection
            namespace_name: Event Hub namespace name
            event_hub_name: Event Hub name
            shared_access_policy_name: Shared access key policy name
            shared_access_key: Shared access key
            
        Returns:
            Dictionary with connection information if successful, None otherwise
            
        Raises:
            FabricApiError: If connection creation fails
        """
        self._log(f"Creating Event Hub connection: {name}")
        
        normalized_endpoint = self._normalize_eventhub_endpoint(namespace_name)

        connection_payload = {
            "displayName": name,
            "connectivityType": "ShareableCloud",
            "allowConnectionUsageInGateway": "false",
            "connectionDetails": {
                "type": "EventHub",
                "creationMethod": "EventHub.Contents",
                "parameters": [
                    {
                        "name": "endpoint",
                        "dataType": "Text",
                        "value": normalized_endpoint,
                    },
                    {
                        "name": "entityPath",
                        "dataType": "Text",
                        "value": event_hub_name,
                    }
                ]
            },
            "credentialDetails": {
                "singleSignOnType": "None",
                "credentials": {
                    "credentialType": "Basic", # the endpoint only accepts Basic auth, but takes SAS key with policy name as password and username
                    "username": shared_access_policy_name, #"RootManageSharedAccessKey",
                    "password": shared_access_key,
                }
            }
        }

        response = self._make_request(f"connections", method="POST", data=connection_payload)
        
        if response.status_code == 201:
            connection = response.json()
            self._log(f"Successfully created Event Hub connection: {name}")
            return connection
        else:
            raise FabricApiError(f"Failed to create Event Hub connection: {response.status_code}")

    def update_eventhub_connection(self, connection_id: str, name: str, namespace_name: str, event_hub_name: str, shared_access_policy_name: str, shared_access_key: str) -> Optional[Dict[str, Any]]:
        """
        Update an existing Event Hub connection in Microsoft Fabric.
        
        Args:
            connection_id: ID of the existing connection to update
            name: Display name for the connection
            namespace_name: Event Hub namespace name
            event_hub_name: Event Hub name
            shared_access_policy_name: Shared access key policy name
            shared_access_key: Shared access key
            
        Returns:
            Dictionary with updated connection information if successful, None otherwise
            
        Raises:
            FabricApiError: If connection update fails
        """
        try:
            self._log(f"Updating Event Hub connection: {name} (ID: {connection_id})")
            
            normalized_endpoint = self._normalize_eventhub_endpoint(namespace_name)

            connection_payload = {
                "displayName": name,
                "connectivityType": "ShareableCloud",
                "allowConnectionUsageInGateway": False,
                "connectionDetails": {
                    "type": "EventHub",
                    "creationMethod": "EventHub.Contents",
                    "parameters": [
                        {
                            "name": "endpoint",
                            "dataType": "Text",
                            "value": normalized_endpoint,
                        },
                        {
                            "name": "entityPath",
                            "dataType": "Text",
                            "value": event_hub_name,
                        }
                    ]
                },
                "credentialDetails": {
                    "singleSignOnType": "None",
                    "credentials": {
                        "credentialType": "Basic", # the endpoint only accepts Basic auth, but takes SAS key with policy name as password and username
                        "username": shared_access_policy_name,
                        "password": shared_access_key,
                    }
                }
            }

            response = self._make_request(f"connections/{connection_id}", method="PATCH", data=connection_payload)
            
            if response.status_code == 200:
                connection = response.json()
                self._log(f"Successfully updated Event Hub connection: {name}")
                return connection
            else:
                raise FabricApiError(f"Failed to update Event Hub connection: {response.status_code}")
                
        except FabricApiError:
            raise
        except Exception as e:
            raise FabricApiError(f"Error updating connection: {e}")
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """
        List all connections in the workspace.
        
        Returns:
            List of connections in the workspace
            
        Raises:
            FabricApiError: If request fails
        """
        self._log("Getting all connections")
        response = self._make_request(f"connections")
        
        if response.status_code == 200:
            connections = response.json().get("value", [])
            self._log(f"Found {len(connections)} connection(s)")
            return connections
        else:
            raise FabricApiError(f"Failed to list connections: {response.status_code}")
    
    def get_connection(self, connection_id: str) -> Dict[str, Any]:
        """
        Get details of a specific connection.
        
        Args:
            connection_id: ID of the connection to retrieve
            
        Returns:
            Connection details
            
        Raises:
            FabricApiError: If request fails
        """
        self._log(f"Getting connection details for {connection_id}")
        response = self._make_request(f"connections/{connection_id}")

        if response.status_code == 200:
            connection = response.json()
            self._log(f"Successfully retrieved connection: {connection.get('displayName', 'N/A')}")
            return connection
        else:
            raise FabricApiError(f"Failed to get connection: {response.status_code}")
    
    def delete_connection(self, connection_id: str) -> Optional[str]:
        """
        Delete a connection from the workspace.
        
        Args:
            connection_id: ID of the connection to delete
            
        Returns:
            Connection ID if successfully deleted, None if connection not found
            
        Raises:
            FabricApiError: If deletion fails due to unexpected error
        """
        try:
            self._log(f"Deleting connection {connection_id}")
            response = self._make_request(f"connections/{connection_id}", method="DELETE")
            
            if response.status_code in [200, 204]:
                self._log(f"Successfully deleted connection {connection_id}")
                return connection_id
            elif response.status_code == 404:
                self._log(f"Connection {connection_id} not found, nothing to delete")
                return None
            else:
                error_msg = f"Failed to delete connection: {response.status_code}"
                self._log(error_msg, level="error")
                raise FabricApiError(error_msg)
                
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error deleting connection: {e}"
            self._log(error_msg, level="error")
            raise FabricApiError(error_msg)

    def list_supported_connection_types(self) -> List[Dict[str, Any]]:
        """
        List all supported connection types in the workspace.
        
        Returns:
            List of supported connection types
            
        Raises:
            FabricApiError: If request fails
        """
        try:
            response = self._make_request(f"connections/supportedConnectionTypes")
            
            if response.status_code == 200:
                connection_types = response.json().get("value", [])
                self._log(f"Found {len(connection_types)} supported connection types")
                return connection_types
            else:
                error_msg = f"Failed to list supported connection types: HTTP {response.status_code}"
                self._log(error_msg, level="error")
                raise FabricApiError(error_msg)
                
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error listing supported connection types: {e}"
            self._log(error_msg, level="error")
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
        Initialize the FabricWorkspaceApiClient.
        
        Args:
            workspace_id: ID of the target workspace
            api_url: Base URL for Fabric API
            resource_url: Resource URL for authentication scope
            credential: Azure credential object (defaults to AzureCliCredential)
            timeout_sec: Default timeout for API requests
        """
        super().__init__(
            api_url=api_url,
            resource_url=resource_url,
            credential=credential,
            timeout_sec=timeout_sec
        )
        self.workspace_id = workspace_id
        self._log(f"FabricWorkspaceApiClient initialized for workspace: {workspace_id}")
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """
        Get information about this workspace.
        
        Returns:
            Dictionary containing workspace information
            
        Raises:
            FabricApiError: If request fails
        """
        self._log(f"Getting workspace information for {self.workspace_id}")
        response = self._make_request(f"workspaces/{self.workspace_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise FabricApiError(f"Failed to get workspace info: {response.status_code}")
    
    def get_items(self, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get items from a workspace.
        
        Args:
            workspace_id: Target workspace ID
            item_type: Optional filter by item type
            
        Returns:
            List of items
        """
        response = self._make_request(f"workspaces/{self.workspace_id}/items")
        items = response.json().get('value', [])
        
        if item_type:
            items = [item for item in items if item.get('type', '').lower() == item_type.lower()]
        
        return items
    
    def assign_to_capacity(self, capacity_id: str) -> None:
        """
        Assign this workspace to a capacity.
        
        Args:
            capacity_id: ID of the capacity to assign the workspace to
            
        Raises:
            FabricApiError: If assignment fails
        """
        self._log(f"Assigning workspace {self.workspace_id} to capacity {capacity_id}")
        
        data = {"capacityId": capacity_id}
        response = self._make_request(
            f"workspaces/{self.workspace_id}/assignToCapacity", 
            method="POST", 
            data=data
        )
        
        if response.status_code in [200, 202]:
            self._log(f"Successfully assigned workspace to capacity")
        else:
            raise FabricApiError(f"Failed to assign workspace to capacity: {response.status_code}")
    
    def delete(self) -> Optional[str]:
        """
        Delete this workspace.
        
        Returns:
            Workspace ID if successfully deleted, None if workspace not found
            
        Raises:
            FabricApiError: If deletion fails due to unexpected error
        """
        return super().delete_workspace(self.workspace_id)
    
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
            raise FabricApiError(f"Failed to add workspace role assignment: {response.status_code}")
    
    def get_role_assignments(self, 
                            continuation_token: Optional[str] = None,
                            get_all: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get workspace role assignments with support for pagination.
        
        Args:
            continuation_token: Optional token for retrieving the next page of results
            get_all: If True, retrieves all role assignments across all pages. 
                    If False, returns the raw API response with pagination info.
            
        Returns:
            If get_all=True: List of WorkspaceRoleAssignment objects
            If get_all=False: Raw API response containing:
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
                        raise FabricApiError(f"Failed to fetch next page of role assignments: {next_response.status_code}")
                
                self._log(f"Retrieved {len(all_role_assignments)} total role assignment(s)")
                return all_role_assignments
            else:
                # Return raw response with pagination info
                role_assignments = response_data.get('value', [])
                self._log(f"Retrieved {len(role_assignments)} role assignment(s) in current page")
                return response_data
        else:
            raise FabricApiError(f"Failed to get workspace role assignments: {response.status_code}")
    
    def get_role_assignment_by_principal(self, 
                                        principal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific workspace role assignment by principal ID.
        
        Args:
            principal_id: Principal ID to search for
            
        Returns:
            WorkspaceRoleAssignment object if found, None otherwise
            
        Raises:
            FabricApiError: If request fails
        """
        self._log(f"Searching for role assignment for principal {principal_id} in workspace {self.workspace_id}")
        
        role_assignments = self.get_role_assignments(get_all=True)
        
        # Search for the specific principal
        for assignment in role_assignments:
            if assignment.get('principal', {}).get('id') == principal_id:
                self._log(f"Found role assignment: {assignment.get('role')} for principal {principal_id}")
                return assignment
        
        self._log(f"No role assignment found for principal {principal_id}")
        return None

    # Folder operations
    def get_folders(self) -> List[Dict[str, Any]]:
        """
        Get all folders in the workspace.
        
        Returns:
            List of folder objects containing:
            - id: Folder ID (GUID)
            - displayName: Folder display name
            - parentFolderId: Parent folder ID (None for root folders)
            - workspaceId: Workspace ID
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
        """
        try:
            self._log(f"Getting folders from workspace {self.workspace_id}")
            response = self._make_request(f"workspaces/{self.workspace_id}/folders")
            
            if response.status_code == 200:
                folders = response.json().get('value', [])
                self._log(f"Found {len(folders)} folder(s)")
                return folders
            else:
                error_msg = f"Failed to get folders: HTTP {response.status_code}"
                self._log(error_msg, level="error")
                raise FabricApiError(error_msg)
                
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error getting folders: {e}"
            self._log(error_msg, level="error")
            raise FabricApiError(error_msg)
    
    def create_folder(self, display_name: str, parent_folder_id: Optional[str] = None) -> str:
        """
        Create a folder in the workspace.
        
        Args:
            display_name: Folder display name
            parent_folder_id: Optional parent folder ID (None for root folder)
            
        Returns:
            Created folder ID
            
        Raises:
            FabricApiError: If creation fails
            
        Required Scopes:
            Workspace.ReadWrite.All
        """
        try:
            self._log(f"Creating folder '{display_name}' in workspace {self.workspace_id}")
            
            data = {"displayName": display_name}
            if parent_folder_id:
                data["parentFolderId"] = parent_folder_id
                self._log(f"Creating folder under parent folder {parent_folder_id}")
            else:
                self._log("Creating folder in workspace root")
            
            response = self._make_request(
                f"workspaces/{self.workspace_id}/folders", 
                method="POST", 
                data=data
            )
            
            if response.status_code in [200, 201]:
                folder_id = response.json()['id']
                self._log(f"Successfully created folder '{display_name}' with ID: {folder_id}")
                return folder_id
            else:
                error_msg = f"Failed to create folder: HTTP {response.status_code}"
                self._log(error_msg, level="error")
                raise FabricApiError(error_msg)
                
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error creating folder: {e}"
            self._log(error_msg, level="error")
            raise FabricApiError(error_msg)
    
    def get_folder_by_name(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a folder by name in the workspace.
        
        Args:
            folder_name: Name of the folder to find
            parent_folder_id: Optional parent folder ID to search within (None for root folders)
            
        Returns:
            Folder object if found, None otherwise
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
        """
        try:
            self._log(f"Searching for folder '{folder_name}' in workspace {self.workspace_id}")
            folders = self.get_folders()
            
            # Filter folders by parent_folder_id and name
            for folder in folders:
                folder_parent_id = folder.get('parentFolderId')
                if (folder['displayName'].lower() == folder_name.lower() and 
                    folder_parent_id == parent_folder_id):
                    self._log(f"Found folder '{folder_name}' with ID: {folder['id']}")
                    return folder
            
            self._log(f"Folder '{folder_name}' not found")
            return None
            
        except FabricApiError:
            raise
        except Exception as e:
            error_msg = f"Error searching for folder '{folder_name}': {e}"
            self._log(error_msg, level="error")
            raise FabricApiError(error_msg)

    def create_eventhouse(self, 
                         display_name: str,
                         description: Optional[str] = None,
                         folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an Eventhouse in the workspace.
        
        Args:
            display_name: The eventhouse display name. The eventhouse name can contain alphanumeric 
                         characters, underscores, periods, and hyphens. Special characters aren't supported.
            description: Optional eventhouse description. Maximum length is 256 characters.
            folder_id: Optional folder ID. If not specified, the eventhouse is created in workspace root.
            
        Returns:
            Eventhouse object containing:
            - id: Eventhouse ID (GUID)
            - displayName: Eventhouse display name
            - description: Eventhouse description (if provided)
            - type: Item type ("Eventhouse")
            - workspaceId: Workspace ID (GUID)
            - folderId: Folder ID (if created in folder)
            - properties: EventhouseProperties object with service URIs and settings
            
        Raises:
            FabricApiError: If creation fails
            
        Required Scopes:
            Eventhouse.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Contributor workspace role or higher
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/eventhouse/items/create-eventhouse
        """
        # Validate required parameters
        if not display_name or not display_name.strip():
            raise FabricApiError("display_name is required and cannot be empty")
        
        # Validate description length
        if description and len(description) > 256:
            raise FabricApiError("description cannot exceed 256 characters")
        
        self._log(f"Creating Eventhouse '{display_name}' in workspace {self.workspace_id}")
        
        # Build request payload
        data = {
            "displayName": display_name.strip()
        }
        
        # Add optional parameters
        if description:
            data["description"] = description
        
        if folder_id:
            data["folderId"] = folder_id
        
        # Make the API request
        response = self._make_request(f"workspaces/{self.workspace_id}/eventhouses", method="POST", data=data)
        
        if response.status_code in [201, 202]:
            eventhouse = response.json()
            eventhouse_id = eventhouse.get('id', 'N/A')
            self._log(f"Successfully created Eventhouse '{display_name}' with ID: {eventhouse_id}")
            return eventhouse
        else:
            raise FabricApiError(f"Failed to create Eventhouse: {response.status_code}")
    
    def list_eventhouses(self, 
                        continuation_token: Optional[str] = None,
                        get_all: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        List all Eventhouses in the workspace with support for pagination.
        
        Args:
            continuation_token: Optional token for retrieving the next page of results
            get_all: If True, retrieves all eventhouses across all pages. 
                    If False, returns the raw API response with pagination info.
            
        Returns:
            If get_all=True: List of Eventhouse objects
            If get_all=False: Raw API response containing:
            - value: List of Eventhouse objects
            - continuationToken: Token for next page (if more results exist)
            - continuationUri: URI for next page (if more results exist)
            
            Each Eventhouse contains:
            - id: Eventhouse ID (GUID)
            - displayName: Eventhouse display name
            - description: Eventhouse description
            - type: Item type ("Eventhouse")
            - workspaceId: Workspace ID (GUID)
            - folderId: Optional folder ID if eventhouse is in a folder
            - properties: EventhouseProperties object with service URIs and settings
            - tags: List of applied tags (if any)
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
            
        Required Permissions:
            Viewer workspace role or higher
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/eventhouse/items/list-eventhouses
        """
        self._log(f"Getting Eventhouses for workspace {self.workspace_id}")
        
        # Build query parameters
        params = []
        if continuation_token:
            params.append(f"continuationToken={continuation_token}")
        
        query_string = f"?{'&'.join(params)}" if params else ""
        uri = f"workspaces/{self.workspace_id}/eventhouses{query_string}"
        
        # Make the API request
        response = self._make_request(uri)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if get_all:
                # Collect all eventhouses across all pages
                all_eventhouses = response_data.get('value', [])
                
                # Continue fetching pages if continuation token exists
                while 'continuationToken' in response_data:
                    next_token = response_data['continuationToken']
                    self._log(f"Fetching next page with token: {next_token[:20]}...")
                    
                    # Make request for next page
                    next_uri = f"workspaces/{self.workspace_id}/eventhouses?continuationToken={next_token}"
                    next_response = self._make_request(next_uri)
                    
                    if next_response.status_code == 200:
                        response_data = next_response.json()
                        all_eventhouses.extend(response_data.get('value', []))
                    else:
                        raise FabricApiError(f"Failed to get next page of Eventhouses: {next_response.status_code}")
                
                self._log(f"Retrieved {len(all_eventhouses)} total Eventhouse(s)")
                return all_eventhouses
            else:
                # Return raw response with pagination info
                eventhouses = response_data.get('value', [])
                self._log(f"Retrieved {len(eventhouses)} Eventhouse(s) in current page")
                return response_data
        else:
            raise FabricApiError(f"Failed to get Eventhouses: {response.status_code}")
    
    def get_eventhouse_by_name(self, eventhouse_name: str) -> Optional[Dict[str, Any]]:
        """
        Get an Eventhouse by name from the workspace.
        
        Args:
            eventhouse_name: Name of the Eventhouse to find
            
        Returns:
            Eventhouse object if found, None otherwise
            
        Raises:
            FabricApiError: If request fails
        """
        self._log(f"Searching for Eventhouse '{eventhouse_name}' in workspace {self.workspace_id}")
        
        eventhouses = self.list_eventhouses(get_all=True)
        
        # Search for the eventhouse by name (case-insensitive)
        for eventhouse in eventhouses:
            if eventhouse.get('displayName', '').lower() == eventhouse_name.lower():
                self._log(f"Found Eventhouse '{eventhouse_name}' with ID: {eventhouse.get('id')}")
                return eventhouse
        
        self._log(f"Eventhouse '{eventhouse_name}' not found")
        return None
    
    def delete_eventhouse(self, eventhouse_id: str) -> bool:
        """
        Delete an Eventhouse from the workspace.
        
        Args:
            eventhouse_id: ID of the Eventhouse to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            FabricApiError: If deletion fails
            
        Required Scopes:
            Eventhouse.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Write permissions for the eventhouse
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/eventhouse/items/delete-eventhouse
        """
        # Validate required parameters
        if not eventhouse_id or not eventhouse_id.strip():
            raise FabricApiError("eventhouse_id is required and cannot be empty")
        
        eventhouse_id = eventhouse_id.strip()
        self._log(f"Deleting Eventhouse {eventhouse_id} from workspace {self.workspace_id}")
        
        response = self._make_request(f"workspaces/{self.workspace_id}/eventhouses/{eventhouse_id}", method="DELETE")
        
        if response.status_code in [200, 204]:
            self._log(f"Successfully deleted Eventhouse")
            return True
        else:
            raise FabricApiError(f"Failed to delete Eventhouse: {response.status_code}")
            
    def get_eventhouse_by_id(self, eventhouse_id: str) -> Dict[str, Any]:
        """
        Get an Eventhouse by ID from the workspace.
        
        Args:
            eventhouse_id: ID of the Eventhouse
            
        Returns:
            Eventhouse object containing:
            - id: Eventhouse ID (GUID)
            - displayName: Eventhouse display name
            - description: Eventhouse description
            - type: Item type ("Eventhouse")
            - workspaceId: Workspace ID (GUID)
            - folderId: Optional folder ID if eventhouse is in a folder
            - properties: EventhouseProperties object with service URIs and settings
            - tags: List of applied tags (if any)
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Eventhouse.Read.All or Eventhouse.ReadWrite.All or Item.Read.All or Item.ReadWrite.All
            
        Required Permissions:
            Read permissions for the eventhouse
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/eventhouse/items/get-eventhouse
        """
        # Validate required parameters
        if not eventhouse_id or not eventhouse_id.strip():
            raise FabricApiError("eventhouse_id is required and cannot be empty")
        
        eventhouse_id = eventhouse_id.strip()
        self._log(f"Getting Eventhouse {eventhouse_id} from workspace {self.workspace_id}")
        
        response = self._make_request(f"workspaces/{self.workspace_id}/eventhouses/{eventhouse_id}")
        
        if response.status_code == 200:
            eventhouse = response.json()
            self._log(f"Successfully retrieved Eventhouse '{eventhouse.get('displayName', 'N/A')}'")
            return eventhouse
        else:
            raise FabricApiError(f"Failed to get Eventhouse: {response.status_code}")
    
    def list_kql_dashboards(self, 
                           continuation_token: Optional[str] = None,
                           get_all: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        List KQL dashboards in the workspace with support for pagination.
        
        Args:
            continuation_token: Optional token for retrieving the next page of results
            get_all: If True, retrieves all KQL dashboards across all pages. 
                    If False, returns the raw API response with pagination info.
            
        Returns:
            If get_all=True: List of KQL Dashboard objects
            If get_all=False: Raw API response containing:
            - value: List of KQL Dashboard objects
            - continuationToken: Token for next page (if more results exist)
            - continuationUri: URI for next page (if more results exist)
            
            Each KQL Dashboard contains:
            - id: Dashboard ID (GUID)
            - displayName: Dashboard display name
            - description: Dashboard description
            - type: Item type ("KQLDashboard")
            - workspaceId: Workspace ID (GUID)
            - folderId: Optional folder ID if dashboard is in a folder
            - tags: List of applied tags (if any)
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
            
        Required Permissions:
            Viewer workspace role or higher
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/kqldashboard/items/list-kql-dashboards
        """
        self._log(f"Getting KQL dashboards for workspace {self.workspace_id}")
        
        # Build query parameters
        params = []
        if continuation_token:
            params.append(f"continuationToken={continuation_token}")
        
        query_string = f"?{'&'.join(params)}" if params else ""
        uri = f"workspaces/{self.workspace_id}/kqlDashboards{query_string}"
        
        # Make the API request
        response = self._make_request(uri)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if get_all:
                # Collect all KQL dashboards across all pages
                all_dashboards = response_data.get('value', [])
                
                # Continue fetching pages if continuation token exists
                while 'continuationToken' in response_data:
                    next_token = response_data['continuationToken']
                    self._log(f"Fetching next page of KQL dashboards (token: {next_token[:20]}...)")
                    
                    next_params = [f"continuationToken={next_token}"]
                    next_query = f"?{'&'.join(next_params)}"
                    next_uri = f"workspaces/{self.workspace_id}/kqlDashboards{next_query}"
                    
                    next_response = self._make_request(next_uri)
                    if next_response.status_code == 200:
                        next_data = next_response.json()
                        all_dashboards.extend(next_data.get('value', []))
                        response_data = next_data
                    else:
                        raise FabricApiError(f"Failed to fetch next page of KQL dashboards: {next_response.status_code}")
                
                self._log(f"Retrieved {len(all_dashboards)} total KQL dashboard(s)")
                return all_dashboards
            else:
                # Return raw response with pagination info
                dashboards = response_data.get('value', [])
                self._log(f"Retrieved {len(dashboards)} KQL dashboard(s) in current page")
                return response_data
        else:
            raise FabricApiError(f"Failed to get KQL dashboards: {response.status_code}")
    
    def get_kql_dashboard_by_name(self, dashboard_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a KQL dashboard by name from the workspace.
        
        Args:
            dashboard_name: Name of the KQL dashboard to find
            
        Returns:
            KQL Dashboard object if found, None otherwise
            
        Raises:
            FabricApiError: If request fails
        """
        self._log(f"Searching for KQL dashboard '{dashboard_name}' in workspace {self.workspace_id}")
        
        dashboards = self.list_kql_dashboards(get_all=True)
        
        # Search for the dashboard by name (case-insensitive)
        for dashboard in dashboards:
            if dashboard.get('displayName', '').lower() == dashboard_name.lower():
                self._log(f"Found KQL dashboard: {dashboard.get('id')}")
                return dashboard
        
        self._log(f"KQL dashboard '{dashboard_name}' not found")
        return None
    
    def create_kql_dashboard(self,
                            display_name: str,
                            description: Optional[str] = None,
                            folder_id: Optional[str] = None,
                            dashboard_definition_base64: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a KQL dashboard in the workspace.
        
        Args:
            display_name: The KQL dashboard name (required)
            description: Optional dashboard description (max 256 characters)
            folder_id: Optional folder ID. If not specified, dashboard is created in workspace root
            dashboard_definition_base64: Optional Base64 encoded JSON string containing the dashboard configuration
            
        Returns:
            KQL Dashboard object containing:
            - id: Dashboard ID (GUID)
            - displayName: Dashboard display name
            - description: Dashboard description (if provided)
            - type: Item type ("KQLDashboard")
            - workspaceId: Workspace ID (GUID)
            - folderId: Folder ID (if created in folder)
            
        Raises:
            FabricApiError: If creation fails
            
        Required Scopes:
            KQLDashboard.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Contributor workspace role or higher
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/kqldashboard/items/create-kql-dashboard
            https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/kql-dashboard-definition
            
        Example:
            # Create simple dashboard
            dashboard = client.create_kql_dashboard("My Dashboard", "Dashboard description")
            
            # Create dashboard with Base64 encoded JSON configuration
            import json
            import base64
            
            dashboard_config = {
                "autoRefresh": {"enabled": False},
                "baseQueries": [],
                "tiles": [],
                "dataSources": [],
                "pages": [{"name": "Page 1", "id": "ab5f0628-9750-43e6-9ba4-20116e868755"}],
                "parameters": [],
                "queries": [],
                "schema_version": "52",
                "title": "My Dashboard"
            }
            
            # Encode to Base64
            json_str = json.dumps(dashboard_config, separators=(',', ':'))
            dashboard_base64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            
            dashboard = client.create_kql_dashboard(
                display_name="My Dashboard",
                dashboard_definition_base64=dashboard_base64
            )
        """
        self._log(f"Creating KQL dashboard '{display_name}' in workspace {self.workspace_id}")
        
        # Validate required parameters
        if not display_name or not display_name.strip():
            raise FabricApiError("display_name is required and cannot be empty")
        
        # Validate description length
        if description and len(description) > 256:
            raise FabricApiError("description cannot exceed 256 characters")
        
        # Build request payload
        data = {
            "displayName": display_name.strip()
        }
        
        # Add optional parameters
        if description:
            data["description"] = description
        
        if folder_id:
            data["folderId"] = folder_id
            
        if dashboard_definition_base64 is not None:
            # Validate dashboard_definition_base64 is a string
            if not isinstance(dashboard_definition_base64, str):
                raise FabricApiError("dashboard_definition_base64 must be a string")
            
            # Validate it's a valid Base64 string by attempting to decode it
            try:
                base64.b64decode(dashboard_definition_base64)
            except Exception as e:
                raise FabricApiError(f"dashboard_definition_base64 is not a valid Base64 encoded string: {str(e)}")
            
            # Build definition with the Base64 encoded JSON content
            definition = {
                "format": None,
                "parts": [
                    {
                        "path": "RealTimeDashboard.json",
                        "payload": dashboard_definition_base64,
                        "payloadType": "InlineBase64"
                    }
                ]
            }
            
            data["definition"] = definition
        
        # Make the API request
        response = self._make_request(
            f"workspaces/{self.workspace_id}/kqlDashboards", 
            method="POST", 
            data=data
        )
        
        if response.status_code in [201, 202]:
            dashboard = response.json()
            dashboard_id = dashboard.get('id', 'N/A')
            self._log(f"Successfully created KQL dashboard '{display_name}' with ID: {dashboard_id}")
            return dashboard
        else:
            raise FabricApiError(f"Failed to create KQL dashboard: {response.status_code}")
    
    def delete_kql_dashboard(self, dashboard_id: str) -> bool:
        """
        Delete a KQL dashboard from the workspace.
        
        Args:
            dashboard_id: ID of the KQL dashboard to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            FabricApiError: If deletion fails
            
        Required Scopes:
            KQLDashboard.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Contributor workspace role or higher
        """
        self._log(f"Deleting KQL dashboard {dashboard_id} from workspace {self.workspace_id}")
        
        response = self._make_request(
            f"workspaces/{self.workspace_id}/kqlDashboards/{dashboard_id}", 
            method="DELETE"
        )
        
        if response.status_code in [200, 204]:
            self._log(f"Successfully deleted KQL dashboard")
            return True
        else:
            raise FabricApiError(f"Failed to delete KQL dashboard: {response.status_code}")
    
    def update_kql_dashboard_content(self,
                                    dashboard_id: str,
                                    dashboard_definition_base64: str) -> bool:
        """
        Update an existing KQL dashboard content in the workspace.
        
        Args:
            dashboard_id: ID of the KQL dashboard to update
            dashboard_definition_base64: Base64 encoded JSON string containing the dashboard configuration
            
        Returns:
            True if update was successful
            
        Raises:
            FabricApiError: If update fails
            
        Required Scopes:
            KQLDashboard.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Read and write permissions for the KQL dashboard
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/kqldashboard/items/update-kql-dashboard-definition
            
        Example:
            import json
            import base64
            
            # Load and encode dashboard configuration
            with open("dashboard.json", "r") as f:
                dashboard_config = json.load(f)
            
            json_str = json.dumps(dashboard_config, separators=(',', ':'))
            dashboard_base64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            
            # Update dashboard content
            success = client.update_kql_dashboard_content(
                dashboard_id="12345678-1234-1234-1234-123456789012",
                dashboard_definition_base64=dashboard_base64
            )
        """
        self._log(f"Updating KQL dashboard {dashboard_id} in workspace {self.workspace_id}")
        
        # Validate dashboard_definition_base64 is a string
        if not isinstance(dashboard_definition_base64, str):
            raise FabricApiError("dashboard_definition_base64 must be a string")
        
        # Validate it's a valid Base64 string by attempting to decode it
        try:
            base64.b64decode(dashboard_definition_base64)
        except Exception as e:
            raise FabricApiError(f"dashboard_definition_base64 is not a valid Base64 encoded string: {str(e)}")
        
        # Build definition with the Base64 encoded JSON content
        definition = {
            "format": None,
            "parts": [
                {
                    "path": "RealTimeDashboard.json",
                    "payload": dashboard_definition_base64,
                    "payloadType": "InlineBase64"
                }
            ]
        }
        
        # Build request payload
        data = {"definition": definition}
        
        # Set updateMetadata to false
        uri = f"workspaces/{self.workspace_id}/kqlDashboards/{dashboard_id}/updateDefinition?updateMetadata=false"
        
        # Make the API request
        response = self._make_request(uri, method="POST", data=data)
        
        if response.status_code in [200, 202]:
            self._log(f"Successfully updated KQL dashboard {dashboard_id}")
            return True
        else:
            raise FabricApiError(f"Failed to update KQL dashboard: {response.status_code}")
    
    def list_eventstreams(self, 
                         continuation_token: Optional[str] = None,
                         get_all: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        List all eventstreams in the workspace with support for pagination.
        
        Args:
            continuation_token: Optional token for retrieving the next page of results
            get_all: If True, retrieves all eventstreams across all pages. 
                    If False, returns the raw API response with pagination info.
            
        Returns:
            If get_all=True: List of Eventstream objects
            If get_all=False: Raw API response containing:
            - value: List of Eventstream objects
            - continuationToken: Token for next page (if more results exist)
            - continuationUri: URI for next page (if more results exist)
            
            Each Eventstream contains:
            - id: Eventstream ID (GUID)
            - displayName: Eventstream display name
            - description: Eventstream description
            - type: Item type ("Eventstream")
            - workspaceId: Workspace ID (GUID)
            - folderId: Optional folder ID if eventstream is in a folder
            - tags: List of applied tags (if any)
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
            
        Required Permissions:
            Viewer workspace role or higher
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/eventstream/items/list-eventstreams
            
        Example:
            # Get all eventstreams
            eventstreams = client.list_eventstreams()
            
            # Get with pagination
            response = client.list_eventstreams(get_all=False)
            eventstreams = response['value']
            next_token = response.get('continuationToken')
        """
        self._log(f"Getting Eventstreams for workspace {self.workspace_id}")
        
        # Build query parameters
        params = []
        if continuation_token:
            params.append(f"continuationToken={continuation_token}")
        
        query_string = f"?{'&'.join(params)}" if params else ""
        uri = f"workspaces/{self.workspace_id}/eventstreams{query_string}"
        
        # Make the API request
        response = self._make_request(uri)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if get_all:
                all_eventstreams = response_data.get('value', [])
                current_token = response_data.get('continuationToken')
                
                # Continue fetching pages if continuation token exists
                while current_token:
                    next_uri = f"workspaces/{self.workspace_id}/eventstreams?continuationToken={current_token}"
                    next_response = self._make_request(next_uri)
                    
                    if next_response.status_code == 200:
                        next_data = next_response.json()
                        next_eventstreams = next_data.get('value', [])
                        all_eventstreams.extend(next_eventstreams)
                        current_token = next_data.get('continuationToken')
                    else:
                        raise FabricApiError(f"Failed to get additional eventstreams page: {next_response.status_code}")
                
                self._log(f"Retrieved {len(all_eventstreams)} eventstream(s)")
                return all_eventstreams
            else:
                eventstreams = response_data.get('value', [])
                self._log(f"Retrieved {len(eventstreams)} eventstream(s) (single page)")
                return response_data
        else:
            raise FabricApiError(f"Failed to get eventstreams: {response.status_code}")
    
    def get_eventstream_by_name(self, eventstream_name: str) -> Optional[Dict[str, Any]]:
        """
        Get an Eventstream by name from the workspace.
        
        Args:
            eventstream_name: Name of the Eventstream to find
            
        Returns:
            Eventstream object if found, None otherwise
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
            
        Required Permissions:
            Viewer workspace role or higher
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/eventstream/items/list-eventstreams
        """
        self._log(f"Searching for Eventstream '{eventstream_name}' in workspace {self.workspace_id}")
        
        eventstreams = self.list_eventstreams(get_all=True)
        
        # Search for the eventstream by name (case-insensitive)
        for eventstream in eventstreams:
            if eventstream.get('displayName', '').lower() == eventstream_name.lower():
                eventstream_id = eventstream.get('id', 'N/A')
                self._log(f"Found Eventstream '{eventstream_name}' with ID: {eventstream_id}")
                return eventstream
        
        self._log(f"Eventstream '{eventstream_name}' not found")
        return None
    
    def get_eventstream_by_id(self, eventstream_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific eventstream by ID.
        
        Args:
            eventstream_id: ID of the eventstream to retrieve
            
        Returns:
            Eventstream object if found, None if not found
            
        Raises:
            FabricApiError: If request fails (except for 404 Not Found)
            
        Required Scopes:
            Eventstream.Read.All or Eventstream.ReadWrite.All or Item.Read.All or Item.ReadWrite.All
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/eventstream/items/get-eventstream
        """
        if not eventstream_id or not eventstream_id.strip():
            raise ValueError("eventstream_id is required and cannot be empty")
        
        eventstream_id = eventstream_id.strip()
        self._log(f"Getting eventstream by ID: {eventstream_id}")
        
        try:
            response = self._make_request(
                f"workspaces/{self.workspace_id}/eventstreams/{eventstream_id}",
                wait_for_lro=False  # GET requests don't need LRO waiting
            )
            
            if response.status_code == 200:
                eventstream = response.json()
                self._log(f"Found eventstream '{eventstream.get('displayName', 'Unknown')}' (ID: {eventstream_id})")
                return eventstream
            elif response.status_code == 404:
                self._log(f"Eventstream with ID '{eventstream_id}' not found")
                return None
            else:
                raise FabricApiError(
                    f"Failed to get eventstream {eventstream_id}: {response.status_code} - {response.text}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )
                
        except FabricApiError:
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error getting eventstream {eventstream_id}: {str(e)}")
    
    def create_eventstream(self,
                          display_name: str,
                          description: Optional[str] = None,
                          folder_id: Optional[str] = None,
                          eventstream_definition_base64: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new eventstream in the workspace.
        
        Args:
            display_name: Name for the eventstream (spaces will be removed)
            description: Optional description for the eventstream
            folder_id: Optional folder ID to create the eventstream in
            eventstream_definition_base64: Base64 encoded JSON string containing the eventstream configuration
            
        Returns:
            Dictionary with eventstream information
            
        Raises:
            FabricApiError: If creation fails
            
        Required Scopes:
            Eventstream.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Contributor workspace role
            
        Reference:
            https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/api-create-with-definition#interface
            
        Example:
            import json
            import base64
            
            # Create without definition
            eventstream = client.create_eventstream(
                display_name="MyEventstream",
                description="My eventstream description"
            )
            
            # Create with definition
            with open("eventstream.json", "r") as f:
                eventstream_config = json.load(f)
            
            json_str = json.dumps(eventstream_config, separators=(',', ':'))
            eventstream_base64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            
            eventstream = client.create_eventstream(
                display_name="MyEventstream",
                description="My eventstream description",
                eventstream_definition_base64=eventstream_base64
            )
        """
        try:
            # Validate required parameters
            if not display_name or not display_name.strip():
                raise FabricApiError("display_name is required and cannot be empty")
            
            # Validate description length if provided
            if description and len(description) > 256:
                raise FabricApiError("description cannot exceed 256 characters")
            
            # Remove whitespaces from display name and validate
            display_name = display_name.strip().replace(" ", "_")
            
            self._log(f"Creating eventstream '{display_name}' in workspace {self.workspace_id}")
            
            # Build request payload
            data = {
                'displayName': display_name,
                'type': 'Eventstream'
            }
            
            if description:
                data['description'] = description.strip()
            
            if folder_id:
                data['folderId'] = folder_id
            
            # Add definition if provided
            if eventstream_definition_base64:
                # Validate eventstream_definition_base64 is a string
                if not isinstance(eventstream_definition_base64, str):
                    raise FabricApiError("eventstream_definition_base64 must be a string")
                
                # Validate it's a valid Base64 string by attempting to decode it
                try:
                    base64.b64decode(eventstream_definition_base64)
                except Exception as e:
                    raise FabricApiError(f"eventstream_definition_base64 is not a valid Base64 encoded string: {str(e)}")
                
                # Build definition with the Base64 encoded JSON content
                definition = {
                    "parts": [
                        {
                            "path": "eventstream.json",
                            "payload": eventstream_definition_base64,
                            "payloadType": "InlineBase64"
                        }
                    ]
                }
                data['definition'] = definition
            
            # Make the API request
            response = self._make_request(
                f"workspaces/{self.workspace_id}/items", 
                method="POST", 
                data=data
            )
            
            # Check response status
            if response.status_code != 200:
                raise FabricApiError(f"Failed to create eventstream: HTTP {response.status_code}")
            
            # HTTP 200 responses don't provide ID, so find the eventstream by name
            self._log(f"Eventstream creation returned HTTP 200, searching for '{display_name}' by name")
            try:
                found_eventstream = self.get_eventstream_by_name(display_name)
                if found_eventstream:
                    eventstream_id = found_eventstream.get('id', 'N/A')
                    self._log(f"Found created eventstream '{display_name}' with ID {eventstream_id}")
                    return found_eventstream
                else:
                    raise FabricApiError(f"Eventstream '{display_name}' was created but could not be found by name")
            except Exception as e:
                raise FabricApiError(f"Eventstream creation succeeded but could not retrieve details: {str(e)}")
            
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error creating eventstream '{display_name}': {str(e)}")
    
    def delete_eventstream(self, eventstream_id: str) -> bool:
        """
        Delete an eventstream from the workspace.
        
        Args:
            eventstream_id: ID of the eventstream to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            FabricApiError: If deletion fails
            
        Required Scopes:
            Eventstream.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Read and write permissions for the eventstream
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/eventstream/items/delete-eventstream
            
        Example:
            success = client.delete_eventstream("12345678-1234-1234-1234-123456789012")
        """
        try:
            # Validate required parameters
            if not eventstream_id or not eventstream_id.strip():
                raise FabricApiError("eventstream_id is required and cannot be empty")
            
            eventstream_id = eventstream_id.strip()
            self._log(f"Deleting eventstream {eventstream_id} from workspace {self.workspace_id}")
            
            # Make the API request
            response = self._make_request(
                f"workspaces/{self.workspace_id}/eventstreams/{eventstream_id}", 
                method="DELETE"
            )
            
            if response.status_code in [200, 204]:
                self._log(f"Successfully deleted eventstream {eventstream_id}")
                return True
            else:
                raise FabricApiError(f"Failed to delete eventstream: HTTP {response.status_code}")
                
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error deleting eventstream '{eventstream_id}': {str(e)}")
    
    def update_eventstream_content(self,
                                  eventstream_id: str,
                                  eventstream_definition_base64: str,
                                  update_metadata: bool = False) -> bool:
        """
        Update an existing eventstream content in the workspace.
        
        Args:
            eventstream_id: ID of the eventstream to update
            eventstream_definition_base64: Base64 encoded JSON string containing the eventstream configuration
            update_metadata: Whether to update the item's metadata if provided in the .platform file
            
        Returns:
            True if update was successful
            
        Raises:
            FabricApiError: If update fails
            
        Required Scopes:
            Eventstream.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Read and write permissions for the eventstream
            
        Reference:
            https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/api-update-eventstream-definition
            
        Example:
            import json
            import base64
            
            # Load and encode eventstream configuration
            with open("eventstream.json", "r") as f:
                eventstream_config = json.load(f)
            
            json_str = json.dumps(eventstream_config, separators=(',', ':'))
            eventstream_base64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            
            # Update eventstream content
            success = client.update_eventstream_content(
                eventstream_id="12345678-1234-1234-1234-123456789012",
                eventstream_definition_base64=eventstream_base64
            )
        """
        try:
            # Validate required parameters
            if not eventstream_id or not eventstream_id.strip():
                raise FabricApiError("eventstream_id is required and cannot be empty")
            
            if not eventstream_definition_base64:
                raise FabricApiError("eventstream_definition_base64 is required and cannot be empty")
            
            eventstream_id = eventstream_id.strip()
            
            self._log(f"Updating eventstream {eventstream_id} in workspace {self.workspace_id}")
            
            # Validate eventstream_definition_base64 is a string
            if not isinstance(eventstream_definition_base64, str):
                raise FabricApiError("eventstream_definition_base64 must be a string")
            
            # Validate it's a valid Base64 string by attempting to decode it
            try:
                base64.b64decode(eventstream_definition_base64)
            except Exception as e:
                raise FabricApiError(f"eventstream_definition_base64 is not a valid Base64 encoded string: {str(e)}")
            
            # Build definition with the Base64 encoded JSON content
            definition = {
                "parts": [
                    {
                        "path": "eventstream.json",
                        "payload": eventstream_definition_base64,
                        "payloadType": "InlineBase64"
                    }
                ]
            }
            
            # Build request payload
            data = {"definition": definition}
            
            # Build URI with updateMetadata parameter
            uri = f"workspaces/{self.workspace_id}/eventstreams/{eventstream_id}/updateDefinition?updateMetadata={str(update_metadata).lower()}"
            
            # Make the API request
            response = self._make_request(uri, method="POST", data=data)
            
            if response.status_code in [200, 202]:
                self._log(f"Successfully updated eventstream {eventstream_id}")
                return True
            else:
                raise FabricApiError(f"Failed to update eventstream: HTTP {response.status_code}")
                
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error updating eventstream '{eventstream_id}': {str(e)}")
    
    def create_kql_database(self,
                           display_name: str,
                           parent_eventhouse_item_id: str,
                           description: Optional[str] = None,
                           folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new KQL database in the workspace.
        
        Args:
            display_name: The KQL database display name
            parent_eventhouse_item_id: Parent eventhouse item ID
            description: Optional database description (max 256 characters)
            folder_id: Optional folder ID. If not specified, creates in workspace root
            
        Returns:
            KQL database object containing:
            - id: Database ID (GUID)
            - displayName: Database display name
            - description: Database description
            - type: Item type ("KQLDatabase")
            - workspaceId: Workspace ID
            - properties: Database properties including parent eventhouse ID and URIs
            
        Raises:
            FabricApiError: If creation fails
            
        Required Scopes:
            KQLDatabase.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Contributor workspace role
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/kqldatabase/items/create-kql-database
        """
        try:
            # Validate required parameters
            if not display_name or not display_name.strip():
                raise FabricApiError("display_name is required and cannot be empty")
            if not parent_eventhouse_item_id or not parent_eventhouse_item_id.strip():
                raise FabricApiError("parent_eventhouse_item_id is required and cannot be empty")
            
            # Build request payload
            data = {
                "displayName": display_name.strip(),
                "creationPayload": {
                    "databaseType": "ReadWrite",
                    "parentEventhouseItemId": parent_eventhouse_item_id.strip()
                }
            }
            
            # Add optional parameters
            if description:
                data["description"] = description.strip()
            if folder_id:
                data["folderId"] = folder_id.strip()
            
            # Log the operation
            self._log(f"Creating KQL database '{display_name}' in eventhouse '{parent_eventhouse_item_id}'")
            
            # Make the API request
            uri = f"workspaces/{self.workspace_id}/kqlDatabases"
            response = self._make_request(uri, method="POST", data=data, wait_for_lro=True)
            
            if response.status_code in [200, 201]:
                result = response.json()
                self._log(f"Successfully created KQL database '{display_name}' with ID: {result.get('id')}")
                return result
            else:
                raise FabricApiError(f"Failed to create KQL database: HTTP {response.status_code}")
                
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error creating KQL database '{display_name}': {str(e)}")
    
    def list_kql_databases(self, 
                          continuation_token: Optional[str] = None,
                          get_all: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        List KQL databases in the workspace.
        
        Args:
            continuation_token: Token for retrieving next page of results
            get_all: If True, returns all databases as a list. If False, returns paginated response
            
        Returns:
            If get_all=True: List of KQL database objects
            If get_all=False: Dict with 'value' (list of databases) and pagination info
            
        Raises:
            FabricApiError: If listing fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
            
        Required Permissions:
            Viewer workspace role
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/kqldatabase/items/list-kql-databases
        """
        try:
            self._log("Listing KQL databases in workspace")
            
            if get_all:
                # Get all databases across multiple pages
                all_databases = []
                current_token = continuation_token
                
                while True:
                    # Build URI with continuation token if provided
                    uri = f"workspaces/{self.workspace_id}/kqlDatabases"
                    if current_token:
                        uri += f"?continuationToken={current_token}"
                    
                    # Make the API request
                    response = self._make_request(uri, method="GET")
                    
                    if response.status_code == 200:
                        result = response.json()
                        databases = result.get('value', [])
                        all_databases.extend(databases)
                        
                        # Check if there are more pages
                        current_token = result.get('continuationToken')
                        if not current_token:
                            break
                    else:
                        raise FabricApiError(f"Failed to list KQL databases: HTTP {response.status_code}")
                
                self._log(f"Found {len(all_databases)} KQL database(s)")
                return all_databases
            else:
                # Get single page response
                uri = f"workspaces/{self.workspace_id}/kqlDatabases"
                if continuation_token:
                    uri += f"?continuationToken={continuation_token}"
                
                response = self._make_request(uri, method="GET")
                
                if response.status_code == 200:
                    result = response.json()
                    databases = result.get('value', [])
                    self._log(f"Found {len(databases)} KQL database(s) in current page")
                    return result
                else:
                    raise FabricApiError(f"Failed to list KQL databases: HTTP {response.status_code}")
                    
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error listing KQL databases: {str(e)}")
    
    def get_kql_database_by_name(self, database_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a KQL database by name from the workspace.
        
        Args:
            database_name: Name of the KQL database to find
            
        Returns:
            KQL database object if found, None otherwise
            
        Raises:
            FabricApiError: If listing fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
            
        Required Permissions:
            Viewer workspace role
        """
        try:
            if not database_name or not database_name.strip():
                raise FabricApiError("database_name is required and cannot be empty")
            
            # Get all databases and search for the one with matching name
            databases = self.list_kql_databases(get_all=True)
            database = next((d for d in databases if d['displayName'].lower() == database_name.lower()), None)
            
            if database:
                self._log(f"Found KQL database '{database_name}' with ID: {database.get('id')}")
            else:
                self._log(f"KQL database '{database_name}' not found")
            
            return database
            
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error finding KQL database '{database_name}': {str(e)}")
    
    def update_kql_database(self,
                           database_id: str,
                           display_name: Optional[str] = None,
                           description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update properties of an existing KQL database.
        
        Args:
            database_id: ID of the KQL database to update
            display_name: New display name for the database
            description: New description for the database (max 256 characters)
            
        Returns:
            Updated KQL database object
            
        Raises:
            FabricApiError: If update fails
            
        Required Scopes:
            KQLDatabase.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Read and write permissions for the KQL database
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/kqldatabase/items/update-kql-database
        """
        try:
            # Validate required parameters
            if not database_id or not database_id.strip():
                raise FabricApiError("database_id is required and cannot be empty")
            
            if not display_name and not description:
                raise FabricApiError("At least one of display_name or description must be provided")
            
            # Build request payload
            data = {}
            if display_name:
                data["displayName"] = display_name.strip()
            if description:
                data["description"] = description.strip()
            
            # Log the operation
            self._log(f"Updating KQL database '{database_id}'")
            
            # Make the API request
            uri = f"workspaces/{self.workspace_id}/kqlDatabases/{database_id}"
            response = self._make_request(uri, method="PATCH", data=data)
            
            if response.status_code == 200:
                result = response.json()
                self._log(f"Successfully updated KQL database '{database_id}'")
                return result
            else:
                raise FabricApiError(f"Failed to update KQL database: HTTP {response.status_code}")
                
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error updating KQL database '{database_id}': {str(e)}")
    
    def delete_kql_database(self, database_id: str) -> bool:
        """
        Delete a KQL database from the workspace.
        
        Args:
            database_id: ID of the KQL database to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            FabricApiError: If deletion fails
            
        Required Scopes:
            KQLDatabase.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Write permissions for the KQL database
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/kqldatabase/items/delete-kql-database
        """
        try:
            # Validate required parameters
            if not database_id or not database_id.strip():
                raise FabricApiError("database_id is required and cannot be empty")
            
            # Log the operation
            self._log(f"Deleting KQL database '{database_id}'")
            
            # Make the API request
            uri = f"workspaces/{self.workspace_id}/kqlDatabases/{database_id}"
            response = self._make_request(uri, method="DELETE")
            
            if response.status_code == 200:
                self._log(f"Successfully deleted KQL database '{database_id}'")
                return True
            else:
                raise FabricApiError(f"Failed to delete KQL database: HTTP {response.status_code}")
                
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error deleting KQL database '{database_id}': {str(e)}")

    def create_activator(self,
                        display_name: str,
                        description: Optional[str] = None,
                        folder_id: Optional[str] = None,
                        definition_base64: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an Activator (Reflex) in the workspace.
        
        Args:
            display_name: Display name for the activator (required)
            description: Description for the activator (optional)
            folder_id: ID of the folder to create the activator in (optional)
            definition_base64: Base64 encoded definition JSON (optional)
            
        Returns:
            Dictionary with activator information if successful
            
        Raises:
            FabricApiError: If creation fails
        """
        try:
            self._log(f"Creating activator '{display_name}'")
            
            # Prepare the request payload
            payload = {
                "displayName": display_name,
                "type": "Reflex"
            }
            
            if description:
                payload["description"] = description
                
            if folder_id:
                payload["folderId"] = folder_id
                
            if definition_base64:
                payload["definition"] = {
                    "parts": [
                        {
                            "path": "ReflexEntities.json",
                            "payload": definition_base64,
                            "payloadType": "InlineBase64"
                        }
                    ]
                }
            
            response = self._make_request(f"workspaces/{self.workspace_id}/items", method="POST", data=payload)
            activator_info = response.json()
            
            self._log(f"✅ Successfully created activator '{display_name}' with ID: {activator_info.get('id')}")
            return activator_info
            
        except FabricApiError as e:
            self._log(f"❌ Failed to create activator '{display_name}': {e}", level="ERROR")
            raise
        except Exception as e:
            self._log(f"❌ Unexpected error creating activator: {e}", level="ERROR")
            raise FabricApiError(f"Error creating activator: {e}")
    
    def list_activators(self, 
                       continuation_token: Optional[str] = None,
                       get_all: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        List all activators (reflexes) in the workspace with support for pagination.
        
        Args:
            continuation_token: Optional token for retrieving the next page of results
            get_all: If True, retrieves all activators across all pages. 
                    If False, returns the raw API response with pagination info.
            
        Returns:
            If get_all=True: List of Activator objects
            If get_all=False: Raw API response containing:
            - value: List of Activator objects
            - continuationToken: Token for next page (if more results exist)
            - continuationUri: URI for next page (if more results exist)
            
            Each Activator contains:
            - id: Activator ID (GUID)
            - displayName: Activator display name
            - description: Activator description
            - type: Item type ("Reflex")
            - workspaceId: Workspace ID (GUID)
            - folderId: Optional folder ID if activator is in a folder
            - tags: List of applied tags (if any)
            
        Raises:
            FabricApiError: If request fails
            
        Required Scopes:
            Workspace.Read.All or Workspace.ReadWrite.All
            
        Required Permissions:
            Viewer workspace role or higher
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/reflex/items/list-reflexes
        """
        self._log(f"Getting Activators for workspace {self.workspace_id}")
        
        # Build query parameters
        params = []
        if continuation_token:
            params.append(f"continuationToken={continuation_token}")
        
        query_string = f"?{'&'.join(params)}" if params else ""
        uri = f"workspaces/{self.workspace_id}/reflexes{query_string}"
        
        # Make the API request
        response = self._make_request(uri)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if get_all:
                all_activators = response_data.get('value', [])
                current_token = response_data.get('continuationToken')
                
                # Continue fetching pages if continuation token exists
                while current_token:
                    next_uri = f"workspaces/{self.workspace_id}/reflexes?continuationToken={current_token}"
                    next_response = self._make_request(next_uri)
                    
                    if next_response.status_code == 200:
                        next_data = next_response.json()
                        next_activators = next_data.get('value', [])
                        all_activators.extend(next_activators)
                        current_token = next_data.get('continuationToken')
                    else:
                        raise FabricApiError(f"Failed to get additional activators page: {next_response.status_code}")
                
                self._log(f"Retrieved {len(all_activators)} activator(s)")
                return all_activators
            else:
                activators = response_data.get('value', [])
                self._log(f"Retrieved {len(activators)} activator(s) (single page)")
                return response_data
        else:
            raise FabricApiError(f"Failed to get activators: {response.status_code}")
    
    def get_activator_by_name(self, activator_name: str) -> Optional[Dict[str, Any]]:
        """
        Get an activator (reflex) by name.
        
        Args:
            activator_name: Name of the activator to find
            
        Returns:
            Activator dictionary if found, None otherwise
            
        Raises:
            FabricApiError: If search fails
        """
        try:
            self._log(f"Searching for activator named '{activator_name}'")
            
            activators = self.list_activators(get_all=True)
            
            for activator in activators:
                if activator.get('displayName') == activator_name:
                    self._log(f"✅ Found activator '{activator_name}' with ID: {activator.get('id')}")
                    return activator
            
            self._log(f"❌ Activator '{activator_name}' not found")
            return None
            
        except FabricApiError as e:
            self._log(f"❌ Failed to search for activator '{activator_name}': {e}", level="ERROR")
            raise
        except Exception as e:
            self._log(f"❌ Unexpected error searching for activator: {e}", level="ERROR")
            raise FabricApiError(f"Error searching for activator: {e}")
    
    def get_activator_by_id(self, activator_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific activator (reflex) by ID.
        
        Args:
            activator_id: ID of the activator to retrieve
            
        Returns:
            Activator object if found, None if not found
            
        Raises:
            FabricApiError: If request fails (except for 404 Not Found)
            
        Required Scopes:
            Reflex.Read.All or Reflex.ReadWrite.All or Item.Read.All or Item.ReadWrite.All
            
        Reference:
            https://learn.microsoft.com/en-us/rest/api/fabric/reflex/items/get-reflex
        """
        if not activator_id or not activator_id.strip():
            raise ValueError("activator_id is required and cannot be empty")
        
        activator_id = activator_id.strip()
        self._log(f"Getting activator by ID: {activator_id}")
        
        try:
            response = self._make_request(
                f"workspaces/{self.workspace_id}/reflexes/{activator_id}",
                wait_for_lro=False  # GET requests don't need LRO waiting
            )
            
            if response.status_code == 200:
                activator = response.json()
                self._log(f"Found activator '{activator.get('displayName', 'Unknown')}' (ID: {activator_id})")
                return activator
            elif response.status_code == 404:
                self._log(f"Activator with ID '{activator_id}' not found")
                return None
            else:
                raise FabricApiError(
                    f"Failed to get activator {activator_id}: {response.status_code} - {response.text}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )
                
        except FabricApiError:
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error getting activator {activator_id}: {str(e)}")
    
    def delete_activator(self, activator_id: str) -> bool:
        """
        Delete an activator (reflex) by ID.
        
        Args:
            activator_id: ID of the activator to delete
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            FabricApiError: If deletion fails
        """
        try:
            self._log(f"Deleting activator with ID '{activator_id}'")
            self._make_request(f"workspaces/{self.workspace_id}/reflexes/{activator_id}", method="DELETE")
            self._log(f"✅ Successfully deleted activator")
            return True
            
        except FabricApiError as e:
            if e.status_code == 404:
                self._log(f"Activator with ID '{activator_id}' not found")
                return False
            else:
                self._log(f"❌ Failed to delete activator: {e}", level="ERROR")
                raise
        except Exception as e:
            self._log(f"❌ Unexpected error deleting activator: {e}", level="ERROR")
            raise FabricApiError(f"Error deleting activator: {e}")
    
    def update_activator_definition(self,
                                   activator_id: str,
                                   definition_base64: str,
                                   update_metadata: bool = False) -> bool:
        """
        Update an activator (reflex) definition.
        
        Args:
            activator_id: ID of the activator to update
            definition_base64: Base64 encoded definition JSON
            update_metadata: Whether to update metadata from .platform file
            
        Returns:
            True if updated successfully
            
        Raises:
            FabricApiError: If update fails
        """
        try:
            self._log(f"Updating activator definition for ID '{activator_id}'")
            
            # Prepare the request payload
            payload = {
                "definition": {
                    "parts": [
                        {
                            "path": "ReflexEntities.json",
                            "payload": definition_base64,
                            "payloadType": "InlineBase64"
                        }
                    ]
                }
            }
            
            # Build the endpoint with optional updateMetadata parameter
            endpoint = f"workspaces/{self.workspace_id}/reflexes/{activator_id}/updateDefinition"
            if update_metadata:
                endpoint += "?updateMetadata=true"
            
            self._make_request(endpoint, method="POST", data=payload)
            self._log(f"✅ Successfully updated activator definition")
            return True
            
        except FabricApiError as e:
            self._log(f"❌ Failed to update activator definition: {e}", level="ERROR")
            raise
        except Exception as e:
            self._log(f"❌ Unexpected error updating activator definition: {e}", level="ERROR")
            raise FabricApiError(f"Error updating activator definition: {e}")
    
    def create_data_agent(self, data_agent_name: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Data Agent in the workspace. Reference: https://pypi.org/project/fabric-data-agent-sdk/
        
        Args:
            data_agent_name: The name of the Data Agent to be created.
            folder_id: Optional folder ID where to create the data agent
            
        Returns:
            Dictionary with data agent information including:
            - id: Data agent ID (GUID)
            - displayName: Data agent display name
            - type: Item type ("DataAgent")
            - workspaceId: Workspace ID (GUID)
            
        Raises:
            FabricApiError: If creation fails
            
        Required Scopes:
            DataAgent.ReadWrite.All or Item.ReadWrite.All
            
        Required Permissions:
            Contributor workspace role or higher
        """
        try:
            # Validate required parameters
            if not data_agent_name or not data_agent_name.strip():
                raise FabricApiError("data_agent_name is required and cannot be empty")
            
            self._log(f"Creating Data Agent '{data_agent_name}' in workspace {self.workspace_id}")
            
            # Build request payload following the pattern from the original function
            data = {
                "artifactType": "LLMPlugin",
                "displayName": data_agent_name.strip()
            }
            
            # Add optional folder ID
            if folder_id:
                data["folderId"] = folder_id
                self._log(f"Creating Data Agent in folder {folder_id}")
            
            # Make the API request using the dataagents endpoint
            response = self._make_request(
                f"workspaces/{self.workspace_id}/dataagents", 
                method="POST", 
                data=data
            )
            
            # Check response status
            if response.status_code in [200, 201, 202]:
                data_agent = response.json()
                data_agent_id = data_agent.get('id')
                
                # If ID is not returned in response, get it by searching by name
                if not data_agent_id:
                    self._log(f"Data Agent ID not returned in response, searching by name")
                    found_agent = self.get_data_agent_by_name(data_agent_name.strip())
                    if found_agent and found_agent.get('id'):
                        data_agent = found_agent
                        data_agent_id = found_agent['id']
                    else:
                        raise FabricApiError(f"Data Agent '{data_agent_name}' was created but could not be found or retrieved")
                
                self._log(f"Successfully created Data Agent '{data_agent_name}' with ID: {data_agent_id}")
                return data_agent
            else:
                raise FabricApiError(f"Failed to create Data Agent: HTTP {response.status_code}")
                
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error creating Data Agent '{data_agent_name}': {str(e)}")
    
    def get_data_agents(self) -> List[Dict[str, Any]]:
        """
        Get all Data Agents in the workspace.
        
        Returns:
            List of data agent objects
            
        Raises:
            FabricApiError: If listing fails
            
        Required Scopes:
            DataAgent.Read.All or Item.Read.All
            
        Required Permissions:
            Viewer workspace role or higher
        """
        try:
            self._log(f"Getting Data Agents in workspace {self.workspace_id}")
            
            # Make the API request to list dataagents
            response = self._make_request(
                f"workspaces/{self.workspace_id}/dataagents", 
                method="GET"
            )
            
            # Check response status
            if response.status_code == 200:
                data_agents = response.json().get('value', [])
                self._log(f"Found {len(data_agents)} Data Agent(s)")
                return data_agents
            else:
                raise FabricApiError(f"Failed to list Data Agents: HTTP {response.status_code}")
                
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error listing Data Agents: {str(e)}")
    
    def get_data_agent_by_name(self, data_agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a Data Agent by name from the workspace.
        
        Args:
            data_agent_name: The name of the Data Agent to find.
            
        Returns:
            Dictionary with data agent information if found, None otherwise
            
        Raises:
            FabricApiError: If listing fails
            
        Required Scopes:
            DataAgent.Read.All or Item.Read.All
            
        Required Permissions:
            Viewer workspace role or higher
        """
        try:
            # Validate required parameters
            if not data_agent_name or not data_agent_name.strip():
                raise FabricApiError("data_agent_name is required and cannot be empty")
            
            self._log(f"Searching for Data Agent '{data_agent_name}' in workspace {self.workspace_id}")
            
            # Get all data agents
            data_agents = self.get_data_agents()
            
            # Find the data agent by name
            for agent in data_agents:
                if agent.get('displayName', '').strip() == data_agent_name.strip():
                    self._log(f"Found Data Agent '{data_agent_name}' with ID: {agent.get('id', 'N/A')}")
                    return agent
            
            self._log(f"Data Agent '{data_agent_name}' not found")
            return None
                
        except FabricApiError:
            # Re-raise FabricApiError as-is
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error searching for Data Agent '{data_agent_name}': {str(e)}")

    # Notebook operations
    def get_notebooks(self) -> Dict[str, str]:
        """
        Get all notebooks in the workspace.
        
        Returns:
            Dictionary mapping notebook names to IDs
            
        Raises:
            FabricApiError: If listing fails
        """
        try:
            self._log(f"Getting notebooks from workspace {self.workspace_id}")
            response = self._make_request(f"workspaces/{self.workspace_id}/notebooks")
            
            if response.status_code == 200:
                notebooks = response.json().get('value', [])
                notebook_dict = {notebook['displayName']: notebook['id'] for notebook in notebooks}
                self._log(f"Found {len(notebooks)} notebook(s)")
                return notebook_dict
            else:
                raise FabricApiError(f"Failed to list notebooks: HTTP {response.status_code}")
                
        except FabricApiError:
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error listing notebooks: {str(e)}")
    
    def create_notebook(self, notebook_name: str, notebook_data_base64: str, folder_id: Optional[str] = None, wait_for_lro: bool = True) -> Dict[str, Any]:
        """
        Create a new notebook in the workspace.
        
        Args:
            notebook_name: Display name for the notebook
            notebook_data_base64: Base64-encoded notebook JSON content
            folder_id: Optional ID of the folder to create the notebook in
            wait_for_lro: Whether to wait for long running operations to complete
            
        Returns:
            Dictionary with notebook information including ID
            
        Raises:
            FabricApiError: If creation fails or ID cannot be retrieved
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
            
            if response.status_code in [200, 201, 202]:
                # Try to get ID from response
                notebook_obj = None
                if response.content:
                    response_data = response.json()
                    if 'id' in response_data:
                        notebook_obj = response_data
                
                # If no ID in response, get notebook by name
                if not notebook_obj or 'id' not in notebook_obj:
                    notebook_obj = self.get_notebook_by_name(notebook_name)
                
                # Ensure we have a notebook object with ID
                if not notebook_obj or 'id' not in notebook_obj:
                    raise FabricApiError(f"Failed to retrieve notebook ID after creation for '{notebook_name}'")
                
                return notebook_obj
            else:
                raise FabricApiError(f"Failed to create notebook: HTTP {response.status_code}")
                
        except FabricApiError:
            raise
        except Exception as e:
            raise FabricApiError(f"Unexpected error creating notebook: {str(e)}")
    
    def update_notebook(self, notebook_id: str, notebook_name: str, notebook_data_base64: str, folder_id: Optional[str] = None, wait_for_lro: bool = True) -> requests.Response:
        """
        Update an existing notebook in the workspace.
        
        Args:
            notebook_id: Notebook ID to update
            notebook_name: Display name for the notebook
            notebook_data_base64: Base64-encoded notebook JSON content
            folder_id: Optional ID of the folder to place the notebook in
            wait_for_lro: Whether to wait for long running operations to complete
            
        Returns:
            API response
            
        Raises:
            FabricApiError: If update fails
        """
        try:
            self._log(f"Updating notebook '{notebook_name}' ({notebook_id}) in workspace {self.workspace_id}")
            
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
            
            return self._make_request(
                f"workspaces/{self.workspace_id}/notebooks/{notebook_id}/updateDefinition", 
                method="POST", 
                data=notebook_data,
                wait_for_lro=wait_for_lro
            )
                
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

    def schedule_notebook_job(self, notebook_id: str) -> Dict[str, Any]:
        """
        Schedule a single notebook job and monitor its completion.
        
        Args:
            notebook_id: Notebook ID to execute
            
        Returns:
            Dictionary with execution results including status, duration, and details
            
        Raises:
            FabricApiError: If execution fails
        """
        import time
        
        job_url = f"workspaces/{self.workspace_id}/items/{notebook_id}/jobs/RunNotebook/instances"
        start_time = time.time()
        
        try:
            self._log(f"Starting notebook execution: {notebook_id}")
            response = self._make_request(job_url, method="POST", wait_for_lro=False)
            
            # Handle immediate completion (HTTP 200)
            if response.status_code == 200:
                job_data = response.json() if response.content else {}
                self._log(f"Notebook {notebook_id} completed immediately (synchronous)")
                return {'status': 'Completed', 'duration': '0m 0s', 'details': job_data}
            
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
                        operation_name=f"notebook-{notebook_id}",
                        max_wait_time=1800,  # 30 minutes for notebook execution
                        check_interval=20   # 20 seconds between checks
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
            raise FabricApiError(f"Unexpected error executing notebook {notebook_id}: {str(e)}")

    # Environment operations
    def create_environment(self,
                          display_name: str,
                          description: Optional[str] = None,
                          folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new environment in the workspace.
        
        Args:
            display_name: Display name for the environment
            description: Optional description for the environment
            folder_id: Optional folder ID where to create the environment
            
        Returns:
            Dictionary containing the created environment details
        """
        self._log(f"Creating environment '{display_name}' in workspace {self.workspace_id}")
        
        # Build request body
        request_body = {
            "displayName": display_name
        }
        
        if description:
            request_body["description"] = description
            
        if folder_id:
            request_body["folderId"] = folder_id
        
        response = self._make_request(
            uri=f"workspaces/{self.workspace_id}/environments",
            method="POST",
            data=json.dumps(request_body),
            wait_for_lro=True
        )
        
        if response.status_code in [201, 202]:
            self._log(f"Successfully created environment '{display_name}'")
            return response.json()
        else:
            self._log(f"Failed to create environment '{display_name}': {response.status_code} - {response.text}", "ERROR")
            raise FabricApiError(f"Failed to create environment: {response.text}", response.status_code, response.json() if response.content else None)

    def list_environments(self, 
                         continuation_token: Optional[str] = None,
                         get_all: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        List environments in the workspace.
        
        Args:
            continuation_token: Optional continuation token for pagination
            get_all: If True, retrieves all environments by handling pagination automatically
            
        Returns:
            Dictionary with environment list and pagination info, or List of all environments if get_all=True
        """
        self._log(f"Listing environments in workspace {self.workspace_id}")
        
        if not get_all:
            # Single page request
            uri = f"workspaces/{self.workspace_id}/environments"
            if continuation_token:
                uri += f"?continuationToken={continuation_token}"
                
            response = self._make_request(uri=uri, method="GET", wait_for_lro=False)
            
            if response.status_code == 200:
                result = response.json()
                self._log(f"Successfully retrieved {len(result.get('value', []))} environments")
                return result
            else:
                self._log(f"Failed to list environments: {response.status_code} - {response.text}", "ERROR")
                raise FabricApiError(f"Failed to list environments: {response.text}", response.status_code, response.json() if response.content else None)
        else:
            # Get all environments with automatic pagination
            all_environments = []
            current_token = continuation_token
            
            while True:
                uri = f"workspaces/{self.workspace_id}/environments"
                if current_token:
                    uri += f"?continuationToken={current_token}"
                    
                response = self._make_request(uri=uri, method="GET", wait_for_lro=False)
                
                if response.status_code == 200:
                    result = response.json()
                    environments = result.get('value', [])
                    all_environments.extend(environments)
                    
                    # Check if there are more pages
                    current_token = result.get('continuationToken')
                    if not current_token:
                        break
                else:
                    self._log(f"Failed to list environments: {response.status_code} - {response.text}", "ERROR")
                    raise FabricApiError(f"Failed to list environments: {response.text}", response.status_code, response.json() if response.content else None)
            
            self._log(f"Successfully retrieved {len(all_environments)} environments")
            return all_environments

    def get_environment_by_name(self, environment_name: str) -> Optional[Dict[str, Any]]:
        """
        Get an environment by its display name.
        
        Args:
            environment_name: Display name of the environment to find
            
        Returns:
            Dictionary containing the environment details if found, None otherwise
        """
        self._log(f"Getting environment by name: '{environment_name}'")
        
        try:
            environments = self.list_environments(get_all=True)
            
            for env in environments:
                if env.get('displayName') == environment_name:
                    self._log(f"Found environment '{environment_name}' with ID: {env.get('id')}")
                    return env
                    
            self._log(f"Environment '{environment_name}' not found")
            return None
            
        except Exception as e:
            self._log(f"Error getting environment by name '{environment_name}': {str(e)}", "ERROR")
            return None

    def delete_environment(self, environment_id: str) -> bool:
        """
        Delete an environment from the workspace.
        
        Args:
            environment_id: ID of the environment to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        self._log(f"Deleting environment with ID: {environment_id}")
        
        try:
            response = self._make_request(
                uri=f"workspaces/{self.workspace_id}/environments/{environment_id}",
                method="DELETE",
                wait_for_lro=False
            )
            
            if response.status_code == 200:
                self._log(f"Successfully deleted environment {environment_id}")
                return True
            else:
                self._log(f"Failed to delete environment {environment_id}: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self._log(f"Error deleting environment {environment_id}: {str(e)}", "ERROR")
            return False

    def publish_environment(self, environment_id: str) -> Dict[str, Any]:
        """
        Trigger a publish operation for an environment.
        
        Args:
            environment_id: ID of the environment to publish
            
        Returns:
            Dictionary containing the publish operation details
        """
        self._log(f"Publishing environment with ID: {environment_id}")
        
        response = self._make_request(
            uri=f"workspaces/{self.workspace_id}/environments/{environment_id}/staging/publish?beta=false",
            method="POST",
            wait_for_lro=True
        )
        
        if response.status_code in [200, 202]:
            self._log(f"Successfully triggered publish for environment {environment_id}")
            return response.json()
        else:
            self._log(f"Failed to publish environment {environment_id}: {response.status_code} - {response.text}", "ERROR")
            raise FabricApiError(f"Failed to publish environment: {response.text}", response.status_code, response.json() if response.content else None)

    def update_environment_definition(self,
                                     environment_id: str,
                                     environment_yml_base64: Optional[str] = None,
                                     sparkcompute_yml_base64: Optional[str] = None,
                                     platform_base64: Optional[str] = None) -> bool:
        """
        Update the definition of an environment.
        
        Args:
            environment_id: ID of the environment to update
            environment_yml_base64: Optional base64 encoded environment.yml content
            sparkcompute_yml_base64: Optional base64 encoded Sparkcompute.yml content
            platform_base64: Optional base64 encoded .platform content
            
        Returns:
            True if update was successful, False otherwise
        
        Note:
            update_metadata is automatically set to True if platform_base64 is provided, False otherwise
        """
        self._log(f"Updating definition for environment {environment_id}")
        
        # Build definition parts
        definition_parts = []
        
        if environment_yml_base64:
            definition_parts.append({
                "path": "Libraries/PublicLibraries/environment.yml",
                "payload": environment_yml_base64,
                "payloadType": "InlineBase64"
            })
            
        if sparkcompute_yml_base64:
            definition_parts.append({
                "path": "Setting/Sparkcompute.yml",
                "payload": sparkcompute_yml_base64,
                "payloadType": "InlineBase64"
            })
            
        if platform_base64:
            definition_parts.append({
                "path": ".platform",
                "payload": platform_base64,
                "payloadType": "InlineBase64"
            })
        
        if not definition_parts:
            self._log("No definition parts provided for update", "ERROR")
            return False
            
        request_body = {
            "definition": {
                "parts": definition_parts
            }
        }
        
        # Auto-determine update_metadata based on platform_base64
        update_metadata = platform_base64 is not None
        
        uri = f"workspaces/{self.workspace_id}/environments/{environment_id}/updateDefinition"
        if update_metadata:
            uri += "?updateMetadata=true"
        
        response = self._make_request(
            uri=uri,
            method="POST",
            data=json.dumps(request_body),
            wait_for_lro=True
        )
        
        if response.status_code in [200, 202]:
            self._log(f"Successfully updated definition for environment {environment_id}")
            return True
        else:
            self._log(f"Failed to update environment definition {environment_id}: {response.status_code} - {response.text}", "ERROR")
            return False
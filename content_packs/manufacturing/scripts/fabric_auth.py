#!/usr/bin/env python3
"""
Fabric Authentication Module

This module provides authentication functionality for Microsoft Fabric API operations.

Usage:
    python fabric_auth.py

Requirements:
    - fabric_api.py module in the same directory
    - Azure CLI authentication or other Azure credentials configured
"""

from content_packs.manufacturing.scripts.fabric_api import FabricApiClient, FabricWorkspaceApiClient

def authenticate():
    """
    Authenticate and create Fabric API client.
    
    Returns:
        Authenticated FabricApiClient instance if successful, None if failed
    """
    try:
        result = FabricApiClient()
        print(f"✅ Successfully authenticated Fabric API client")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def authenticate_workspace(workspace_id: str):
    """
    Authenticate and create Fabric Workspace API client for a specific workspace.
    
    Args:
        workspace_id: ID of the workspace to create client for
        
    Returns:
        Authenticated FabricWorkspaceApiClient instance if successful, None if failed
    """
    try:
        result = FabricWorkspaceApiClient(workspace_id=workspace_id)
        print(f"✅ Successfully authenticated Fabric Workspace API client for workspace: {workspace_id}")
        return result
    except Exception as e:
        print(f"❌ Error creating workspace client: {e}")
        return None
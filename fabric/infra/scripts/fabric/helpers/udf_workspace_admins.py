#!/usr/bin/env python3
"""
UDF Workspace Administrators Setup Module

This module provides functionality to add administrators to a Fabric workspace
for the Unified Data Foundation solution.
"""

import sys
import os
import uuid
from typing import Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fabric_api import FabricApiError, FabricWorkspaceApiClient
from graph_api import GraphApiError


def is_valid_guid(value):
    """Check if a string is a valid GUID format."""
    if not value or not isinstance(value, str):
        return False
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def detect_principal_type(admin_identifier, graph_client=None):
    """
    Detect if an identifier is a user or service principal and resolve to object ID.
    
    Args:
        admin_identifier: User UPN, object ID (GUID), or application ID (GUID)
        graph_client: Optional Graph API client (will create one if not provided)
    
    Returns:
        Tuple of (principal_type, object_id, principal_data)
        - principal_type: "User" or "ServicePrincipal" 
        - object_id: The object ID of the principal
        - principal_data: Full principal object from Graph API
        
    Raises:
        ValueError: If identifier cannot be resolved
        GraphApiError: If Graph API calls fail
    """
    try:
        # Use Graph API to resolve the principal if available
        if graph_client:
            principal_type, object_id, principal_data = graph_client.resolve_principal(admin_identifier)
            return principal_type, object_id, principal_data
        
    except GraphApiError as e:
        # Convert Graph API errors to Unknown type for fallback handling
        print(f"  ⚠️ WARNING: Graph API lookup failed for '{admin_identifier}': {str(e)}")
        print(f"     Will try both ServicePrincipal and User types...")
        return "Unknown", admin_identifier, {"id": admin_identifier, "displayName": "Unknown"}
    except Exception as e:
        # Fallback to original logic if Graph API is not available
        print(f"  ⚠️ WARNING: Graph API lookup failed for '{admin_identifier}': {str(e)}")
        print(f"     Falling back to basic identifier pattern detection...")
        
        if is_valid_guid(admin_identifier):
            return "ServicePrincipal", admin_identifier, {"id": admin_identifier, "displayName": "Unknown"}
        elif "@" in admin_identifier and "." in admin_identifier:
            return "User", admin_identifier, {"userPrincipalName": admin_identifier, "displayName": "Unknown"}
        else:
            print(f"     Unable to determine principal type - will try both ServicePrincipal and User...")
            return "Unknown", admin_identifier, {"id": admin_identifier, "displayName": "Unknown"}


def get_existing_admin_principals(workspace_client: FabricWorkspaceApiClient) -> set:
    """Get set of existing admin principal IDs for duplicate checking."""
    try:
        print(f"    🔍 Checking existing role assignments...")
        assignments = workspace_client.list_role_assignments(get_all=True)
        
        existing_principals = set()
        admin_count = 0
        
        for assignment in assignments:
            if assignment.get('role') == 'Admin':
                admin_count += 1
                principal = assignment.get('principal', {})
                principal_id = principal.get('id', '').lower()
                if principal_id:
                    existing_principals.add(principal_id)
                
                # Also add UPN if available for easier matching
                user_details = principal.get('userDetails', {})
                upn = user_details.get('userPrincipalName', '').lower()
                if upn:
                    existing_principals.add(upn)
        
        print(f"    📊 Found {admin_count} existing administrator(s)")
        return existing_principals
        
    except Exception as e:
        print(f"    ⚠️ WARNING: Could not retrieve existing role assignments: {str(e)}")
        print("       Will proceed but may create duplicates")
        return set()


def add_workspace_admin(workspace_client, admin_identifier, existing_principals, graph_client):
    """Add a single workspace administrator with simplified error handling."""
    # Check if already exists
    if admin_identifier.lower() in existing_principals:
        print(f"    ⏭️ Skipping '{admin_identifier}' - already a workspace administrator")
        return {'status': 'skipped', 'message': 'Already exists'}
    
    try:
        # Try to resolve principal type using Graph API
        principal_type, object_id, principal_data = detect_principal_type(admin_identifier, graph_client)
        
        if object_id.lower() in existing_principals:
            print(f"    ⏭️ Skipping '{admin_identifier}' - already a workspace administrator")
            existing_principals.add(admin_identifier.lower())  # Prevent future duplicates
            return {'status': 'skipped', 'message': 'Already exists (by object ID)'}
        
        display_name = principal_data.get('displayName', 'Unknown')
        
        # Handle unknown principal type by trying both ServicePrincipal and User
        if principal_type == "Unknown":
            print(f"    🔐 Trying to add administrator (type unknown): {admin_identifier} ({display_name})")
            
            # Try ServicePrincipal first
            try:
                print(f"    🔄 Attempting as ServicePrincipal...")
                workspace_client.add_role_assignment(
                    principal_id=object_id,
                    principal_type="ServicePrincipal",
                    role="Admin",
                    display_name=display_name,
                    aad_app_id=principal_data.get('appId')
                )
                print(f"    ✅ Successfully added '{admin_identifier}' as ServicePrincipal administrator")
                existing_principals.add(object_id.lower())
                existing_principals.add(admin_identifier.lower())
                return {'status': 'success', 'message': 'Added successfully as ServicePrincipal'}
            except Exception as sp_error:
                print(f"    ❌ ServicePrincipal attempt failed: {str(sp_error)}")
                
                # Try User as fallback
                try:
                    print(f"    🔄 Attempting as User...")
                    workspace_client.add_role_assignment(
                        principal_id=object_id,
                        principal_type="User",
                        role="Admin",
                        display_name=display_name,
                        user_principal_name=principal_data.get('userPrincipalName', admin_identifier)
                    )
                    print(f"    ✅ Successfully added '{admin_identifier}' as User administrator")
                    existing_principals.add(object_id.lower())
                    existing_principals.add(admin_identifier.lower())
                    return {'status': 'success', 'message': 'Added successfully as User'}
                except Exception as user_error:
                    error_msg = f"Both ServicePrincipal and User attempts failed: SP=({str(sp_error)}), User=({str(user_error)})"
                    print(f"    ❌ {error_msg}")
                    return {'status': 'failed', 'message': error_msg}
        
        else:
            print(f"    🔐 Adding {principal_type.lower()} administrator: {admin_identifier} ({display_name})")
            
            # Add role assignment based on type
            if principal_type == "User":
                workspace_client.add_role_assignment(
                    principal_id=object_id,
                    principal_type=principal_type,
                    role="Admin",
                    display_name=display_name,
                    user_principal_name=principal_data.get('userPrincipalName', admin_identifier)
                )
            else:  # ServicePrincipal
                workspace_client.add_role_assignment(
                    principal_id=object_id,
                    principal_type=principal_type,
                    role="Admin",
                    display_name=display_name,
                    aad_app_id=principal_data.get('appId')
                )
            
            print(f"    ✅ Successfully added '{admin_identifier}' as workspace administrator")
            existing_principals.add(object_id.lower())
            existing_principals.add(admin_identifier.lower())
            return {'status': 'success', 'message': 'Added successfully'}
        
    except (ValueError, GraphApiError) as e:
        return {'status': 'failed', 'message': f'Principal type detection failed: {str(e)}'}
        
    except FabricApiError as e:
        error_hints = {
            400: "Verify the identifier is correct and the principal exists",
            403: "Ensure you have Admin permissions on this workspace", 
            404: "Check if the principal exists in your Azure AD tenant"
        }
        hint = error_hints.get(e.status_code, "Check API permissions and principal validity")
        return {'status': 'failed', 'message': f'API error ({e.status_code}): {hint}'}
        
    except Exception as e:
        return {'status': 'failed', 'message': f'Unexpected error: {str(e)}'}


def setup_workspace_administrators(workspace_client, fabric_admins: list = None, graph_client = None) -> dict:
    """
    Add administrators to a Fabric workspace.
    
    Args:
        workspace_client: Workspace-specific Fabric API client
        fabric_admins: List of administrators (UPNs or GUIDs)
        graph_client: Optional Graph API client (for UPN resolution)
        
    Returns:
        dict: Summary of admin assignments (added, skipped, failed, errors)
    """
    # Validate input
    if not fabric_admins:
        print("ℹ️ No administrators specified - skipping workspace administrator setup")
        return {'added': 0, 'skipped': 0, 'failed': 0, 'errors': []}
    
    # Clean up whitespace from list items
    admins_to_add = [admin.strip() for admin in fabric_admins if admin and admin.strip()]
    
    if not admins_to_add:
        print("ℹ️ No valid administrators found - skipping workspace administrator setup")
        return {'added': 0, 'skipped': 0, 'failed': 0, 'errors': []}
    
    print(f"📋 Parsed {len(admins_to_add)} administrator(s): {', '.join(admins_to_add)}")
    print(f"👥 Setting up workspace administrators...")
    
    # Get existing admin principals for this workspace
    existing_admin_principals = get_existing_admin_principals(workspace_client)
    
    workspace_stats = {'added': 0, 'skipped': 0, 'failed': 0, 'errors': []}
    
    # Process administrators (UPNs and object IDs with Graph API resolution)
    print(f"    👥 Adding administrators...")
    
    for admin_identifier in admins_to_add:
        result = add_workspace_admin(workspace_client, admin_identifier, existing_admin_principals, graph_client)
        
        if result['status'] == 'success':
            workspace_stats['added'] += 1
        elif result['status'] == 'skipped':
            workspace_stats['skipped'] += 1
        else:  # failed
            workspace_stats['failed'] += 1
            workspace_stats['errors'].append(f"{admin_identifier}: {result['message']}")
    
    # Print workspace summary
    total_requested = len(admins_to_add)
    print(f"    📊 Workspace administrators summary - Added: {workspace_stats['added']}, Skipped: {workspace_stats['skipped']}, Failed: {workspace_stats['failed']}, Total: {total_requested}")
    
    # Show error details if any failures occurred
    if workspace_stats['errors']:
        print(f"    ⚠️ Errors in workspace administrator setup:")
        for error in workspace_stats['errors'][:3]:  # Show first 3 errors
            print(f"       • {error}")
        if len(workspace_stats['errors']) > 3:
            print(f"       ... and {len(workspace_stats['errors']) - 3} more error(s)")
    
    if workspace_stats['added'] > 0 or workspace_stats['skipped'] > 0:
        return workspace_stats
    elif workspace_stats['failed'] > 0:
        print(f"❌ Failed to add workspace administrators")
        return None
    else:
        print(f"✅ No administrators to add")
        return workspace_stats


if __name__ == "__main__":
    """Command-line interface for testing."""
    import argparse
    from fabric_api import create_workspace_fabric_client
    from graph_api import create_graph_client
    
    parser = argparse.ArgumentParser(
        description="Add administrators to a Microsoft Fabric workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add admins by CSV string
  python udf_workspace_admins.py --workspace-id "12345678-1234-1234-1234-123456789012" --admins-csv "user1@contoso.com,user2@contoso.com,87654321-4321-4321-4321-210987654321"
        """
    )
    
    parser.add_argument(
        "--workspace-id",
        required=True,
        help="ID of the workspace"
    )
    
    parser.add_argument(
        "--admins-csv",
        required=True,
        help="Comma-separated list of administrators (UPNs or GUIDs)"
    )
    
    args = parser.parse_args()
    
    try:
        workspace_client = create_workspace_fabric_client(args.workspace_id)
        graph_client = create_graph_client()
        
        # Convert CSV string to list for function call
        admins_list = [admin.strip() for admin in args.admins_csv.split(',') if admin.strip()]
        
        result = setup_workspace_administrators(
            workspace_client=workspace_client,
            fabric_admins=admins_list,
            graph_client=graph_client
        )
        
        if result:
            print(f"\n🎉 Final Results:")
            print(f"   Workspace ID: {args.workspace_id}")
            print(f"   Admins Added: {result.get('added', 0)}")
            print(f"   Admins Skipped: {result.get('skipped', 0)}")
            print(f"   Admins Failed: {result.get('failed', 0)}")
            sys.exit(0 if result.get('failed', 0) == 0 else 1)
        else:
            print(f"❌ Failed to setup workspace administrators")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

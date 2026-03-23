#!/usr/bin/env python3
"""
UDF Workspace Setup Module

This module provides workspace creation and capacity assignment functionality 
for the Unified Data Foundation solution.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fabric_api import FabricApiClient, FabricApiError


def setup_workspace(fabric_client: FabricApiClient, capacity_name: str, workspace_name: str) -> str:
    """
    Create or retrieve a Fabric workspace and assign it to a capacity.
    
    Args:
        fabric_client: Authenticated Fabric API client
        capacity_name: Name of the capacity to assign
        workspace_name: Name of the workspace to create
        
    Returns:
        str: Workspace ID
        
    Raises:
        FabricApiError: If workspace creation or capacity assignment fails
        SystemExit: If capacity is not found
    """
    print(f"🏢 Setting up workspace: {workspace_name}")
    
    try:
        # Get capacity ID
        print(f"   Looking up capacity: {capacity_name}")
        capacity = fabric_client.get_capacity(capacity_name)
        
        if not capacity:
            print(f"❌ Error: Capacity '{capacity_name}' not found")
            print(f"   Please ensure the capacity exists and you have access to it.")
            raise FabricApiError(f"Capacity '{capacity_name}' not found")
    except FabricApiError:
        raise
    except Exception as e:
        print(f"❌ Error looking up capacity: {e}")
        raise FabricApiError(f"Failed to lookup capacity: {e}")
    
    capacity_id = capacity['id']
    print(f"   ✅ Found capacity: {capacity_name} ({capacity_id})")
    
    try:
        # Check if workspace already exists
        print(f"   Checking if workspace '{workspace_name}' exists...")
        workspace = fabric_client.get_workspace(workspace_name)
    except FabricApiError as e:
        print(f"❌ Error checking workspace existence: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error checking workspace: {e}")
        raise FabricApiError(f"Failed to check workspace: {e}")
    
    if workspace:
        workspace_id = workspace['id']
        print(f"   ℹ️  Workspace already exists: {workspace_name} ({workspace_id})")
        
        # Check if workspace is already assigned to the target capacity
        current_capacity_id = workspace.get('capacityId')
        if current_capacity_id == capacity_id:
            print(f"   ✅ Workspace already assigned to capacity: {capacity_name}")
        else:
            # Workspace is on a different capacity or no capacity - reassign
            print(f"   🔄 Assigning workspace to capacity: {capacity_name}")
            try:
                fabric_client.assign_workspace_to_capacity(workspace_id, capacity_id)
                print(f"   ✅ Successfully assigned workspace to capacity")
            except FabricApiError as e:
                # On failure, re-fetch the workspace to verify actual capacity assignment
                try:
                    refreshed = fabric_client.get_workspace(workspace_name)
                except Exception as refresh_err:
                    print(f"❌ Error assigning workspace to capacity: {e}")
                    print(f"   Additionally, failed to verify workspace state: {refresh_err}")
                    raise e from refresh_err
                if refreshed and refreshed.get('capacityId') == capacity_id:
                    print(f"   ⚠️  Assignment call failed but workspace is already on the correct capacity. Continuing...")
                else:
                    print(f"❌ Error assigning workspace to capacity: {e}")
                    raise
    else:
        # Create new workspace
        print(f"   Creating new workspace: {workspace_name}")
        try:
            workspace_id = fabric_client.create_workspace(workspace_name)
            print(f"   ✅ Created workspace: {workspace_name} ({workspace_id})")
        except FabricApiError as e:
            print(f"❌ Error creating workspace: {e}")
            raise
        
        # Assign workspace to capacity
        print(f"   🔄 Assigning workspace to capacity: {capacity_name}")
        try:
            fabric_client.assign_workspace_to_capacity(workspace_id, capacity_id)
            print(f"   ✅ Successfully assigned workspace to capacity")
        except FabricApiError as e:
            print(f"❌ Error assigning new workspace to capacity: {e}")
            raise
    
    return workspace_id


def main():
    """Main function to create/setup a Fabric workspace."""
    import argparse
    from fabric_api import FabricApiClient, FabricApiError
    
    parser = argparse.ArgumentParser(
        description="Create or setup a Microsoft Fabric workspace and assign it to a capacity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create workspace and assign to capacity
  python udf_workspace.py --capacity-name "MyCapacity" --workspace-name "MyWorkspace"
        """
    )
    
    parser.add_argument(
        "--capacity-name",
        required=True,
        help="Name of the capacity to assign the workspace to"
    )
    
    parser.add_argument(
        "--workspace-name",
        required=True,
        help="Name of the workspace to create or retrieve"
    )
    
    args = parser.parse_args()
    
    try:
        fabric_client = FabricApiClient()
        
        workspace_id = setup_workspace(
            fabric_client=fabric_client,
            capacity_name=args.capacity_name,
            workspace_name=args.workspace_name
        )
        
        print(f"\n🎉 Final Results:")
        print(f"   Workspace Name: {args.workspace_name}")
        print(f"   Workspace ID: {workspace_id}")
        print(f"   Capacity: {args.capacity_name}")
        print(f"   Status: Ready for use!")
        
    except FabricApiError as e:
        print(f"❌ Fabric API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

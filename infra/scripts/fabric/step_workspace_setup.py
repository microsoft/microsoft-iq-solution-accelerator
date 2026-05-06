#!/usr/bin/env python3
"""
Microsoft IQ Workspace Setup Module

This module provides workspace creation and capacity assignment functionality 
for the Microsoft IQ solution.
"""

import logging
import sys
import os

from fabric.fabric_api import FabricApiClient, FabricApiError

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.  No handlers or levels are
# configured here; this follows the Python convention that library modules
# only acquire loggers and never configure them.
logger = logging.getLogger(__name__)


def _resume_capacity(
    fabric_client: FabricApiClient,
    capacity_name: str,
    subscription_id: str,
    resource_group: str,
) -> None:
    """
    Resume a paused Fabric capacity using the azure-mgmt-fabric SDK.
    
    Args:
        fabric_client: Authenticated Fabric API client (credential is reused)
        capacity_name: Name of the Fabric capacity
        subscription_id: Azure subscription ID containing the capacity
        resource_group: Resource group name containing the capacity
        
    Raises:
        FabricApiError: If the resume operation fails
    """
    from azure.mgmt.fabric import FabricMgmtClient
    from azure.core.exceptions import HttpResponseError
    
    credential = fabric_client._credential
    
    logger.info(f"   Resuming capacity '{capacity_name}' "
          f"(subscription={subscription_id}, rg={resource_group})...")
    try:
        mgmt_client = FabricMgmtClient(credential, subscription_id)
        poller = mgmt_client.fabric_capacities.begin_resume(
            resource_group_name=resource_group,
            capacity_name=capacity_name,
        )
        poller.result()  # blocks until the resume operation completes
        logger.info(f"   Capacity '{capacity_name}' is now Active")
    except HttpResponseError as e:
        raise FabricApiError(
            f"Failed to resume capacity '{capacity_name}': {e.message}",
            status_code=e.status_code,
        )


def setup_workspace(
    fabric_client: FabricApiClient,
    capacity_name: str,
    workspace_name: str,
    subscription_id: str = "",
    resource_group: str = "",
) -> str:
    """
    Create or retrieve a Fabric workspace and assign it to a capacity.
    
    Args:
        fabric_client: Authenticated Fabric API client
        capacity_name: Name of the capacity to assign
        workspace_name: Name of the workspace to create
        subscription_id: Azure subscription ID (required to resume a paused capacity)
        resource_group: Resource group name (required to resume a paused capacity)
        
    Returns:
        str: Workspace ID
        
    Raises:
        FabricApiError: If workspace creation or capacity assignment fails
        SystemExit: If capacity is not found
    """
    logger.info(f"🏢 Setting up workspace: {workspace_name}")
    
    try:
        # Get capacity ID
        logger.info(f"   Looking up capacity: {capacity_name}")
        capacity = fabric_client.get_capacity(capacity_name)
        
        if not capacity:
            logger.error(f"Capacity '{capacity_name}' not found")
            logger.error(f"   Please ensure the capacity exists and you have access to it.")
            raise FabricApiError(f"Capacity '{capacity_name}' not found")
    except FabricApiError:
        raise
    except Exception as e:
        logger.error(f"Error looking up capacity: {e}")
        raise FabricApiError(f"Failed to lookup capacity: {e}")
    
    capacity_id = capacity['id']
    logger.info(f"   Found capacity: {capacity_name} ({capacity_id})")
    
    # Check if capacity is paused and resume if needed
    # Note: Fabric REST API reports paused capacities as "Inactive", while
    # the ARM API uses "Paused". We check for both to be safe.
    capacity_state = capacity.get('state', 'Unknown')
    if capacity_state in ('Inactive', 'Paused'):
        if not subscription_id or not resource_group:
            raise FabricApiError(
                f"Capacity '{capacity_name}' is paused but subscription_id and "
                "resource_group are required to resume it. Set AZURE_SUBSCRIPTION_ID "
                "and AZURE_RESOURCE_GROUP environment variables."
            )
        logger.warning(f"Capacity '{capacity_name}' is paused. Attempting to resume...")
        _resume_capacity(fabric_client, capacity_name, subscription_id, resource_group)
    elif capacity_state != 'Active':
        logger.warning(f"Capacity state is '{capacity_state}' — proceeding, but operations may fail.")
    
    try:
        # Check if workspace already exists
        logger.info(f"   Checking if workspace '{workspace_name}' exists...")
        workspace = fabric_client.get_workspace(workspace_name)
    except FabricApiError as e:
        logger.error(f"Error checking workspace existence: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error checking workspace: {e}")
        raise FabricApiError(f"Failed to check workspace: {e}")
    
    if workspace:
        workspace_id = workspace['id']
        logger.info(f"   Workspace already exists: {workspace_name} ({workspace_id})")
        
        # Check if workspace is already assigned to the target capacity
        current_capacity_id = workspace.get('capacityId')
        if current_capacity_id == capacity_id:
            logger.info(f"   Workspace already assigned to capacity: {capacity_name}")
        else:
            # Workspace is on a different capacity or no capacity - reassign
            logger.info(f"   Assigning workspace to capacity: {capacity_name}")
            try:
                fabric_client.assign_workspace_to_capacity(workspace_id, capacity_id)
                logger.info(f"   Workspace assigned to capacity")
            except FabricApiError as e:
                # On failure, re-fetch the workspace to verify actual capacity assignment
                try:
                    refreshed = fabric_client.get_workspace(workspace_name)
                except Exception as refresh_err:
                    logger.error(f"Error assigning workspace to capacity: {e}")
                    logger.error(f"   Additionally, failed to verify workspace state: {refresh_err}")
                    raise e from refresh_err
                if refreshed and refreshed.get('capacityId') == capacity_id:
                    logger.warning(f"Assignment call failed but workspace is already on the correct capacity. Continuing...")
                else:
                    logger.error(f"Error assigning workspace to capacity: {e}")
                    raise
    else:
        # Create new workspace
        logger.info(f"   Creating new workspace: {workspace_name}")
        try:
            workspace_id = fabric_client.create_workspace(workspace_name)
            logger.info(f"   Created workspace: {workspace_name} ({workspace_id})")
        except FabricApiError as e:
            logger.error(f"Error creating workspace: {e}")
            raise
        
        # Assign workspace to capacity
        logger.info(f"   Assigning workspace to capacity: {capacity_name}")
        try:
            fabric_client.assign_workspace_to_capacity(workspace_id, capacity_id)
            logger.info(f"   Workspace assigned to capacity")
        except FabricApiError as e:
            logger.error(f"Error assigning new workspace to capacity: {e}")
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
  python step_workspace_setup.py --capacity-name "MyCapacity" --workspace-name "MyWorkspace"
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
        
        logger.info(f"\n🎉 Final Results:")
        logger.info(f"   Workspace Name: {args.workspace_name}")
        logger.info(f"   Workspace ID: {workspace_id}")
        logger.info(f"   Capacity: {args.capacity_name}")
        logger.info(f"   Status: Ready for use!")
        
    except FabricApiError as e:
        logger.error(f"Fabric API Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

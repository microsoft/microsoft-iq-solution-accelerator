#!/usr/bin/env python3
"""
Fabric Eventhouse Setup Module

This module provides Eventhouse setup functionality for Microsoft Fabric operations.
It creates an Eventhouse if it doesn't already exist and manages database configuration.

Usage:
    python fabric_eventhouse.py --workspace-id "workspace-guid" --eventhouse-name "MyEventhouse"
    python fabric_eventhouse.py --workspace-id "workspace-guid" --eventhouse-name "MyEventhouse" --database-name "MyDatabase"

Requirements:
    - fabric_api.py module in the same directory
    - Azure CLI authentication or other Azure credentials configured
    - Appropriate permissions to create Eventhouses in the workspace
"""

import argparse
import sys
import time
from typing import Optional
from content_packs.manufacturing.scripts.fabric_api import FabricWorkspaceApiClient, FabricApiError


def _rename_default_database(workspace_client: FabricWorkspaceApiClient, 
                            eventhouse_name: str, 
                            database_name: str,
                            max_retries: int = 3,
                            retry_delay: float = 2.0) -> bool:
    """
    Helper function to rename the default database of an eventhouse.
    
    Args:
        workspace_client: The Fabric workspace API client
        eventhouse_name: Current name of the eventhouse (and default database)
        database_name: Desired name for the database
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        True if rename was successful, False otherwise
    """
    if not database_name or not database_name.strip():
        return True  # Nothing to do
        
    database_name = database_name.strip()
    
    print(f"🔄 Attempting to rename default database to '{database_name}'...")
    
    for attempt in range(max_retries):
        try:
            # Find the default database (should have the same name as the eventhouse)
            default_database = workspace_client.get_kql_database_by_name(eventhouse_name)
            
            if default_database:
                current_name = default_database.get('displayName', '')
                
                # Check if already has the desired name
                if current_name == database_name:
                    print(f"ℹ️  Default database already has the desired name '{database_name}'")
                    return True
                    
                # Rename the database
                print(f"🏗️  Renaming default database from '{current_name}' to '{database_name}'...")
                workspace_client.update_kql_database(
                    database_id=default_database.get('id'),
                    display_name=database_name
                )
                print(f"✅ Successfully renamed default database to '{database_name}'")
                return True
            else:
                if attempt < max_retries - 1:
                    print(f"⏳ Default database '{eventhouse_name}' not found yet, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"⚠️  Could not find default database '{eventhouse_name}' after {max_retries} attempts")
                    return False
                    
        except FabricApiError as e:
            if attempt < max_retries - 1:
                print(f"⏳ Database rename failed, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay)
            else:
                print(f"⚠️  Failed to rename default database after {max_retries} attempts: {e}")
                return False
    
    return False


def setup_eventhouse(workspace_client: FabricWorkspaceApiClient,
                    eventhouse_name: str,
                    database_name: Optional[str] = None) -> object:
    """
    Set up an Eventhouse in the specified workspace.
    
    Args:
        workspace_client: Authenticated FabricWorkspaceApiClient instance
        eventhouse_name: Name of the Eventhouse to create
        database_name: Optional name for the default database. If provided, 
                      the default database will be renamed from the eventhouse name to this name.
        
    Returns:
        Eventhouse object if successful, None otherwise
    """
    try:
        print(f"🔍 Using provided Fabric Workspace API client...")
        
        print(f"🔍 Checking if Eventhouse '{eventhouse_name}' already exists...")
        existing_eventhouse = workspace_client.get_eventhouse_by_name(eventhouse_name)
        
        if existing_eventhouse:
            eventhouse_id = existing_eventhouse.get('id')
            print(f"📋 Found existing Eventhouse:")
            print(f"   Name: {existing_eventhouse.get('displayName', 'Unknown')}")
            print(f"   ID: {eventhouse_id}")
            print(f"   Type: {existing_eventhouse.get('type', 'Unknown')}")
            
            # Rename the default database if a database name is provided
            _rename_default_database(workspace_client, eventhouse_name, database_name)
            
            return existing_eventhouse
            
        print(f"📁 Creating new Eventhouse: '{eventhouse_name}'")
        try:
            result = workspace_client.create_eventhouse(display_name=eventhouse_name)
            
            if result and isinstance(result, dict):
                eventhouse_id = result.get('id')
                print(f"✅ Successfully created Eventhouse!")
                print(f"   Name: {result.get('displayName', eventhouse_name)}")
                print(f"   ID: {eventhouse_id}")
                print(f"   Type: {result.get('type', 'Eventhouse')}")
                
                # Verify creation by fetching details
                print(f"🔍 Verifying Eventhouse creation...")
                try:
                    result = workspace_client.get_eventhouse_by_id(eventhouse_id)
                    print(f"✅ Verification successful!")
                    print(f"   Status: Active")
                    
                    # Rename the default database if a database name is provided
                    _rename_default_database(workspace_client, eventhouse_name, database_name)
                    
                    return result
                except FabricApiError as e:
                    print(f"⚠️  Eventhouse created but verification failed: {e}")
                    return result  # Still consider it successful
            else:
                print(f"❌ Eventhouse creation returned unexpected result: {result}")
                return None
                
        except FabricApiError as e:
            print(f"❌ Failed to create Eventhouse: {e}")
            return None
        
    except FabricApiError as e:
        print(f"❌ FabricApiError ({e.status_code}): {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main function to handle command line arguments and execute Eventhouse setup."""
    parser = argparse.ArgumentParser(
        description="Set up an Eventhouse in Microsoft Fabric",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fabric_eventhouse.py --workspace-id "12345678-1234-1234-1234-123456789abc" --eventhouse-name "ManufacturingEventhouse"
        """
    )
    
    parser.add_argument(
        "--workspace-id",
        help="ID of the Fabric workspace (can also use AZURE_FABRIC_WORKSPACE_ID env var)"
    )
    
    parser.add_argument(
        "--eventhouse-name",
        default="ManufacturingEventhouse",
        help="Name of the Eventhouse to create (default: ManufacturingEventhouse, can also use AZURE_EVENTHOUSE_NAME env var)"
    )
    
    parser.add_argument(
        "--database-name",
        help="Optional name for the default database. If provided, the default database will be renamed from the eventhouse name to this name."
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the main logic
    from content_packs.manufacturing.scripts.fabric_auth import authenticate_workspace
    
    workspace_client = authenticate_workspace(args.workspace_id)
    if not workspace_client:
        print("❌ Failed to authenticate workspace-specific Fabric API client")
        sys.exit(1)
    
    result = setup_eventhouse(
        workspace_client=workspace_client,
        eventhouse_name=args.eventhouse_name,
        database_name=args.database_name
    )
    
    print(f"\n✅ Eventhouse ID: {result.get('id') if result else 'Failed'}")
    print(f"✅ Eventhouse Name: {result.get('displayName') if result else 'Failed'}")


if __name__ == "__main__":
    main()

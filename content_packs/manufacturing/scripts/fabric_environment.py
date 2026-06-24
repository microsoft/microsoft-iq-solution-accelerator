#!/usr/bin/env python3
"""
Fabric Environment Setup Module

This module provides Environment setup functionality for Microsoft Fabric operations.
It creates an Environment if it doesn't already exist, or updates it if it does exist,
using the specified environment.yml configuration.

Usage:
    python fabric_environment.py --workspace-id "workspace-guid" --environment-name "MyEnvironment"
    python fabric_environment.py --workspace-id "workspace-guid" --environment-name "MyEnvironment" --description "My Environment Description"
    python fabric_environment.py --workspace-id "workspace-guid" --environment-name "MyEnvironment" --environment-yml-path "path/to/environment.yml"

Requirements:
    - fabric_api.py module in the same directory
    - Azure CLI authentication or other Azure credentials configured
    - Appropriate permissions to create/update Environments in the workspace
"""

import argparse
import sys
import os
import base64
from typing import Optional, Dict, Any
from content_packs.manufacturing.scripts.fabric_api import FabricWorkspaceApiClient


def read_environment_yml(file_path: str) -> str:
    """
    Read environment.yml file content.
    
    Args:
        file_path: Path to the environment.yml file
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: If file can't be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Environment file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading environment file {file_path}: {e}")


def setup_environment(workspace_client: FabricWorkspaceApiClient, 
                     environment_name: str,
                     description: Optional[str] = None,
                     environment_yml_path: Optional[str] = None,
                     folder_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create or update an Environment in the workspace.
    Check if environment exists first, create only if needed, then update configuration.
    
    Args:
        workspace_client: Authenticated FabricWorkspaceApiClient instance
        environment_name: Name of the environment
        description: Optional description for the environment
        environment_yml_path: Optional path to environment.yml file
        folder_id: Optional folder ID where to create the environment
        
    Returns:
        dict: Environment information
    """
    print(f"🌍 Setting up Environment: '{environment_name}'")
    
    # Step 1: Check if environment already exists
    try:
        environment_info = workspace_client.get_environment_by_name(environment_name)
        
        if environment_info:
            environment_id = environment_info['id']
            print(f"ℹ️  Using existing Environment: '{environment_name}' ({environment_id})")
        else:
            # Step 2: Create the environment if it doesn't exist
            print(f"📁 Creating new Environment: '{environment_name}'")
            environment_info = workspace_client.create_environment(
                display_name=environment_name,
                description=description,
                folder_id=folder_id
            )
            environment_id = environment_info['id']
            print(f"✅ Successfully created Environment: '{environment_name}' ({environment_id})")
    except Exception as e:
        print(f"❌ Failed to get or create Environment: {e}")
        raise
    
    # Step 3: Update environment definition if yml file is provided
    if environment_yml_path:
        try:
            print(f"🔄 Updating Environment definition from: {environment_yml_path}")
            
            # Read environment.yml content
            yml_content = read_environment_yml(environment_yml_path)
            yml_base64 = base64.b64encode(yml_content.encode('utf-8')).decode('utf-8')
            
            # Update environment definition
            success = workspace_client.update_environment_definition(
                environment_id=environment_id,
                environment_yml_base64=yml_base64
            )
            
            if success:
                print(f"✅ Successfully updated Environment definition: '{environment_name}'")
                
                # Publish the environment to make it available
                print(f"📤 Publishing Environment: '{environment_name}'")
                workspace_client.publish_environment(environment_id)
                print(f"✅ Successfully published Environment: '{environment_name}'")
            else:
                print(f"⚠️  Failed to update Environment definition: '{environment_name}'")
        except Exception as e:
            print(f"❌ Failed to update Environment configuration: {e}")
            # Don't re-raise here - environment was created successfully
    else:
        print(f"ℹ️  No environment.yml provided, skipping configuration update")
    
    return environment_info


def main():
    """Main function to handle command line arguments and execute environment setup."""
    parser = argparse.ArgumentParser(
        description='Create or update a Microsoft Fabric Environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Create basic environment
  python fabric_environment.py --workspace-id "12345678-1234-1234-1234-123456789abc" --environment-name "DataProcessing"
  
  # Create environment with description
  python fabric_environment.py --workspace-id "12345678-1234-1234-1234-123456789abc" --environment-name "DataProcessing" --description "Environment for data processing tasks"
  
  # Create/update environment with yml configuration
  python fabric_environment.py --workspace-id "12345678-1234-1234-1234-123456789abc" --environment-name "DataProcessing" --environment-yml-path "../../definitions/environment/Libraries/PublicLibraries/environment.yml"
        '''
    )
    
    parser.add_argument('--workspace-id', 
                      required=True,
                      help='Workspace ID (GUID) where the environment will be created')
    
    parser.add_argument('--environment-name',
                      required=True, 
                      help='Name of the environment to create or update')
    
    parser.add_argument('--description',
                      help='Optional description for the environment')
    
    parser.add_argument('--environment-yml-path',
                      help='Optional path to environment.yml file to configure the environment')
    
    parser.add_argument('--folder-id',
                      help='Optional folder ID where to create the environment')
    
    args = parser.parse_args()
    
    try:
        # Initialize Fabric API client for the workspace
        workspace_client = FabricWorkspaceApiClient(workspace_id=args.workspace_id)
        
        # Set default environment.yml path if not provided
        environment_yml_path = args.environment_yml_path
        if not environment_yml_path:
            # Default to the environment.yml in the project structure
            script_dir = os.path.dirname(os.path.abspath(__file__))
            default_yml_path = os.path.join(script_dir, "..", "..", "..", "src", "definitions", "environment", "Libraries", "PublicLibraries", "environment.yml")
            default_yml_path = os.path.normpath(default_yml_path)
            
            if os.path.exists(default_yml_path):
                environment_yml_path = default_yml_path
                print(f"ℹ️  Using default environment.yml: {environment_yml_path}")
            else:
                print(f"ℹ️  No environment.yml specified and default not found at: {default_yml_path}")
        
        # Setup the environment
        environment_info = setup_environment(
            workspace_client=workspace_client,
            environment_name=args.environment_name,
            description=args.description,
            environment_yml_path=environment_yml_path,
            folder_id=args.folder_id
        )
        
        # Print summary
        print("\n" + "="*50)
        print("📋 ENVIRONMENT SETUP SUMMARY")
        print("="*50)
        print(f"Environment Name: {environment_info.get('displayName', 'N/A')}")
        print(f"Environment ID: {environment_info.get('id', 'N/A')}")
        print(f"Workspace ID: {args.workspace_id}")
        if args.description:
            print(f"Description: {args.description}")
        if environment_yml_path:
            print(f"Configuration File: {environment_yml_path}")
        if args.folder_id:
            print(f"Folder ID: {args.folder_id}")
        print("="*50)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
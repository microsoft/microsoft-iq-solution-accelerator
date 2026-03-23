import sys
import os

# Add current directory to path so local modules can be imported
sys.path.append(os.path.dirname(__file__))

from fabric_api import create_fabric_client, FabricApiError
from helpers.config import SOLUTION_NAME, default_workspace_name
from helpers.utils import get_required_env_var


####################
# Variables set up #
####################

##############################
# Environment Variable Setup #
##############################

# Load configuration from environment variables
solution_suffix = get_required_env_var("SOLUTION_SUFFIX")
# Use custom workspace name if provided; fall back to auto-generated name.
# 'or' handles both None (unset) and '' (set to empty by CI/CD when var is not configured).
workspace_name = os.getenv("FABRIC_WORKSPACE_NAME") or default_workspace_name(solution_suffix)
workspace_id = os.getenv("FABRIC_WORKSPACE_ID")
if workspace_name and workspace_id:
    print("⚠️ WARNING: Both FABRIC_WORKSPACE_NAME and FABRIC_WORKSPACE_ID are set")
    print("   Using workspace name and ignoring workspace ID...")
    workspace_id = None

print(f"🗑️  Starting {SOLUTION_NAME} workspace removal from Microsoft Fabric")
print(f"📋 Solution suffix: {solution_suffix}")
if workspace_name:
    print(f"📋 Target workspace name: {workspace_name}")
else:
    print(f"📋 Target workspace ID: {workspace_id}")
print("-" * 60)

##########################
# Clients authentication #
##########################

print("🔐 Authenticating Fabric client...")
# Initialize Fabric API client
try:
    fabric_client = create_fabric_client()
    print("✅ Fabric API client authenticated successfully")
except Exception as e:
    print(f"⚠️ WARNING: Failed to authenticate with Fabric APIs")
    print(f"   Details: {str(e)}")
    print("   Solution: Please ensure you are logged in with Azure CLI: az login")
    print("   Exiting gracefully...")
    sys.exit(0)

###########################
# Workspace lookup/verify #
###########################

try:
    # If workspace name is provided, look it up to get the ID
    if workspace_name:
        print(f"🔍 Looking up workspace: '{workspace_name}'")
        workspaces = fabric_client.list_workspaces()
        workspace = next(
            (w for w in workspaces if w['displayName'].lower() == workspace_name.lower()), None)

        if not workspace:
            print(f"⚠️ WARNING: Workspace '{workspace_name}' not found")
            print("   Available workspaces:")
            for ws in workspaces:
                print(f"   - {ws['displayName']} (ID: {ws['id']})")
            print("   Exiting gracefully...")
            sys.exit(0)
        
        workspace_id = workspace['id']
        workspace_display_name = workspace['displayName']
        print(f"✅ Found workspace: '{workspace_display_name}' (ID: {workspace_id})")
    else:
        # If workspace ID is provided, verify it exists
        print(f"🔍 Verifying workspace ID: '{workspace_id}'")
        workspaces = fabric_client.list_workspaces()
        workspace = next(
            (w for w in workspaces if w['id'].lower() == workspace_id.lower()), None)
        
        if not workspace:
            print(f"⚠️ WARNING: Workspace with ID '{workspace_id}' not found")
            print("   Available workspaces:")
            for ws in workspaces:
                print(f"   - {ws['displayName']} (ID: {ws['id']})")
            print("   Exiting gracefully...")
            sys.exit(0)
        
        workspace_display_name = workspace['displayName']
        print(f"✅ Found workspace: '{workspace_display_name}' (ID: {workspace_id})")

except FabricApiError as e:
    if e.status_code == 401:
        print(f"⚠️ WARNING: Unauthorized access to Fabric APIs")
        print("   ⚠️ WARNING: Please review your Fabric permissions and licensing:")
        print("   📋 Check these resources:")
        print("   • Fabric licenses: https://learn.microsoft.com/en-us/fabric/enterprise/licenses")
        print("   • Identity support: https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support")
        print("   • Create Entra app: https://learn.microsoft.com/en-us/rest/api/fabric/articles/get-started/create-entra-app")
        print("   Solution: Ensure you have proper Fabric licensing and permissions")
        print("   Exiting gracefully...")
        sys.exit(0)
    elif e.status_code == 404:
        print(f"⚠️ WARNING: Resource not found")
    elif e.status_code == 403:
        print(f"⚠️ WARNING: Access denied")
        print("   Solution: Ensure you have appropriate permissions")
    else:
        print(f"⚠️ WARNING: Fabric API error")
    print(f"   Status Code: {e.status_code}")
    print(f"   Details: {str(e)}")
    print("   Exiting gracefully...")
    sys.exit(0)
except Exception as e:
    print(f"⚠️ WARNING: Unexpected error during workspace lookup: {str(e)}")
    print("   Exiting gracefully...")
    sys.exit(0)

####################
# Confirmation     #
####################

# Proceeding with deletion in unattended mode
print(f"✅ Proceeding with workspace deletion...")

######################
# Workspace deletion #
######################

try:
    print(f"🗑️  Deleting workspace: '{workspace_display_name}'")
    fabric_client.delete_workspace(workspace_id)
    print(f"✅ Workspace '{workspace_display_name}' deleted successfully")

except FabricApiError as e:
    if e.status_code == 401:
        print(f"⚠️ WARNING: Unauthorized access to Fabric APIs")
        print("   ⚠️ WARNING: Please review your Fabric permissions and licensing:")
        print("   📋 Check these resources:")
        print("   • Fabric licenses: https://learn.microsoft.com/en-us/fabric/enterprise/licenses")
        print("   • Identity support: https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support")
        print("   • Create Entra app: https://learn.microsoft.com/en-us/rest/api/fabric/articles/get-started/create-entra-app")
        print("   Solution: Ensure you have proper Fabric licensing and permissions")
        print("   Exiting gracefully...")
        sys.exit(0)
    elif e.status_code == 404:
        print(f"⚠️ WARNING: Workspace not found (may have already been deleted)")
        print("   This is typically not an issue during cleanup operations")
    elif e.status_code == 403:
        print(f"⚠️ WARNING: Access denied")
        print("   Solution: Ensure you have Admin permissions on this workspace")
    else:
        print(f"⚠️ WARNING: Fabric API error")
    print(f"   Status Code: {e.status_code}")
    print(f"   Details: {str(e)}")
    print("   Exiting gracefully...")
    sys.exit(0)
except Exception as e:
    print(f"⚠️ WARNING: Unexpected error during workspace deletion: {str(e)}")
    print("   Exiting gracefully...")
    sys.exit(0)

##################
# End of program #
##################

print("-" * 60)
print(f"🎉 {SOLUTION_NAME} workspace removal completed successfully!")
print(f"✅ Deleted workspace: {workspace_display_name}")
print(f"✅ Workspace ID: {workspace_id}")
print("-" * 60)
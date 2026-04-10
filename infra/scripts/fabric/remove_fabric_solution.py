import logging
import sys
import os

# Add current directory to path so local modules can be imported
sys.path.append(os.path.dirname(__file__))

from helpers.logging_config import setup_logging

# Configure logging before any other imports so that library modules
# (fabric_api, graph_api, helpers.*) inherit the root logger's settings.
# The log level can be set via ``azd env set LOG_LEVEL DEBUG``.
setup_logging()

# Module-level logger for this entry-point script.  All log calls below
# use this logger; the level and handler are inherited from setup_logging().
logger = logging.getLogger(__name__)

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
    logger.warning("Both FABRIC_WORKSPACE_NAME and FABRIC_WORKSPACE_ID are set")
    logger.warning("   Using workspace name and ignoring workspace ID...")
    workspace_id = None

logger.info(f"🗑️  Starting {SOLUTION_NAME} workspace removal from Microsoft Fabric")
logger.info(f"Solution suffix: {solution_suffix}")
if workspace_name:
    logger.info(f"Target workspace name: {workspace_name}")
else:
    logger.info(f"Target workspace ID: {workspace_id}")
logger.info("-" * 60)

##########################
# Clients authentication #
##########################

logger.info("🔐 Authenticating Fabric client...")
# Initialize Fabric API client
try:
    fabric_client = create_fabric_client()
    logger.info("   Fabric API client authenticated")
except Exception as e:
    logger.warning(f"Failed to authenticate with Fabric APIs")
    logger.warning(f"   Details: {str(e)}")
    logger.warning("   Solution: Please ensure you are logged in with Azure CLI: az login")
    logger.warning("   Exiting gracefully...")
    sys.exit(0)

###########################
# Workspace lookup/verify #
###########################

try:
    # If workspace name is provided, look it up to get the ID
    if workspace_name:
        logger.info(f"Looking up workspace: '{workspace_name}'")
        workspaces = fabric_client.list_workspaces()
        workspace = next(
            (w for w in workspaces if w['displayName'].lower() == workspace_name.lower()), None)

        if not workspace:
            logger.warning(f"Workspace '{workspace_name}' not found")
            logger.debug("   Available workspaces:")
            for ws in workspaces:
                logger.debug(f"   - {ws['displayName']} (ID: {ws['id']})")
            logger.warning("   Exiting gracefully...")
            sys.exit(0)
        
        workspace_id = workspace['id']
        workspace_display_name = workspace['displayName']
        logger.info(f"Found workspace: '{workspace_display_name}' (ID: {workspace_id})")
    else:
        # If workspace ID is provided, verify it exists
        logger.info(f"Verifying workspace ID: '{workspace_id}'")
        workspaces = fabric_client.list_workspaces()
        workspace = next(
            (w for w in workspaces if w['id'].lower() == workspace_id.lower()), None)
        
        if not workspace:
            logger.warning(f"Workspace with ID '{workspace_id}' not found")
            logger.debug("   Available workspaces:")
            for ws in workspaces:
                logger.debug(f"   - {ws['displayName']} (ID: {ws['id']})")
            logger.warning("   Exiting gracefully...")
            sys.exit(0)
        
        workspace_display_name = workspace['displayName']
        logger.info(f"Found workspace: '{workspace_display_name}' (ID: {workspace_id})")

except FabricApiError as e:
    if e.status_code == 401:
        logger.warning(f"Unauthorized access to Fabric APIs")
        logger.warning("   Please review your Fabric permissions and licensing:")
        logger.warning("   Check these resources:")
        logger.warning("   • Fabric licenses: https://learn.microsoft.com/en-us/fabric/enterprise/licenses")
        logger.warning("   • Identity support: https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support")
        logger.warning("   • Create Entra app: https://learn.microsoft.com/en-us/rest/api/fabric/articles/get-started/create-entra-app")
        logger.warning("   Solution: Ensure you have proper Fabric licensing and permissions")
        logger.warning("   Exiting gracefully...")
        sys.exit(0)
    elif e.status_code == 404:
        logger.warning(f"Resource not found")
    elif e.status_code == 403:
        logger.warning(f"Access denied")
        logger.warning("   Solution: Ensure you have appropriate permissions")
    else:
        logger.warning(f"Fabric API error")
    logger.warning(f"   Status Code: {e.status_code}")
    logger.warning(f"   Details: {str(e)}")
    logger.warning("   Exiting gracefully...")
    sys.exit(0)
except Exception as e:
    logger.warning(f"Unexpected error during workspace lookup: {str(e)}")
    logger.warning("   Exiting gracefully...")
    sys.exit(0)

####################
# Confirmation     #
####################

# Proceeding with deletion in unattended mode
logger.info(f"Proceeding with workspace deletion...")

######################
# Workspace deletion #
######################

try:
    logger.info(f"Deleting workspace: '{workspace_display_name}'")
    fabric_client.delete_workspace(workspace_id)
    logger.info(f"Workspace '{workspace_display_name}' deleted successfully")

except FabricApiError as e:
    if e.status_code == 401:
        logger.warning(f"Unauthorized access to Fabric APIs")
        logger.warning("   Please review your Fabric permissions and licensing:")
        logger.warning("   Check these resources:")
        logger.warning("   • Fabric licenses: https://learn.microsoft.com/en-us/fabric/enterprise/licenses")
        logger.warning("   • Identity support: https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support")
        logger.warning("   • Create Entra app: https://learn.microsoft.com/en-us/rest/api/fabric/articles/get-started/create-entra-app")
        logger.warning("   Solution: Ensure you have proper Fabric licensing and permissions")
        logger.warning("   Exiting gracefully...")
        sys.exit(0)
    elif e.status_code == 404:
        logger.warning(f"Workspace not found (may have already been deleted)")
        logger.warning("   This is typically not an issue during cleanup operations")
    elif e.status_code == 403:
        logger.warning(f"Access denied")
        logger.warning("   Solution: Ensure you have Admin permissions on this workspace")
    else:
        logger.warning(f"Fabric API error")
    logger.warning(f"   Status Code: {e.status_code}")
    logger.warning(f"   Details: {str(e)}")
    logger.warning("   Exiting gracefully...")
    sys.exit(0)
except Exception as e:
    logger.warning(f"Unexpected error during workspace deletion: {str(e)}")
    logger.warning("   Exiting gracefully...")
    sys.exit(0)

##################
# End of program #
##################

logger.info("-" * 60)
logger.info(f"🎉 {SOLUTION_NAME} workspace removal completed successfully!")
logger.info(f"Deleted workspace: {workspace_display_name}")
logger.info(f"Workspace ID:      {workspace_id}")
logger.info("-" * 60)
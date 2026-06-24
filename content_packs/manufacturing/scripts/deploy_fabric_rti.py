#!/usr/bin/env python3
"""
Data pipeline initialization orchestrator script.

This script coordinates the execution of all data pipeline initialization functions
in the correct order, with proper error handling and logging. It uses environment
variables for configuration and calls each function directly.

Functions executed in order:
1. setup_workspace - Create and configure Fabric workspace
2. setup_workspace_administrators - Add workspace administrators
3. setup_eventhouse - Set up Eventhouse in the workspace
4. setup_fabric_database - Set up database tables and schema
5. load_data_to_fabric - Load sample data into Fabric
6. setup_eventhub_connection - Configure Event Hub connection
7. setup_real_time_dashboard - Create real-time dashboard in Fabric
8. create_eventstream - Create Eventstream (empty)
9. create_activator - Create Activator (empty)
10. setup_activator_definition - Configure Activator (Reflex) for real-time alerts  # noqa: E501
11. setup_eventstream_definition - Configure Eventstream with Event Hub to Eventhouse flow  # noqa: E501
12. setup_folder - Create folder for organizing environment and data agent
13. setup_environment - Set up Fabric Environment in the created folder
14. setup_data_agent - Create and configure Data Agent (Preview) with notebook in the folder  # noqa: E501
 
Usage:
    python deploy_fabric_rti.py

Environment Variables (from Bicep outputs):
    AZURE_LOCATION - The location the resources were deployed to
    AZURE_RESOURCE_GROUP - The name of the resource group
    AZURE_SUBSCRIPTION_ID - The Azure subscription ID (from azd environment)
    AZURE_ENV_NAME - The azd environment name (used as solution name)
    AZURE_FABRIC_CAPACITY_NAME - The name of the Fabric capacity resource
    AZURE_FABRIC_CAPACITY_ADMINISTRATORS - The identities added as Fabric Capacity Admin members  # noqa: E501
    AZURE_EVENT_HUB_NAMESPACE_NAME - The name of the Event Hub Namespace created for ingestion  # noqa: E501
    AZURE_EVENT_HUB_NAMESPACE_HOSTNAME - Event Hub Namespace hostname
    AZURE_EVENT_HUB_NAME - The name of the Event Hub for ingestion
    AZURE_EVENT_HUB_RESOURCE_GROUP - Resource group for Event Hub
        (may differ from AZURE_RESOURCE_GROUP for cross-RG scenarios)
    AZURE_EVENT_HUB_SUBSCRIPTION_ID - Subscription ID for Event Hub
        (may differ from AZURE_SUBSCRIPTION_ID for cross-sub scenarios)
    AZURE_EVENT_HUB_AUTHORIZATION_RULE_NAME - Event Hub auth rule name
        (optional, defaults to "RootManageSharedAccessKey")
    SOLUTION_SUFFIX - The solution name suffix used for resource naming
    
Optional Environment Variables (custom configuration):
    FABRIC_WORKSPACE_NAME - Custom name for the Fabric workspace
        (defaults to "Real-Time Intelligence for Operations - {suffix}")
    FABRIC_WORKSPACE_ADMINISTRATORS - Comma-separated list of workspace administrator
        identities (UPNs or GUIDs, optional)
    FABRIC_EVENTHOUSE_NAME - Custom name for the Eventhouse
        (defaults to "rti_eventhouse_{suffix}")
    FABRIC_EVENTHOUSE_DATABASE_NAME - Custom name for the Eventhouse database
        (defaults to "rti_kqldb_{suffix}")
    FABRIC_EVENT_HUB_CONNECTION_NAME - Custom name for the Event Hub connection
        (defaults to "rti_eventhub_connection_{suffix}")
    FABRIC_RTIDASHBOARD_NAME - Custom name for the real-time dashboard
        (defaults to "rti_dashboard_{suffix}")
    FABRIC_EVENTSTREAM_NAME - Custom name for the Eventstream
        (defaults to "rti_eventstream_{suffix}")
    FABRIC_ACTIVATOR_NAME - Custom name for the Activator
        (defaults to "rti_activator_{suffix}")
    FABRIC_ACTIVATOR_ALERTS_EMAIL - Email address for activator alerts
        (defaults to "alerts@contoso.com")
    FABRIC_ENVIRONMENT_NAME - Custom name for the Environment
        (defaults to "rti_environment_{suffix}")
    FABRIC_DATA_AGENT_NAME - Custom name for the Data Agent
        (defaults to "rti_dataagent_{suffix}")
    FABRIC_NOTEBOOK_NAME - Custom name for the Data Agent configuration notebook
        (defaults to "rti_notebook_{suffix}")
    FABRIC_FOLDER_NAME - Custom name for the folder containing environment and
        data agent (defaults to "rti_folder_{suffix}")
"""

import os
import sys
from datetime import datetime

# Add current directory to path so we can import local modules
sys.path.append(os.path.dirname(__file__))

# Import pipeline functions  # noqa: E402 (imports after code)
from content_packs.manufacturing.scripts.fabric_auth import authenticate, authenticate_workspace
from content_packs.manufacturing.scripts.fabric_api import FabricApiError
from content_packs.manufacturing.scripts.fabric_eventhouse import setup_eventhouse
from content_packs.manufacturing.scripts.fabric_database import setup_fabric_database
from content_packs.manufacturing.scripts.fabric_data_ingester import load_data_to_fabric
from content_packs.manufacturing.scripts.fabric_environment import setup_environment
from content_packs.manufacturing.scripts.fabric_common_utils import (
    get_required_env_var,
    print_step,
    print_steps_summary
)


def main():
    # Calculate repository root directory (3 levels up from this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    
    # Load configuration from environment variables
    solution_name = get_required_env_var("AZURE_ENV_NAME")
    solution_suffix = get_required_env_var("SOLUTION_SUFFIX")
    subscription_id = get_required_env_var("AZURE_SUBSCRIPTION_ID")
    resource_group_name = get_required_env_var("AZURE_RESOURCE_GROUP")
    capacity_name = get_required_env_var("AZURE_FABRIC_CAPACITY_NAME")
    event_hub_name = get_required_env_var("AZURE_EVENT_HUB_NAME")
    event_hub_namespace_name = get_required_env_var("AZURE_EVENT_HUB_NAMESPACE_NAME")
    # Event Hub resource group and subscription resolution
    # When using existing Event Hub from different RG/subscription, Bicep
    # outputs correct values. Otherwise, defaults to deployment context.
    event_hub_resource_group_name = (
        os.getenv("AZURE_EVENT_HUB_RESOURCE_GROUP")
        or resource_group_name
    )
    event_hub_subscription_id = (
        os.getenv("AZURE_EVENT_HUB_SUBSCRIPTION_ID")
        or subscription_id
    )
    event_hub_authorization_rule_name = os.getenv(
        "AZURE_EVENT_HUB_AUTHORIZATION_RULE_NAME",
        "RootManageSharedAccessKey"
    )
    workspace_name = os.getenv(
        "FABRIC_WORKSPACE_NAME",
        f"Real-Time Intelligence for Operations - {solution_suffix}"
    )
    workspace_administrators = os.getenv("FABRIC_WORKSPACE_ADMINISTRATORS")
    eventhouse_name = os.getenv(
        "FABRIC_EVENTHOUSE_NAME",
        f"rti_eventhouse_{solution_suffix}"
    )
    eventhouse_database_name = os.getenv(
        "FABRIC_EVENTHOUSE_DATABASE_NAME",
        f"rti_kqldb_{solution_suffix}"
    )
    event_hub_connection_name = os.getenv(
        "FABRIC_EVENT_HUB_CONNECTION_NAME",
        f"rti_eventhub_connection_{solution_suffix}"
    )
    dashboard_title = os.getenv(
        "FABRIC_RTIDASHBOARD_NAME",
        f"rti_dashboard_{solution_suffix}"
    )
    eventstream_name = os.getenv(
        "FABRIC_EVENTSTREAM_NAME",
        f"rti_eventstream_{solution_suffix}"
    )
    activator_name = os.getenv(
        "FABRIC_ACTIVATOR_NAME",
        f"rti_activator_{solution_suffix}"
    )
    activator_alerts_email = os.getenv(
        "FABRIC_ACTIVATOR_ALERTS_EMAIL",
        "alerts@contoso.com"
    )
    data_agent_name = os.getenv(
        "FABRIC_DATA_AGENT_NAME",
        f"rti_dataagent_{solution_suffix}"
    )
    folder_name = os.getenv(
        "FABRIC_DATA_AGENT_CONFIGURATION_FOLDER_NAME",
        f"rti_dataagentconfig_{solution_suffix}"
    )
    environment_name = os.getenv(
        "FABRIC_DATA_AGENT_CONFIGURATION_ENVIRONMENT_NAME",
        f"rti_environment_{solution_suffix}"
    )
    notebook_name = os.getenv(
        "FABRIC_DATA_AGENT_CONFIGURATION_NOTEBOOK_NAME",
        f"rti_notebook_{solution_suffix}"
    )

    # Note: This solution expects deployments that reuse existing Event Hub resources
    # to target the same Azure Resource Group where those resources live.
    
    # Show initialization summary
    print(f"🏭 {solution_name} Initialization")
    print("="*60)
    print(f"Capacity: {capacity_name}")
    print(f"Workspace: {workspace_name}")
    print(f"Eventhouse Name: {eventhouse_name}")
    print(f"Kusto Database Name: {eventhouse_database_name}")
    print(f"Event Hub Connection Name: {event_hub_connection_name}")
    print(f"Event Hub Namespace Name: {event_hub_namespace_name}")
    print(f"Event Hub Name: {event_hub_name}")
    print(f"Event Hub Resource Group: {event_hub_resource_group_name}")
    print(f"Environment Name: {environment_name}")
    print(f"Data Agent Name: {data_agent_name}")
    print(f"Folder Name: {folder_name}")
    print(f"Activator Name: {activator_name}")
    print(f"Activator Alerts Email: {activator_alerts_email}")
    print(f"Solution Suffix: {solution_suffix}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Authenticate Fabric API client once
    print("\n🔐 Authenticating Fabric API client...")
    fabric_client = authenticate()
    if not fabric_client:
        print("❌ Failed to authenticate with Fabric APIs")
        sys.exit(1)
    print("✅ Authentication successful")
    
    executed_steps = []
        
    # Create workspace-specific client for subsequent operations
    print("\n🔐 Creating workspace-specific Fabric API client...")
    workspace_client = authenticate_workspace(workspace_id)
    if not workspace_client:
        print("❌ Failed to authenticate workspace-specific Fabric API client")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)
    print("✅ Workspace-specific authentication successful")
    
    # Step 3: Setup eventhouse
    print_step(
        3, 14,
        "Setting up Fabric Eventhouse",
        eventhouse_name=eventhouse_name,
        workspace_id=workspace_id,
        database_name=eventhouse_database_name
    )
    try:
        eventhouse_result = setup_eventhouse(
            workspace_client=workspace_client,
            eventhouse_name=eventhouse_name,
            database_name=eventhouse_database_name
        )
        if eventhouse_result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: setup_eventhouse")
        executed_steps.append("setup_eventhouse")
    except Exception as e:
        print(f"❌ Exception while executing setup_eventhouse: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)

    kusto_cluster_uri = eventhouse_result.get('properties')['queryServiceUri']
    eventhouse_database_id = (
        eventhouse_result.get('properties').get('databasesItemIds')[0]
    )
    
    # Step 5: Setup database
    print_step(4, 14, "Setting up Fabric database and table schemas", cluster_uri=kusto_cluster_uri, database_name=eventhouse_database_name)
    try:
        result = setup_fabric_database(
            cluster_uri=kusto_cluster_uri,
            database_name=eventhouse_database_name
        )
        if result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: setup_fabric_database")
        executed_steps.append("setup_fabric_database")
    except Exception as e:
        print(f"❌ Exception while executing setup_fabric_database: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)
    
    # Step 6: Load data
    data_path = os.path.join(repo_dir, "infra", "data")
    print_step(5, 14, "Loading sample data into Fabric database", cluster_uri=kusto_cluster_uri, database_name=eventhouse_database_name, data_path=data_path)
    try:
        result = load_data_to_fabric(
            cluster_uri=kusto_cluster_uri,
            database_name=eventhouse_database_name,
            data_path=data_path,
            refresh_event_dates=True,
            overwrite_existing=True
        )
        if result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: load_data_to_fabric")
        executed_steps.append("load_data_to_fabric")
    except Exception as e:
        print(f"❌ Exception while executing load_data_to_fabric: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)

    # Step 6: Setup Event Hub connection
    print_step(
        6, 14,
        "Setting up Event Hub connection",
        connection_name=event_hub_connection_name,
        namespace_name=event_hub_namespace_name,
        event_hub_name=event_hub_name
    )
    try:
        eventhub_connection_result = setup_eventhub_connection(
            fabric_client=fabric_client,
            connection_name=event_hub_connection_name,
            namespace_name=event_hub_namespace_name,
            event_hub_name=event_hub_name,
            subscription_id=event_hub_subscription_id,
            resource_group_name=event_hub_resource_group_name,
            authorization_rule_name=event_hub_authorization_rule_name
        )
        if eventhub_connection_result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: setup_eventhub_connection")
        executed_steps.append("setup_eventhub_connection")
        
        # Extract the connection ID for use in eventstream setup
        eventhub_connection_id = (
            eventhub_connection_result.get('id')
            if eventhub_connection_result else None
        )
    except Exception as e:
        print(f"❌ Exception while executing setup_eventhub_connection: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)

    # Step 9: Setup dashboard
    # Build dashboard file path relative to repository root
    rti_dashboard_file_path = os.path.join(
        repo_dir, "src", "definitions",
        "realTimeDashboard", "RealTimeDashboard.json"
    )
    
    print_step(7, 14, "Setting up Real-time Dashboard", workspace_id=workspace_id, dashboard_title=dashboard_title, cluster_uri=kusto_cluster_uri)
    try:
        dashboard_result = setup_real_time_dashboard(
            workspace_client=workspace_client,
            workspace_id=workspace_id,
            dashboard_title=dashboard_title,
            rti_dashboard_file_path=rti_dashboard_file_path,
            cluster_uri=kusto_cluster_uri,
            eventhouse_database_id=eventhouse_database_id
        )
        if dashboard_result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: setup_real_time_dashboard")
        executed_steps.append("setup_real_time_dashboard")
    except Exception as e:
        print(f"❌ Exception while executing setup_real_time_dashboard: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)

    # Step 10: Create eventstream
    print_step(
        8, 14,
        "Creating Eventstream",
        workspace_id=workspace_id,
        eventstream_name=eventstream_name
    )
    try:
        eventstream_result = create_eventstream(
            workspace_client=workspace_client,
            eventstream_name=eventstream_name
        )
        if eventstream_result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: create_eventstream")
        executed_steps.append("create_eventstream")
        eventstream_id = eventstream_result.get('id') if eventstream_result else None
    except Exception as e:
        print(f"❌ Exception while executing create_eventstream: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)

    # Step 11: Create activator
    print_step(
        9, 14,
        "Creating Activator",
        workspace_id=workspace_id,
        activator_name=activator_name
    )
    try:
        activator_result = create_activator(
            workspace_client=workspace_client,
            activator_name=activator_name,
            activator_description=(
                f"Real-time alerts and notifications for {solution_name}"
            )
        )
        if activator_result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: create_activator")
        executed_steps.append("create_activator")
        activator_id = activator_result.get('id') if activator_result else None
    except Exception as e:
        print(f"❌ Exception while executing create_activator: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)

    # Step 12: Update activator definition
    # Build activator file path relative to repository root
    activator_file_path = os.path.join(
        repo_dir, "src", "definitions", "activator", "ReflexEntities.json"
    )
    
    print_step(10, 14, "Updating Activator Definition", workspace_id=workspace_id, activator_id=activator_id, eventstream_name=eventstream_name)
    try:
        activator_definition_result = setup_activator_definition(
            workspace_client=workspace_client,
            workspace_id=workspace_id,
            activator_id=activator_id,
            activator_file_path=activator_file_path,
            eventstream_id=eventstream_id,
            eventstream_name=eventstream_name,
            activator_alerts_email=activator_alerts_email
        )
        if activator_definition_result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: setup_activator_definition")
        executed_steps.append("setup_activator_definition")
    except Exception as e:
        print(f"❌ Exception while executing setup_activator_definition: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)

    # Step 13: Update eventstream definition
    # Build eventstream file path relative to repository root
    eventstream_file_path = os.path.join(
        repo_dir, "src", "definitions", "eventstream", "eventstream.json"
    )
    
    print_step(11, 14, "Updating Eventstream Definition", workspace_id=workspace_id, eventstream_id=eventstream_id, eventhouse_database_name=eventhouse_database_name)
    try:
        # Create destination-friendly names (without underscores) for eventstream
        eventhouse_destination_name = eventhouse_name.replace('_', '-')
        activator_destination_name = activator_name.replace('_', '-')
        
        eventstream_definition_result = setup_eventstream_definition(
            workspace_client=workspace_client,
            workspace_id=workspace_id,
            eventstream_id=eventstream_result.get('id') if eventstream_result else None,
            eventstream_file_path=eventstream_file_path,
            eventhouse_database_id=eventhouse_database_id,
            eventhouse_database_name=eventhouse_database_name,
            eventhouse_table_name="events",
            eventhub_connection_id=eventhub_connection_id,
            source_name=event_hub_name,
            eventhouse_name=eventhouse_destination_name,
            stream_name=eventstream_name,
            activator_name=activator_destination_name,
            activator_id=activator_id
        )
        if eventstream_definition_result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: setup_eventstream_definition")
        executed_steps.append("setup_eventstream_definition")
    except Exception as e:
        print(f"❌ Exception while executing setup_eventstream_definition: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)
    
    # Step 12: Setup folder
    print_step(
        12, 14,
        "Setting up Fabric folder",
        folder_name=folder_name,
        workspace_id=workspace_id
    )
    try:
        folder_result = setup_folder(
            workspace_client=workspace_client,
            folder_name=folder_name
        )
        if folder_result is None:
            raise Exception("setup_folder returned None")
        folder_id = folder_result.get('id')
        print(f"✅ Successfully completed: setup_folder")
        executed_steps.append("setup_folder")
    except Exception as e:
        print(f"❌ Exception while executing setup_folder: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)
    
    # Step 13: Setup environment
    environment_yml_path = os.path.join(
        repo_dir, "src", "definitions", "environment",
        "Libraries", "PublicLibraries", "environment.yml"
    )
    print_step(
        13, 14,
        "Setting up Fabric environment",
        environment_name=environment_name,
        workspace_id=workspace_id,
        environment_yml_path=environment_yml_path,
        folder_id=folder_id
    )
    try:
        environment_result = setup_environment(
            workspace_client=workspace_client,
            environment_name=environment_name,
            description=f"Environment for {solution_name}",
            environment_yml_path=environment_yml_path,
            folder_id=folder_id
        )
        if environment_result is None:
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(1)
        print(f"✅ Successfully completed: setup_environment")
        executed_steps.append("setup_environment")
        environment_id = environment_result.get('id')
    except Exception as e:
        print(f"❌ Exception while executing setup_environment: {e}")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(1)

    # Step 13: Create data agent (Preview Feature)
    print(f"\n⚠️  PREVIEW FEATURE WARNING:")
    print(f"   Microsoft Fabric Data Agent creation is in preview and may have limitations.")  # noqa: E501
    print(f"   If this step fails, you can complete setup manually using: docs/FabricDataAgentGuide.md")  # noqa: E501
    print_step(
        14, 14,
        "Creating and configuring Data Agent (Preview)",
        data_agent_name=data_agent_name,
        workspace_id=workspace_id,
        environment_id=environment_id,
        folder_id=folder_id
    )
    try:
        data_agent_result = setup_data_agent(
            workspace_client=workspace_client,
            data_agent_name=data_agent_name,
            kusto_db_id=eventhouse_database_id,
            kusto_db_workspace_id=workspace_id,
            environment_id=environment_id,
            notebook_name=notebook_name,
            notebook_folder_id=folder_id
        )
        if data_agent_result is None:
            print(f"⚠️ Failed to create data agent: Unknown error")
            print(f"📄 To complete data agent setup manually:")
            print(f"   1. Open Microsoft Fabric portal: https://app.fabric.microsoft.com")  # noqa: E501
            print(f"   2. Navigate to your workspace: {workspace_name}")
            print(f"   3. Create a new Data Agent item with name: {data_agent_name}")
            print(f"   4. Configure the agent using the KQL database: {eventhouse_database_name}")  # noqa: E501
            print(f"\n📝 For detailed instructions, see: docs/FabricDataAgentGuide.md")
            print_steps_summary(solution_name, solution_suffix, executed_steps, [])
            sys.exit(0)
        print(f"✅ Successfully completed: setup_data_agent")
        executed_steps.append("setup_data_agent")
        data_agent_id = data_agent_result.get('id')
    except Exception as e:
        print(f"⚠️ Exception while executing setup_data_agent: {e}")
        print(f"📄 To complete data agent setup manually:")
        print(f"   1. Open Microsoft Fabric portal: https://app.fabric.microsoft.com")
        print(f"   2. Navigate to your workspace: {workspace_name}")
        print(f"   3. Create a new Data Agent item with name: {data_agent_name}")
        print(f"   4. Configure the agent using the KQL database: {eventhouse_database_name}")
        print(f"\n📝 For detailed instructions, see: docs/FabricDataAgentGuide.md")
        print_steps_summary(solution_name, solution_suffix, executed_steps, [])
        sys.exit(0)
    
    # Success!
    print(f"\n🎉 {solution_name} data initialization completed successfully!")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print_steps_summary(solution_name, solution_suffix, executed_steps)

    # Construct URLs for the resources
    dashboard_id = dashboard_result.get('id') if dashboard_result else None
    eventstream_id = eventstream_result.get('id') if eventstream_result else None
    activator_id = activator_result.get('id') if activator_result else None
    eventhouse_id = eventhouse_result.get('id') if eventhouse_result else None
    
    # Azure
    eventhub_namespace_url = (
        f"https://portal.azure.com/#@/resource/subscriptions/"
        f"{event_hub_subscription_id}/resourceGroups/"
        f"{event_hub_resource_group_name}/providers/Microsoft.EventHub/"
        f"namespaces/{event_hub_namespace_name}/overview"
    )
    capacity_url = (
        f"https://portal.azure.com/#@/resource/subscriptions/"
        f"{subscription_id}/resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.Fabric/capacities/{capacity_name}/overview"
    )
    
    # Fabric
    workspace_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}?experience=fabric-developer"
    eventhouse_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}/eventhouses/{eventhouse_id}?experience=fabric-developer" if eventhouse_id else None
    kql_database_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}/databases/{eventhouse_database_id}?experience=fabric-developer" if eventhouse_database_id else None
    dashboard_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}/kustodashboards/{dashboard_id}?experience=fabric-developer" if dashboard_id else None
    eventstream_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}/eventstreams/{eventstream_id}?experience=fabric-developer" if eventstream_id else None
    activator_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}/reflexes/{activator_id}?experience=fabric-developer" if activator_id else None
    eventhub_connection_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}/gateways?experience=fabric-developer"
    environment_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}/sparkenvironments/{environment_id}?experience=fabric-developer" if environment_id else None
    data_agent_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}/aiskills/{data_agent_id}?experience=fabric-developer" if data_agent_id else None

    print(f"\n" + "="*60)
    print(f"🎉 {solution_name.upper()} DEPLOYMENT COMPLETE!")
    print(f"="*60)
    print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏷️  Solution: {solution_suffix}")
    
    print(f"\n✅ DEPLOYED RESOURCES:")
    print(f"   🏠 Workspace:    {workspace_name}")
    print(f"   📁 Folder:       {folder_name}")
    print(f"   🌍 Environment:  {environment_name}")
    print(f"   🤖 Data Agent:   {data_agent_name} (✅ Configured)")
    print(f"   🏛️ Eventhouse:   {eventhouse_name}")
    print(f"   🗄️ Database:     {eventhouse_database_name} (✅ Data loaded)")
    print(f"   📊 Dashboard:    {dashboard_title}")
    print(f"   🌊 Eventstream:  {eventstream_name}")
    print(f"   🚨 Activator:    {activator_name}")
    print(f"   🔗 Connection:   {event_hub_connection_name}")
    
    print(f"\n☁️ AZURE URLS:")
    print(f"   ⚡ Capacity:     {capacity_url}")
    print(f"   📡 Event Hub:    {eventhub_namespace_url}")
    
    print(f"\n📦 FABRIC URLS:")
    print(f"   🏠 Workspace:    {workspace_url}")
    print(f"   🌍 Environment:  {environment_url}")
    print(f"   🤖 Data Agent:   {data_agent_url}")
    print(f"   🏛️ Eventhouse:   {eventhouse_url}")
    print(f"   🗄️ Database:     {kql_database_url}")
    print(f"   📊 Dashboard:    {dashboard_url}")
    print(f"   🌊 Eventstream:  {eventstream_url}")
    print(f"   🚨 Activator:    {activator_url}")
    print(f"   🔗 Connections:  {eventhub_connection_url}")
    
    print(f"\n✨ Your real-time intelligence solution is ready!")
    print(f"="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n⚠️ Pipeline interrupted by user")
        sys.exit(1)
    except UnicodeEncodeError as e:
        print(f"\n[ERROR] Unicode encoding error detected:")
        print(f"Your console doesn't support the Unicode characters used in this script.")
        print(f"This is common on Windows systems with certain console configurations.")
        print(f"\nSolutions:")
        print(f"1. Run the script in Windows Terminal or VS Code terminal")
        print(f"2. Use PowerShell 7+ instead of Windows PowerShell")
        print(f"3. Set environment variable: set PYTHONIOENCODING=utf-8")
        print(f"4. Use command: chcp 65001 (to set UTF-8 codepage)")
        print(f"\nTechnical details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)

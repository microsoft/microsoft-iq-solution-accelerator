#!/usr/bin/env python3
"""
Microsoft IQ Solution Installer

This script provides the deployment entry-point for the Microsoft IQ solution.
It performs the following steps to bootstrap the solution:

    1. setup_knowledge_base   - Create Azure AI Search index, upload documents,
                                create Foundry IQ Knowledge Source and Knowledge Base
                                (skipped gracefully if Foundry env vars are not set)
    2. setup_agent            - Create AI Foundry agent with Knowledge Base MCP tool
                                (skipped gracefully if AZURE_AI_AGENT_ENDPOINT is not set)
    3. setup_workspace        - Create and configure the Fabric workspace/capacity
    4. setup_administrators   - Add workspace administrators
    5. upload_installer       - Upload the installer notebook to the workspace
    6. run_installer          - Execute the installer notebook end-to-end

The installer notebook (fabric_solution_installer.ipynb) handles the remaining
solution-specific steps (lakehouse creation, data ingestion, notebook deployment,
post-deployment tasks, …) once it has been uploaded and started.

Usage:
    python install_microsoft_iq_solution.py

Environment Variables:
    The following variables are automatically set by 'azd' from main.bicep outputs and
    must be present in the environment before running this script:

    AZURE_FABRIC_CAPACITY_NAME           (required) Name of the Fabric capacity resource.
                                                    Sourced from main.bicep output:
                                                    AZURE_FABRIC_CAPACITY_NAME.
    SOLUTION_SUFFIX                      (required) Suffix used for resource naming.
                                                    Sourced from main.bicep output:
                                                    SOLUTION_SUFFIX.
    AZURE_FABRIC_CAPACITY_ADMINISTRATORS (required) JSON array of capacity administrator
                                                    identities. Sourced from main.bicep
                                                    output: AZURE_FABRIC_CAPACITY_ADMINISTRATORS.

    The following variables are optional and must be set manually if needed:

    FABRIC_WORKSPACE_NAME                (optional) Override the default workspace name
                                                    (defaults to "<SOLUTION_NAME> - <SOLUTION_SUFFIX>").
    FABRIC_WORKSPACE_ADMINISTRATORS      (optional) Comma-separated list of additional
                                                    workspace administrator identities.
    GITHUB_TOKEN                         (optional) GitHub personal access token. When set,
                                                    the installer notebook is patched to
                                                    include the token for private repo access.

    The following variables enable the setup_knowledge_base step (all three required):

    AZURE_AI_SEARCH_ENDPOINT             (optional) Azure AI Search service endpoint URL.
    AZURE_STORAGE_BLOB_ENDPOINT          (optional) Azure Blob Storage service endpoint URL.
    AZURE_AI_ENDPOINT                    (optional) Azure AI Services / OpenAI endpoint URL.
                                                    Falls back to AZURE_AI_AGENT_ENDPOINT.
    AZURE_OPENAI_EMBEDDING_MODEL         (optional) Embedding model deployment name.
                                                    Defaults to text-embedding-3-small.
    AZURE_CHAT_MODEL                     (optional) Chat model deployment name.
                                                    Defaults to gpt-4o-mini.
    AZURE_AI_SEARCH_INDEX                (optional) Search index name.
                                                    Defaults to <SOLUTION_SUFFIX>-documents.

    The following variables enable the setup_agent step:

    AZURE_AI_AGENT_ENDPOINT              (optional) Azure AI Project endpoint URL.
                                                    Required to enable the step.
    AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME (optional) Chat model deployment name for the agent.
                                                    Falls back to AZURE_CHAT_MODEL, then gpt-4.1-mini.
    AI_SERVICE_NAME                      (optional) Azure AI Services account name.
                                                    Required for MCP connection creation.
    AZURE_AI_PROJECT_NAME                (optional) Azure AI Project name.
                                                    Required for MCP connection creation.
    KB_MCP_CONNECTION_NAME               (optional) Project connection name for the Knowledge Base MCP tool.
                                                    Defaults to <SOLUTION_SUFFIX>-kb-mcp-connection.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import NoReturn

# Add infra/scripts/ to path so the fabric package and its modules can be imported
sys.path.append(os.path.dirname(__file__))

from fabric.helpers.logging_config import setup_logging

# Configure logging before any other imports so that library modules
# (fabric_api, graph_api, helpers.*) inherit the root logger's settings.
# The log level can be set via ``azd env set LOG_LEVEL DEBUG``.
setup_logging()

# Module-level logger for this entry-point script.  All log calls below
# use this logger; the level and handler are inherited from setup_logging().
logger = logging.getLogger(__name__)

from fabric.fabric_api import FabricApiError, create_fabric_client, create_workspace_fabric_client
from fabric.graph_api import create_graph_client
from fabric.helpers.config import SOLUTION_NAME, default_workspace_name
from fabric.helpers.utils import (
    INSTALLER_NOTEBOOK_NAME,
    get_notebook_path,
    run_installer_notebook,
    upload_installer_notebook,
    get_required_env_var,
    parse_workspace_administrators,
    print_step,
    print_steps_summary,
)
from fabric.helpers.workspace import setup_workspace
from fabric.helpers.workspace_admins import setup_workspace_administrators
from foundry.agent_api import (
    CHAT_AGENT_NAME,
    build_agent_instructions,
    create_agent_client,
    create_kb_mcp_connection,
    create_or_update_agent,
)
from foundry.blob_api import create_blob_service_client, upload_pdf_to_blob
from foundry.helpers.config import DATA_DIR as FOUNDRY_DATA_DIR
from foundry.helpers.pdf_utils import process_pdfs_to_documents
from foundry.search_api import (
    create_or_update_knowledge_base,
    create_or_update_knowledge_source,
    create_or_update_search_index,
    create_search_client,
    create_search_index_client,
    upload_documents_to_search,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALL_DEPLOYMENT_STEPS = [
    "setup_knowledge_base",
    "setup_agent",
    "setup_workspace",
    "setup_administrators",
    "upload_installer",
    "run_installer",
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the minimal three-step solution installation."""

    # ------------------------------------------------------------------
    # Configuration from environment variables
    # ------------------------------------------------------------------
    capacity_name = get_required_env_var("AZURE_FABRIC_CAPACITY_NAME")
    subscription_id = get_required_env_var("AZURE_SUBSCRIPTION_ID")
    resource_group = get_required_env_var("AZURE_RESOURCE_GROUP")
    solution_suffix = get_required_env_var("SOLUTION_SUFFIX")
    workspace_name = os.getenv(
        "FABRIC_WORKSPACE_NAME", default_workspace_name(solution_suffix)
    )
    workspace_administrators = parse_workspace_administrators(
        get_required_env_var("AZURE_FABRIC_CAPACITY_ADMINISTRATORS"),
        os.getenv("FABRIC_WORKSPACE_ADMINISTRATORS"),
    )
    github_token = os.getenv("GITHUB_TOKEN")

    notebook_path = get_notebook_path()

    # Foundry / AI Search configuration (optional — steps skipped if not set)
    search_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
    blob_endpoint = os.getenv("AZURE_STORAGE_BLOB_ENDPOINT")
    ai_endpoint = (
        os.getenv("AZURE_AI_ENDPOINT")
        or os.getenv("AZURE_AI_AGENT_ENDPOINT", "").split("/api/projects")[0]
    )
    embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model = os.getenv("AZURE_CHAT_MODEL", "gpt-4o-mini")
    search_index_name = os.getenv("AZURE_AI_SEARCH_INDEX", f"{solution_suffix}-documents")
    blob_container_name = f"{solution_suffix}-documents"
    knowledge_base_name = f"{solution_suffix}-kb"
    knowledge_source_name = f"{solution_suffix}-ks"
    foundry_configured = bool(search_endpoint and blob_endpoint and ai_endpoint)

    # Agent configuration (optional — step skipped if not set)
    agent_endpoint = os.getenv("AZURE_AI_AGENT_ENDPOINT")
    agent_model = (
        os.getenv("AZURE_CHAT_MODEL")
        or os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")
    )
    ai_service_name = os.getenv("AI_SERVICE_NAME") or os.getenv("AZURE_OPENAI_RESOURCE")
    ai_project_name = os.getenv("AZURE_AI_PROJECT_NAME")
    kb_mcp_connection_name = os.getenv("KB_MCP_CONNECTION_NAME", f"{solution_suffix}-kb-mcp-connection")
    agent_configured = bool(agent_endpoint and search_endpoint)

    # ------------------------------------------------------------------
    # Startup banner
    # ------------------------------------------------------------------
    logger.info(f"🏭 {SOLUTION_NAME} – Solution Installer")
    logger.info("=" * 60)
    logger.info(f"Capacity:          {capacity_name}")
    logger.info(f"Subscription:      {subscription_id}")
    logger.info(f"Resource Group:    {resource_group}")
    logger.info(f"Workspace:         {workspace_name}")
    logger.info(f"Solution Suffix:   {solution_suffix}")
    logger.info(f"Installer Notebook: {notebook_path}")
    logger.info(f"GitHub Token:      {'***' if github_token else 'Not set'}")
    if workspace_administrators:
        logger.info(f"Administrators:    {', '.join(workspace_administrators)}")
    logger.info(f"Search Endpoint:   {search_endpoint or 'Not configured (step will be skipped)'}")
    if foundry_configured:
        logger.info(f"Search Index:      {search_index_name}")
        logger.info(f"Knowledge Base:    {knowledge_base_name}")
    logger.info(f"Agent Endpoint:    {agent_endpoint or 'Not configured (step will be skipped)'}")
    if agent_configured:
        logger.info(f"Agent Model:       {agent_model}")
        logger.info(f"KB MCP Connection: {kb_mcp_connection_name}")
    logger.info(f"Start time:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Authenticate API clients
    # ------------------------------------------------------------------
    logger.info("\n🔐 Authenticating clients…")
    try:
        fabric_client = create_fabric_client()
        logger.info("   Fabric API client authenticated")
    except Exception as exc:
        logger.error(f"Failed to authenticate Fabric API client: {exc}")
        sys.exit(1)

    try:
        graph_client = create_graph_client()
        logger.info("   Graph API client authenticated")
    except Exception as exc:
        logger.error(f"Failed to authenticate Graph API client: {exc}")
        sys.exit(1)

    executed_steps: list = []
    failed_steps: list = []

    def _abort(step_name: str, error: Exception) -> NoReturn:
        """Record the failure, log a summary, and exit."""
        logger.error(f"Exception while executing {step_name}: {error}")
        failed_steps.append({"step": step_name, "error": str(error)})
        completed = {s for s in executed_steps} | {s["step"] for s in failed_steps}
        uncompleted = [s for s in ALL_DEPLOYMENT_STEPS if s not in completed]
        print_steps_summary(SOLUTION_NAME, solution_suffix, executed_steps, failed_steps, uncompleted)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 1 – Set up AI Search knowledge base (Foundry IQ)
    # ------------------------------------------------------------------
    print_step(1, 6, "Setting up AI Search knowledge base and Foundry IQ",
               search_endpoint=search_endpoint or "Not configured",
               index=search_index_name,
               knowledge_base=knowledge_base_name)
    if not foundry_configured:
        logger.warning(
            "   Skipping setup_knowledge_base: AZURE_AI_SEARCH_ENDPOINT, "
            "AZURE_STORAGE_BLOB_ENDPOINT, and AZURE_AI_ENDPOINT must all be set"
        )
        executed_steps.append("setup_knowledge_base (skipped)")
    else:
        try:
            assert search_endpoint and blob_endpoint and ai_endpoint  # guaranteed by foundry_configured

            # Locate PDFs
            data_path = Path(FOUNDRY_DATA_DIR)
            docs_dir = data_path / "documents" if (data_path / "documents").exists() else data_path
            pdf_files = list(docs_dir.glob("*.pdf"))
            if not pdf_files:
                logger.warning(f"   No PDF files found in {docs_dir} — knowledge base will be empty")
            else:
                logger.info(f"   Found {len(pdf_files)} PDF file(s)")

            # Create Azure clients
            logger.info("   Initialising Azure clients…")
            _index_client = create_search_index_client(search_endpoint)
            _search_client = create_search_client(search_endpoint, search_index_name)
            _blob_client = create_blob_service_client(blob_endpoint)

            # Create / update search index
            logger.info("   Creating search index…")
            create_or_update_search_index(_index_client, search_index_name, embedding_model, ai_endpoint)

            # Upload PDFs and index document chunks
            pdf_blob_urls: dict = {}
            documents: list = []
            if pdf_files:
                logger.info(f"   Uploading {len(pdf_files)} PDF(s) to blob storage…")
                for _pdf_path in pdf_files:
                    _url = upload_pdf_to_blob(_blob_client, blob_endpoint, blob_container_name, _pdf_path)
                    pdf_blob_urls[_pdf_path.name] = _url

                logger.info("   Processing and indexing document chunks…")
                documents = process_pdfs_to_documents(pdf_files, pdf_blob_urls)
                if documents:
                    upload_documents_to_search(_search_client, documents)

            # Create Knowledge Source
            logger.info("   Creating knowledge source…")
            try:
                create_or_update_knowledge_source(
                    _index_client, knowledge_source_name, search_index_name, SOLUTION_NAME
                )
            except Exception as _exc:
                logger.warning(f"   Could not create knowledge source: {_exc}")

            # Create Knowledge Base
            logger.info("   Creating knowledge base…")
            try:
                create_or_update_knowledge_base(
                    _index_client, knowledge_base_name, knowledge_source_name,
                    SOLUTION_NAME, ai_endpoint, chat_model
                )
            except Exception as _exc:
                logger.warning(f"   Could not create knowledge base: {_exc}")

            logger.info("Successfully completed: setup_knowledge_base")
            executed_steps.append("setup_knowledge_base")
        except Exception as exc:
            _abort("setup_knowledge_base", exc)

    # ------------------------------------------------------------------
    # Step 2 – Create AI Foundry agent (Knowledge Base MCP tool)
    # ------------------------------------------------------------------
    print_step(2, 6, "Creating AI Foundry agent with Knowledge Base MCP tool",
               agent_endpoint=agent_endpoint or "Not configured",
               knowledge_base=knowledge_base_name,
               connection=kb_mcp_connection_name)
    if not agent_configured:
        logger.warning(
            "   Skipping setup_agent: AZURE_AI_AGENT_ENDPOINT and "
            "AZURE_AI_SEARCH_ENDPOINT must both be set"
        )
        executed_steps.append("setup_agent (skipped)")
    else:
        try:
            assert agent_endpoint and search_endpoint  # guaranteed by agent_configured

            # Load scenario info from ontology config if available
            _data_path = Path(FOUNDRY_DATA_DIR)
            _config_dir = _data_path / "config" if (_data_path / "config").exists() else _data_path
            _ontology_path = _config_dir / "ontology_config.json"
            _scenario_name = SOLUTION_NAME
            _scenario_desc = ""
            if _ontology_path.exists():
                import json as _json
                with open(_ontology_path) as _f:
                    _ontology = _json.load(_f)
                _scenario_name = _ontology.get("name", SOLUTION_NAME)
                _scenario_desc = _ontology.get("description", "")
                logger.debug(f"      Loaded ontology config: {_scenario_name}")
            else:
                logger.debug("      No ontology_config.json found — using default scenario name")

            # Load KB name from previous step's output if available
            _search_ids_path = _config_dir / "search_ids.json"
            _kb_name = knowledge_base_name
            if _search_ids_path.exists():
                import json as _json2
                with open(_search_ids_path) as _f2:
                    _search_ids = _json2.load(_f2)
                _kb_name = _search_ids.get("knowledge_base_name", knowledge_base_name)

            # Build agent instructions
            _instructions = build_agent_instructions(_scenario_name, _scenario_desc)
            logger.debug(f"      Built instructions ({len(_instructions)} chars)")

            # Create agent client and MCP connection
            logger.info("   Initialising AI Project client…")
            _agent_client = create_agent_client(agent_endpoint)

            logger.info("   Creating KB MCP project connection…")
            _mcp_ep = (
                f"{search_endpoint.rstrip('/')}/knowledgebases/{_kb_name}"
                f"/mcp?api-version=2025-11-01-preview"
            )
            if ai_service_name and ai_project_name:
                _connected = create_kb_mcp_connection(
                    search_endpoint=search_endpoint,
                    kb_name=_kb_name,
                    connection_name=kb_mcp_connection_name,
                    subscription_id=subscription_id,
                    resource_group=resource_group,
                    ai_service_name=ai_service_name,
                    project_name=ai_project_name,
                )
                if not _connected:
                    logger.warning(
                        "   MCP connection creation may have failed — "
                        "create it manually in the Foundry portal if needed"
                    )
            else:
                logger.warning(
                    "   Skipping MCP connection: AI_SERVICE_NAME and "
                    "AZURE_AI_PROJECT_NAME must both be set"
                )

            # Create / replace agent
            logger.info(f"   Creating agent '{CHAT_AGENT_NAME}'…")
            with _agent_client:
                _agent = create_or_update_agent(
                    project_client=_agent_client,
                    agent_name=CHAT_AGENT_NAME,
                    model=agent_model,
                    instructions=_instructions,
                    mcp_endpoint=_mcp_ep,
                    connection_name=kb_mcp_connection_name,
                )
            logger.info(f"   Agent '{_agent.name}' ready (id: {_agent.id})")

            # Persist agent metadata for downstream scripts
            _agent_ids_path = _config_dir / "agent_ids.json"
            _agent_ids: dict = {}
            if _agent_ids_path.exists():
                import json as _json3
                with open(_agent_ids_path) as _f3:
                    _agent_ids = _json3.load(_f3)
            _agent_ids.update({
                "chat_agent_id": _agent.id,
                "chat_agent_name": _agent.name,
                "search_index": search_index_name,
                "knowledge_base_name": _kb_name,
                "mcp_connection_name": kb_mcp_connection_name,
                "search_endpoint": search_endpoint,
                "tools": ["knowledge_base_retrieve"],
            })
            import json as _json4
            with open(_agent_ids_path, "w") as _f4:
                _json4.dump(_agent_ids, _f4, indent=2)
            logger.debug(f"      Agent config saved to {_agent_ids_path}")

            logger.info("Successfully completed: setup_agent")
            executed_steps.append("setup_agent")
        except Exception as exc:
            _abort("setup_agent", exc)

    # ------------------------------------------------------------------
    # Step 3 – Set up Fabric workspace
    # ------------------------------------------------------------------
    print_step(3, 6, "Setting up Fabric workspace and capacity assignment",
               capacity_name=capacity_name, workspace_name=workspace_name)
    try:
        workspace_id = setup_workspace(
            fabric_client=fabric_client,
            capacity_name=capacity_name,
            workspace_name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group,
        )
        logger.info("Successfully completed: setup_workspace")
        executed_steps.append("setup_workspace")
    except Exception as exc:
        _abort("setup_workspace", exc)

    # Workspace-scoped client required for all subsequent steps
    logger.info("\nCreating workspace-scoped Fabric API client…")
    try:
        workspace_client = create_workspace_fabric_client(workspace_id)
        logger.info("   Workspace client authenticated")
    except Exception as exc:
        _abort("create_workspace_client", exc)

    # ------------------------------------------------------------------
    # Step 4 – Configure workspace administrators
    # ------------------------------------------------------------------
    admin_display = ", ".join(workspace_administrators) if workspace_administrators else "None"
    print_step(4, 6, "Configuring workspace administrators",
               workspace_id=workspace_id, administrators=admin_display)
    try:
        setup_workspace_administrators(
            workspace_client=workspace_client,
            fabric_admins=workspace_administrators or [],
            graph_client=graph_client,
        )
        logger.info("Successfully completed: setup_administrators")
        executed_steps.append("setup_administrators")
    except Exception as exc:
        _abort("setup_administrators", exc)

    # ------------------------------------------------------------------
    # Step 5 – Upload installer notebook
    # ------------------------------------------------------------------
    print_step(5, 6, "Uploading installer notebook",
               notebook=INSTALLER_NOTEBOOK_NAME)
    try:
        notebook_id = upload_installer_notebook(workspace_client, notebook_path, github_token=github_token)
        logger.info("Successfully completed: upload_installer")
        executed_steps.append("upload_installer")
    except Exception as exc:
        _abort("upload_installer", exc)

    # ------------------------------------------------------------------
    # Step 6 – Run installer notebook
    # ------------------------------------------------------------------
    print_step(6, 6, "Running installer notebook",
               notebook_id=notebook_id)
    try:
        run_installer_notebook(workspace_client, notebook_id)
        logger.info("Successfully completed: run_installer")
        executed_steps.append("run_installer")
    except Exception as exc:
        _abort("run_installer", exc)

    # ------------------------------------------------------------------
    # Success summary
    # ------------------------------------------------------------------
    workspace_url = (
        f"https://app.fabric.microsoft.com/groups/{workspace_id}?experience=fabric-developer"
    )

    print_steps_summary(SOLUTION_NAME, solution_suffix, executed_steps, failed_steps, [])

    logger.info(f"\n{'='*60}")
    logger.info(f"🎉 {SOLUTION_NAME.upper()} INSTALLATION COMPLETE!")
    logger.info(f"{'='*60}")
    logger.info(f"Completed:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Suffix:     {solution_suffix}")
    logger.info(f"Workspace:  {workspace_name}")
    logger.info(f"URL:        {workspace_url}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\nInstallation interrupted by user")
        sys.exit(1)
    except Exception as exc:
        logger.error(f"\n\nUnexpected error: {exc}")
        sys.exit(1)

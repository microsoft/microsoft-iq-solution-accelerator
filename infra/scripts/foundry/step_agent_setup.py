#!/usr/bin/env python3
"""
AI Foundry agent setup step for the Microsoft IQ deployment.

Extracts step 2 (``setup_agent``) of the deployment flow into a single
top-level function callable from the entry-point script.
"""

import json
import logging
from pathlib import Path

from common.config import DATA_DIR
from foundry.agent_api import (
    CHAT_AGENT_NAME,
    build_agent_instructions,
    create_agent_client,
    create_kb_mcp_connection,
    create_or_update_agent,
)

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.
logger = logging.getLogger(__name__)


def setup_agent(
    *,
    solution_name: str,
    agent_endpoint: str,
    agent_model: str,
    search_endpoint: str,
    search_index_name: str,
    knowledge_base_name: str,
    kb_mcp_connection_name: str,
    subscription_id: str,
    resource_group: str,
    ai_service_name: str | None,
    ai_project_name: str | None,
) -> None:
    """Create or update an AI Foundry agent wired up to the Knowledge Base MCP tool.

    Args:
        solution_name: Default scenario name when ``ontology_config.json`` is absent.
        agent_endpoint: Azure AI Project endpoint URL.
        agent_model: Chat model deployment name for the agent.
        search_endpoint: Azure AI Search service endpoint URL.
        search_index_name: Name of the search index that backs the KB.
        knowledge_base_name: Default KB name (overridden by ``search_ids.json`` if present).
        kb_mcp_connection_name: Project connection name for the KB MCP tool.
        subscription_id: Azure subscription ID.
        resource_group: Azure resource group name.
        ai_service_name: Azure AI Services account name (required for MCP connection).
        ai_project_name: Azure AI Project name (required for MCP connection).
    """
    # Load scenario info from ontology config if available
    _data_path = Path(DATA_DIR)
    _config_dir = _data_path / "config" if (_data_path / "config").exists() else _data_path
    _ontology_path = _config_dir / "ontology_config.json"
    _scenario_name = solution_name
    _scenario_desc = ""
    if _ontology_path.exists():
        with open(_ontology_path) as _f:
            _ontology = json.load(_f)
        _scenario_name = _ontology.get("name", solution_name)
        _scenario_desc = _ontology.get("description", "")
        logger.debug(f"      Loaded ontology config: {_scenario_name}")
    else:
        logger.debug("      No ontology_config.json found — using default scenario name")

    # Load KB name from previous step's output if available
    _search_ids_path = _config_dir / "search_ids.json"
    _kb_name = knowledge_base_name
    if _search_ids_path.exists():
        with open(_search_ids_path) as _f2:
            _search_ids = json.load(_f2)
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
        with open(_agent_ids_path) as _f3:
            _agent_ids = json.load(_f3)
    _agent_ids.update({
        "chat_agent_id": _agent.id,
        "chat_agent_name": _agent.name,
        "search_index": search_index_name,
        "knowledge_base_name": _kb_name,
        "mcp_connection_name": kb_mcp_connection_name,
        "search_endpoint": search_endpoint,
        "tools": ["knowledge_base_retrieve"],
    })
    with open(_agent_ids_path, "w") as _f4:
        json.dump(_agent_ids, _f4, indent=2)
    logger.debug(f"      Agent config saved to {_agent_ids_path}")

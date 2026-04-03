"""
Load environment variables from azd deployment and project .env file.

This module provides a unified way to load configuration:
1. Azure service settings from azd environment (.azure/<env>/.env)
2. Project-specific settings from project root .env (Fabric, industry, etc.)

Azure services (from azd):
    - AZURE_AI_AGENT_ENDPOINT
    - AZURE_AI_ENDPOINT  
    - AZURE_OPENAI_ENDPOINT
    - AZURE_AI_SEARCH_ENDPOINT
    - AZURE_STORAGE_BLOB_ENDPOINT
    - AZURE_CHAT_MODEL
    - AZURE_EMBEDDING_MODEL
    - etc.

Project settings (from .env):
    - FABRIC_WORKSPACE_ID
    - SOLUTION_NAME
    - INDUSTRY
    - USECASE
    - DATA_SIZE
    - DATA_FOLDER
    - FOUNDRY_AGENT_ID
    - etc.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


def load_azd_env():
    """
    Load environment variables from azd deployment.
    
    Reads from .azure/<defaultEnvironment>/.env
    Returns True if azd env was found and loaded.
    """
    script_dir = Path(__file__).parent
    azure_dir = script_dir.parent / ".azure"
    
    # Get environment name from config.json or AZURE_ENV_NAME
    env_name = os.environ.get("AZURE_ENV_NAME", "")
    
    if not env_name and (azure_dir / "config.json").exists():
        with open(azure_dir / "config.json") as f:
            config = json.load(f)
            env_name = config.get("defaultEnvironment", "")
    
    if not env_name:
        return False
    
    env_file = azure_dir / env_name / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        return True
    
    return False


def load_project_env():
    """
    Load environment variables from project .env file.
    
    Reads from project root .env file (same directory as azure.yaml)
    Returns True if .env was found and loaded.
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        load_dotenv(env_file, override=False)  # Don't override azd settings
        return True
    
    return False


def load_all_env():
    """Load both azd and project environment variables."""
    azd_loaded = load_azd_env()
    project_loaded = load_project_env()
    
    # Set defaults if not provided
    if not os.getenv("SOLUTION_NAME"):
        os.environ["SOLUTION_NAME"] = os.getenv("AZURE_ENV_NAME", "demo")
    
    return azd_loaded, project_loaded


def get_required_env(var_name, description=None):
    """Get required environment variable or exit with error."""
    value = os.getenv(var_name)
    if not value:
        desc = f" ({description})" if description else ""
        print(f"ERROR: {var_name} environment variable not set{desc}")
        print(f"       Make sure azd deployment completed successfully")
        exit(1)
    return value


def get_data_folder():
    """Get data folder path with proper validation."""
    data_folder = os.getenv("DATA_FOLDER")
    if not data_folder:
        raise ValueError("DATA_FOLDER environment variable not set")
    
    # Convert to absolute path if relative
    if not os.path.isabs(data_folder):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        data_folder = str(project_root / data_folder)
    
    return data_folder


def print_env_status():
    """Print current environment status for debugging."""
    print(f"Environment Status:")
    print(f"  AZURE_ENV_NAME: {os.getenv('AZURE_ENV_NAME', 'Not set')}")
    print(f"  SOLUTION_NAME: {os.getenv('SOLUTION_NAME', 'Not set')}")
    print(f"  AZURE_AI_AGENT_ENDPOINT: {os.getenv('AZURE_AI_AGENT_ENDPOINT', 'Not set')}")
    print(f"  AZURE_AI_SEARCH_ENDPOINT: {os.getenv('AZURE_AI_SEARCH_ENDPOINT', 'Not set')}")
    print(f"  AZURE_STORAGE_BLOB_ENDPOINT: {os.getenv('AZURE_STORAGE_BLOB_ENDPOINT', 'Not set')}")
    print(f"  DATA_FOLDER: {os.getenv('DATA_FOLDER', 'Not set')}")


if __name__ == "__main__":
    load_all_env()
    print_env_status()
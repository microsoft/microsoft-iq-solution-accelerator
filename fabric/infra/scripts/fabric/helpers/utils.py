#!/usr/bin/env python3
"""
Common Utility Functions

This module provides common utility functions used across the Unified Data Foundation deployment scripts.
"""

import base64
import os
import sys
import json
from typing import Optional


def read_file_content(file_path: str) -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file to read
        
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
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")


def get_required_env_var(var_name: str) -> str:
    """
    Get required environment variable or exit with error.
    
    Args:
        var_name: Name of the environment variable
        
    Returns:
        Value of the environment variable
        
    Raises:
        SystemExit: If environment variable is not set
    """
    value = os.getenv(var_name)
    if not value:
        print(f"❌ Error: Required environment variable '{var_name}' is not set")
        print(f"   Please ensure the variable is set before running this script.")
        sys.exit(1)
    return value


def encode_notebook(notebook_path: str) -> str:
    """
    Read a ``.ipynb`` file and return its content as a Base64 string.

    Args:
        notebook_path: Absolute path to the notebook file.

    Returns:
        Base64-encoded notebook content (UTF-8).

    Raises:
        FileNotFoundError: If the notebook file does not exist.
        ValueError: If the file is not valid JSON.
    """
    content = read_file_content(notebook_path)  # raises FileNotFoundError if missing
    notebook_json = json.loads(content)         # validate JSON before encoding
    raw_bytes = json.dumps(notebook_json).encode("utf-8")
    return base64.b64encode(raw_bytes).decode("utf-8")


def parse_workspace_administrators(
    capacity_administrators_json: Optional[str],
    fabric_workspace_admins: Optional[str],
) -> Optional[list]:
    """
    Combine administrator identities from environment variable values.

    Args:
        capacity_administrators_json: JSON-array string from
            ``AZURE_FABRIC_CAPACITY_ADMINISTRATORS``.
        fabric_workspace_admins: Comma-separated string from
            ``FABRIC_WORKSPACE_ADMINISTRATORS``.

    Returns:
        List of administrator identity strings, or ``None`` if the list is empty.
    """
    administrators: list = []

    if capacity_administrators_json:
        try:
            administrators.extend(json.loads(capacity_administrators_json))
        except json.JSONDecodeError:
            print("⚠️  Warning: AZURE_FABRIC_CAPACITY_ADMINISTRATORS is not valid JSON – ignoring")

    if fabric_workspace_admins:
        administrators.extend(
            admin.strip()
            for admin in fabric_workspace_admins.split(",")
            if admin.strip()
        )

    return administrators if administrators else None


def print_step(step_number: int, total_steps: int, step_name: str, **kwargs):
    """
    Print a formatted step header with details.
    
    Args:
        step_number: Current step number
        total_steps: Total number of steps
        step_name: Name of the step
        **kwargs: Additional key-value pairs to display
    """
    print(f"\n{'='*60}")
    print(f"📋 Step {step_number}/{total_steps}: {step_name}")
    print(f"{'='*60}")
    
    # Print additional details if provided
    if kwargs:
        for key, value in kwargs.items():
            formatted_key = key.replace('_', ' ').title()
            print(f"   {formatted_key}: {value}")


def print_steps_summary(solution_name: str, solution_suffix: str, executed_steps: list, failed_steps: list = None, uncompleted_steps: list = None):
    """
    Print a summary of executed, failed, and uncompleted steps.
    
    Args:
        solution_name: Name of the solution being deployed
        solution_suffix: Solution suffix identifier
        executed_steps: List of successfully executed step names
        failed_steps: Optional list of failed step names
        uncompleted_steps: Optional list of steps that were not reached
    """
    print(f"\n{'='*60}")
    print(f"📊 {solution_name} Deployment Summary")
    print(f"{'='*60}")
    print(f"Solution Suffix: {solution_suffix}")
    print(f"\n✅ Successfully Completed Steps ({len(executed_steps)}):")
    for i, step in enumerate(executed_steps, 1):
        print(f"   {i}. {step}")
    
    if failed_steps:
        print(f"\n❌ Failed Steps ({len(failed_steps)}):")
        for i, step_info in enumerate(failed_steps, 1):
            if isinstance(step_info, dict):
                step_name = step_info.get('step', 'Unknown step')
                error_msg = step_info.get('error', 'No error details')
                print(f"   {i}. {step_name}")
                print(f"      Error: {error_msg}")
            else:
                print(f"   {i}. {step_info}")
    
    if uncompleted_steps:
        print(f"\n⏭️  Uncompleted Steps ({len(uncompleted_steps)}):")
        for i, step in enumerate(uncompleted_steps, 1):
            print(f"   {i}. {step}")
    
    print(f"{'='*60}")

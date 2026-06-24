#!/usr/bin/env python3
"""
Common Utilities Module

This module provides common utility functions for Fabric operations.

Usage:
    python fabric_common_utils.py --test-env-var AZURE_ENV_NAME

Requirements:
    - Environment variables for testing
"""

import os
import sys
from datetime import datetime

def get_required_env_var(var_name: str) -> str:
    """Get a required environment variable or exit with error.
    
    Args:
        var_name: Name of the environment variable to retrieve
        
    Returns:
        Value of the environment variable
        
    Raises:
        SystemExit: If the environment variable is not set
    """
    value = os.getenv(var_name)
    if not value:
        print(f"❌ Missing environment variable: {var_name}")
        sys.exit(1)
    return value

def print_step(step_num: int = None, total_steps: int = None, description: str = None, **kwargs):
    """
    Print operation step information.
    
    Args:
        step_num: Optional current step number
        total_steps: Optional total number of steps
        description: Optional description of what this step does
        **kwargs: Arguments for display purposes
    """
    if step_num is not None and total_steps is not None and description:
        print(f"\n📋 Step {step_num}/{total_steps}: {description}")
    elif description:
        print(f"\n📋 {description}")
    
    if kwargs:
        args_str = ", ".join([f"{k}={v}" for k, v in kwargs.items() if "key" not in k.lower()])
        print(f"   Parameters: {args_str}")

def print_steps_summary(solution_name: str = None, solution_suffix: str = None, executed_steps: list = None, failed_steps: list = None):
    """Print operation execution summary."""
    any_failures = bool(failed_steps)
    status_icon = "⚠️" if any_failures else "🎉"
    status_text = "COMPLETED WITH WARNINGS" if any_failures else "COMPLETED SUCCESSFULLY"
    
    print(f"\n" + "="*60)
    if solution_name:
        print(f"{status_icon} {solution_name.upper()} {status_text}!")
    else:
        print(f"{status_icon} OPERATION {status_text}!")
    print(f"="*60)
    print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if solution_suffix:
        print(f"🏷️  Solution: {solution_suffix}")
    
    if executed_steps:
        print(f"\n✅ SUCCESSFULLY EXECUTED:")
        for step in executed_steps:
            print(f"   ✓ {step}")
    
    if failed_steps:
        print(f"\n❌ FAILED STEPS:")
        for step in failed_steps:
            print(f"   ⚠️ {step}")
    
    if not any_failures and executed_steps:
        print(f"\n✨ All {len(executed_steps)} operations completed successfully!")
    elif any_failures:
        print(f"\n⚠️ Some operations failed. Check warnings above.")
        print(f"   Fix issues and re-run if needed.")
    print(f"="*60)
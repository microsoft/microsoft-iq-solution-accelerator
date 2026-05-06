#!/usr/bin/env python3
"""
Step header and summary formatters for the Microsoft IQ deployment scripts.
"""

import logging
from typing import Optional

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.  No handlers or levels are
# configured here; this follows the Python convention that library modules
# only acquire loggers and never configure them.
logger = logging.getLogger(__name__)


def print_step(step_number: int, total_steps: int, step_name: str, **kwargs):
    """
    Print a formatted step header with details.
    
    Args:
        step_number: Current step number
        total_steps: Total number of steps
        step_name: Name of the step
        **kwargs: Additional key-value pairs to display
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"📋 Step {step_number}/{total_steps}: {step_name}")
    logger.info(f"{'='*60}")
    
    # Log additional details if provided
    if kwargs:
        for key, value in kwargs.items():
            formatted_key = key.replace('_', ' ').title()
            logger.info(f"   {formatted_key}: {value}")


def print_steps_summary(solution_name: str, solution_suffix: str, executed_steps: list, failed_steps: Optional[list] = None, uncompleted_steps: Optional[list] = None):
    """
    Print a summary of executed, failed, and uncompleted steps.
    
    Args:
        solution_name: Name of the solution being deployed
        solution_suffix: Solution suffix identifier
        executed_steps: List of successfully executed step names
        failed_steps: Optional list of failed step names
        uncompleted_steps: Optional list of steps that were not reached
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 {solution_name} Deployment Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Solution Suffix: {solution_suffix}")
    logger.info(f"\n✅ Successfully Completed Steps ({len(executed_steps)}):")
    for i, step in enumerate(executed_steps, 1):
        logger.info(f"   {i}. {step}")
    
    if failed_steps:
        logger.info(f"\n❌ Failed Steps ({len(failed_steps)}):")
        for i, step_info in enumerate(failed_steps, 1):
            if isinstance(step_info, dict):
                step_name = step_info.get('step', 'Unknown step')
                error_msg = step_info.get('error', 'No error details')
                logger.info(f"   {i}. {step_name}")
                logger.info(f"      Error: {error_msg}")
            else:
                logger.info(f"   {i}. {step_info}")
    
    if uncompleted_steps:
        logger.info(f"\n⏭️  Uncompleted Steps ({len(uncompleted_steps)}):")
        for i, step in enumerate(uncompleted_steps, 1):
            logger.info(f"   {i}. {step}")
    
    logger.info(f"{'='*60}")

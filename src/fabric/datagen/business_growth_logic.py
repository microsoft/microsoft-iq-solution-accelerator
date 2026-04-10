"""
Business Growth & Market Event Logic
===================================

This module contains the logic for business growth patterns and market event simulation
to make sample data generation more realistic and representative of growing businesses.

Implements a three-phase smooth growth model with consolidation:
- Phase 1 (0-33%): Steady Initial Growth (1.0x → 1.8x, avg 1.4x)
- Phase 2 (33-35%): Consolidation Period (flat at 1.8x)  
- Phase 3 (35-100%): Sustained Growth (1.8x → 3.0x, avg 2.4x)

Market events include Black Friday, Christmas, Memorial Day, etc.
Customer tier amplification makes VIP/Partner customers more responsive to trends.
"""

from datetime import datetime, timedelta
from typing import Tuple
import calendar

def calculate_business_phase(current_date: datetime, start_date: datetime, end_date: datetime) -> Tuple[int, float]:
    """
    Calculate which business growth phase we're in and the growth multiplier.
    Uses the entire period as a scale of 100%, with each phase getting proportional days.
    
    Returns:
        Tuple[int, float]: (phase_number, growth_multiplier)
    """
    total_days = (end_date - start_date).days
    days_elapsed = (current_date - start_date).days
    
    # Calculate progress as percentage of total period (0.0 to 1.0)
    progress_percent = days_elapsed / total_days if total_days > 0 else 0.0
    
    # Define phase boundaries as percentages
    phase_1_end = 0.33  # 0% to 33%
    phase_2_end = 0.35  # 33% to 35% (brief consolidation)
    # phase_3_end = 1.0  # 35% to 100%
    
    if progress_percent <= phase_1_end:
        # Phase 1: Steady Initial Growth (0% → 33%)
        phase = 1
        phase_progress = progress_percent / phase_1_end  # 0.0 to 1.0 within this phase
        # Smooth growth from 1.0 to 1.8 (steady initial growth)
        multiplier = 1.0 + (phase_progress * 0.8)
        
    elif progress_percent <= phase_2_end:
        # Phase 2: Consolidation Period (33% → 35%) 
        phase = 2
        # Flat period at 1.8x for consolidation
        multiplier = 1.8
        
    else:
        # Phase 3: Sustained Growth (35% → 100%)
        phase = 3
        phase_progress = (progress_percent - phase_2_end) / (1.0 - phase_2_end)  # 0.0 to 1.0 within this phase
        # Continued growth from 1.8 to 3.0 (sustained growth)
        multiplier = 1.8 + (phase_progress * 1.2)
    
    return phase, multiplier

def get_market_event_multiplier(current_date: datetime) -> Tuple[str, float, float]:
    """
    Simple market events - minimal seasonal variation for smooth trends.
    
    Returns:
        Tuple[str, float, float]: (event_name, order_frequency_multiplier, order_size_multiplier)
    """
    # Keep it simple - just normal business operations
    return "Normal", 1.0, 1.0

def get_customer_tier_multiplier(customer_relationship_type: str, base_multiplier: float) -> float:
    """
    Apply tier-based multipliers to the base growth multiplier.
    Higher tiers benefit more from growth and suffer more from decline.
    
    Args:
        customer_relationship_type: The customer's relationship type
        base_multiplier: The base phase multiplier
        
    Returns:
        float: Adjusted multiplier for this customer tier
    """
    tier_amplifiers = {
        # Individual customers
        "standard": 1.0,    # Base tier, no amplification
        "premium": 1.3,     # 30% more responsive to changes
        "vip": 1.6,         # 60% more responsive
        
        # Business customers  
        "smb": 1.2,         # 20% more responsive
        "premier": 1.5,     # 50% more responsive
        "partner": 1.6,     # 60% more responsive (highest tier)
        
        # Government customers (less responsive)
        "federal": 0.8,     # 20% less responsive
        "state": 0.7,       # 30% less responsive  
        "local": 0.6        # 40% less responsive
    }
    
    tier_key = customer_relationship_type.lower()
    amplifier = tier_amplifiers.get(tier_key, 1.0)
    
    # Calculate the deviation from 1.0 and amplify it
    deviation = base_multiplier - 1.0
    amplified_deviation = deviation * amplifier
    
    # Ensure we don't go below 0.1 (minimum activity level)
    final_multiplier = max(1.0 + amplified_deviation, 0.1)
    
    return final_multiplier

def calculate_order_adjustments(current_date: datetime, start_date: datetime, end_date: datetime, 
                              customer_relationship_type: str) -> Tuple[float, float, str]:
    """
    Calculate the complete order frequency and size adjustments for a given date and customer.
    
    Returns:
        Tuple[float, float, str]: (frequency_multiplier, size_multiplier, debug_info)
    """
    # Get business phase
    phase, phase_multiplier = calculate_business_phase(current_date, start_date, end_date)
    
    # Get market event
    event_name, event_freq_mult, event_size_mult = get_market_event_multiplier(current_date)
    
    # Apply customer tier amplification
    tier_adjusted_multiplier = get_customer_tier_multiplier(customer_relationship_type, phase_multiplier)
    
    # Combine all multipliers
    final_freq_multiplier = tier_adjusted_multiplier * event_freq_mult
    final_size_multiplier = event_size_mult
    
    # Debug information
    debug_info = f"Phase{phase}({phase_multiplier:.2f}) × Tier({tier_adjusted_multiplier:.2f}) × {event_name}({event_freq_mult:.1f}×{event_size_mult:.1f})"
    
    return final_freq_multiplier, final_size_multiplier, debug_info
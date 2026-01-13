"""
Battery Utils
Battery status and health information.
"""

import psutil
from typing import Dict, Optional, Any


def get_battery_info() -> Optional[Dict[str, Any]]:
    """
    Get battery information.
    
    Returns:
        Dictionary with battery info, or None if no battery
    """
    battery = psutil.sensors_battery()
    
    if battery is None:
        return None
    
    # Determine status
    if battery.power_plugged:
        if battery.percent == 100:
            status = "Fully Charged"
        else:
            status = "Charging"
    else:
        status = "Discharging"
    
    # Calculate time remaining
    time_left = None
    if battery.secsleft > 0 and battery.secsleft != psutil.POWER_TIME_UNLIMITED:
        hours, remainder = divmod(battery.secsleft, 3600)
        minutes = remainder // 60
        time_left = f"{int(hours)}h {int(minutes)}m"
    elif battery.secsleft == psutil.POWER_TIME_UNLIMITED:
        time_left = "Calculating..."
    
    return {
        "percent": battery.percent,
        "power_plugged": battery.power_plugged,
        "status": status,
        "time_left": time_left,
        "seconds_left": battery.secsleft if battery.secsleft > 0 else None,
    }


def get_battery_health_estimate() -> Optional[Dict[str, Any]]:
    """
    Estimate battery health.
    
    Note: This is a rough estimate. Accurate health requires
    manufacturer-specific tools.
    
    Returns:
        Dictionary with health estimate
    """
    battery = psutil.sensors_battery()
    
    if battery is None:
        return None
    
    # Basic health indicators
    health = {
        "current_percent": battery.percent,
        "is_charging": battery.power_plugged,
    }
    
    # Simple health assessment based on behavior
    # This is a placeholder - real health requires battery wear level data
    if battery.percent >= 95 and not battery.power_plugged:
        health["status"] = "Good"
        health["health_percent"] = 100
    else:
        health["status"] = "Unknown"
        health["health_percent"] = None
        health["note"] = "Accurate health data requires manufacturer tools"
    
    return health


def format_time_remaining(seconds: int) -> str:
    """Format seconds to human-readable time."""
    if seconds <= 0:
        return "Unknown"
    
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m"
    else:
        return f"{int(minutes)}m"


def has_battery() -> bool:
    """Check if system has a battery."""
    return psutil.sensors_battery() is not None

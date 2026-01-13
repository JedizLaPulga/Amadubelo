"""
System Info
Get hardware and OS information.
"""

import platform
import psutil
from datetime import datetime
from typing import Dict, Any


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information."""
    
    # OS Info
    os_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
    }
    
    # CPU Info
    cpu_info = {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "current_frequency": None,
        "usage_percent": psutil.cpu_percent(interval=1),
    }
    
    # Get CPU frequency if available
    freq = psutil.cpu_freq()
    if freq:
        cpu_info["current_frequency"] = f"{freq.current:.0f} MHz"
        cpu_info["max_frequency"] = f"{freq.max:.0f} MHz"
    
    # Memory Info
    mem = psutil.virtual_memory()
    memory_info = {
        "total": format_bytes(mem.total),
        "available": format_bytes(mem.available),
        "used": format_bytes(mem.used),
        "percent": mem.percent,
    }
    
    # Disk Info
    disk_info = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": format_bytes(usage.total),
                "used": format_bytes(usage.used),
                "free": format_bytes(usage.free),
                "percent": usage.percent,
            })
        except PermissionError:
            continue
    
    # Boot time
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    return {
        "os": os_info,
        "cpu": cpu_info,
        "memory": memory_info,
        "disks": disk_info,
        "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": format_uptime(uptime.total_seconds()),
    }


def get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    return psutil.cpu_percent(interval=0.5)


def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage."""
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "available": mem.available,
        "used": mem.used,
        "percent": mem.percent,
        "total_formatted": format_bytes(mem.total),
        "available_formatted": format_bytes(mem.available),
        "used_formatted": format_bytes(mem.used),
    }


def get_disk_usage(path: str = "/") -> Dict[str, Any]:
    """Get disk usage for a specific path."""
    try:
        usage = psutil.disk_usage(path)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent,
            "total_formatted": format_bytes(usage.total),
            "used_formatted": format_bytes(usage.used),
            "free_formatted": format_bytes(usage.free),
        }
    except Exception as e:
        return {"error": str(e)}


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} PB"


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "< 1m"

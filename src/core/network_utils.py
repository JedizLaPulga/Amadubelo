"""
Network Utils
Network and IP information.
"""

import socket
import psutil
from typing import Dict, List, Any, Optional


def get_network_info() -> Dict[str, Any]:
    """Get comprehensive network information."""
    
    # Get local IP
    local_ip = get_local_ip()
    
    # Get all network interfaces
    interfaces = get_network_interfaces()
    
    # Get active connections count
    connections = len(psutil.net_connections())
    
    return {
        "local_ip": local_ip,
        "hostname": socket.gethostname(),
        "interfaces": interfaces,
        "active_connections": connections,
    }


def get_local_ip() -> str:
    """Get the local IP address."""
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_network_interfaces() -> List[Dict[str, Any]]:
    """Get all network interfaces with their details."""
    interfaces = []
    
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    for iface_name, iface_addrs in addrs.items():
        iface_info = {
            "name": iface_name,
            "addresses": [],
            "is_up": False,
            "speed": None,
        }
        
        # Get stats
        if iface_name in stats:
            iface_info["is_up"] = stats[iface_name].isup
            iface_info["speed"] = stats[iface_name].speed
        
        # Get addresses
        for addr in iface_addrs:
            addr_info = {
                "family": str(addr.family.name),
                "address": addr.address,
                "netmask": addr.netmask,
            }
            
            # Filter to show only IPv4 and IPv6
            if addr.family.name in ['AF_INET', 'AF_INET6']:
                iface_info["addresses"].append(addr_info)
        
        if iface_info["addresses"]:  # Only add interfaces with IP addresses
            interfaces.append(iface_info)
    
    return interfaces


def get_network_io() -> Dict[str, Any]:
    """Get network I/O statistics."""
    io = psutil.net_io_counters()
    
    return {
        "bytes_sent": io.bytes_sent,
        "bytes_recv": io.bytes_recv,
        "packets_sent": io.packets_sent,
        "packets_recv": io.packets_recv,
        "bytes_sent_formatted": format_bytes(io.bytes_sent),
        "bytes_recv_formatted": format_bytes(io.bytes_recv),
    }


def is_connected() -> bool:
    """Check if there's an active internet connection."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} PB"

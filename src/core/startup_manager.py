"""
Startup Manager
Manage Windows startup programs.
"""

import winreg
from typing import List, Dict, Optional
import os


# Registry paths for startup items
STARTUP_KEYS = [
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
]


def get_startup_items() -> List[Dict]:
    """
    Get all startup programs from Windows Registry.
    
    Returns:
        List of startup items with name, path, and location
    """
    items = []
    
    for root_key, subkey in STARTUP_KEYS:
        try:
            key = winreg.OpenKey(root_key, subkey, 0, winreg.KEY_READ)
            
            # Determine location name
            if root_key == winreg.HKEY_CURRENT_USER:
                location = "Current User"
            else:
                location = "Local Machine"
            
            if "RunOnce" in subkey:
                location += " (Run Once)"
            
            # Enumerate values
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    items.append({
                        "name": name,
                        "path": value,
                        "location": location,
                        "enabled": True,
                        "root_key": root_key,
                        "subkey": subkey,
                    })
                    i += 1
                except OSError:
                    break
            
            winreg.CloseKey(key)
            
        except FileNotFoundError:
            continue
        except PermissionError:
            continue
    
    # Also check startup folder
    startup_folder_items = get_startup_folder_items()
    items.extend(startup_folder_items)
    
    return items


def get_startup_folder_items() -> List[Dict]:
    """Get startup items from the Startup folder."""
    items = []
    
    # User startup folder
    user_startup = os.path.join(
        os.environ.get('APPDATA', ''),
        r'Microsoft\Windows\Start Menu\Programs\Startup'
    )
    
    if os.path.exists(user_startup):
        for filename in os.listdir(user_startup):
            filepath = os.path.join(user_startup, filename)
            if os.path.isfile(filepath):
                items.append({
                    "name": os.path.splitext(filename)[0],
                    "path": filepath,
                    "location": "Startup Folder",
                    "enabled": True,
                    "is_folder_item": True,
                })
    
    return items


def disable_startup_item(name: str, root_key, subkey: str) -> bool:
    """
    Disable a startup item by removing it from registry.
    
    Note: This actually removes the entry. To truly disable,
    you might want to move it to a disabled key instead.
    
    Args:
        name: Name of the startup item
        root_key: Registry root key
        subkey: Registry subkey path
        
    Returns:
        True if successful
    """
    try:
        key = winreg.OpenKey(root_key, subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        return False


def add_startup_item(name: str, path: str, current_user: bool = True) -> bool:
    """
    Add a program to startup.
    
    Args:
        name: Display name for the startup item
        path: Full path to the executable
        current_user: If True, add to current user. Else, local machine.
        
    Returns:
        True if successful
    """
    if current_user:
        root_key = winreg.HKEY_CURRENT_USER
    else:
        root_key = winreg.HKEY_LOCAL_MACHINE
    
    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        key = winreg.OpenKey(root_key, subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        return False

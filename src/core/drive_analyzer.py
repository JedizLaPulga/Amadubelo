"""
Drive Analyzer
Analyze disk space usage.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Callable
from collections import defaultdict


def analyze_folder(
    folder_path: str,
    max_depth: int = 2,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    Analyze disk space usage in a folder.
    
    Args:
        folder_path: Path to analyze
        max_depth: Maximum depth to analyze (default 2)
        progress_callback: Optional callback(current_folder)
        
    Returns:
        Dictionary with folder sizes and structure
    """
    if not os.path.exists(folder_path):
        return {"error": "Path does not exist"}
    
    result = {
        "path": folder_path,
        "total_size": 0,
        "file_count": 0,
        "folder_count": 0,
        "children": [],
    }
    
    try:
        # Get immediate children sizes
        for item in os.scandir(folder_path):
            if progress_callback:
                progress_callback(item.path)
            
            try:
                if item.is_file(follow_symlinks=False):
                    result["file_count"] += 1
                    result["total_size"] += item.stat().st_size
                    
                elif item.is_dir(follow_symlinks=False):
                    result["folder_count"] += 1
                    folder_size = get_folder_size(item.path)
                    result["total_size"] += folder_size
                    
                    result["children"].append({
                        "name": item.name,
                        "path": item.path,
                        "size": folder_size,
                        "size_formatted": format_size(folder_size),
                        "is_folder": True,
                    })
            except (OSError, PermissionError):
                continue
        
        # Sort children by size (largest first)
        result["children"].sort(key=lambda x: x["size"], reverse=True)
        
        # Calculate percentages
        total = result["total_size"]
        for child in result["children"]:
            if total > 0:
                child["percent"] = (child["size"] / total) * 100
            else:
                child["percent"] = 0
        
        result["total_size_formatted"] = format_size(result["total_size"])
        
    except PermissionError:
        result["error"] = "Permission denied"
    
    return result


def get_folder_size(folder_path: str) -> int:
    """
    Calculate total size of a folder.
    
    Args:
        folder_path: Path to folder
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    
    return total_size


def get_largest_files(
    folder_path: str,
    count: int = 20,
    progress_callback: Optional[Callable] = None
) -> List[Dict]:
    """
    Find the largest files in a folder.
    
    Args:
        folder_path: Path to search
        count: Number of files to return
        progress_callback: Optional callback
        
    Returns:
        List of file info dictionaries
    """
    files = []
    
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                
                if progress_callback:
                    progress_callback(filepath)
                
                try:
                    size = os.path.getsize(filepath)
                    files.append({
                        "name": filename,
                        "path": filepath,
                        "size": size,
                        "size_formatted": format_size(size),
                    })
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    
    # Sort by size and return top N
    files.sort(key=lambda x: x["size"], reverse=True)
    return files[:count]


def get_file_type_breakdown(
    folder_path: str,
    progress_callback: Optional[Callable] = None
) -> Dict[str, Dict]:
    """
    Get breakdown of file types and their sizes.
    
    Args:
        folder_path: Path to analyze
        progress_callback: Optional callback
        
    Returns:
        Dictionary mapping extension to size info
    """
    type_sizes = defaultdict(lambda: {"size": 0, "count": 0})
    
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                
                if progress_callback:
                    progress_callback(filepath)
                
                try:
                    ext = os.path.splitext(filename)[1].lower() or "(no extension)"
                    size = os.path.getsize(filepath)
                    
                    type_sizes[ext]["size"] += size
                    type_sizes[ext]["count"] += 1
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    
    # Add formatted sizes and sort
    result = []
    for ext, data in type_sizes.items():
        result.append({
            "extension": ext,
            "size": data["size"],
            "size_formatted": format_size(data["size"]),
            "count": data["count"],
        })
    
    result.sort(key=lambda x: x["size"], reverse=True)
    return result


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

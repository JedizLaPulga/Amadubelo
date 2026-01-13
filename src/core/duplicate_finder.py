"""
Duplicate Finder
Find duplicate files using hash comparison.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Callable
from collections import defaultdict


def find_duplicates(
    folder_path: str,
    recursive: bool = True,
    min_size: int = 0,
    extensions: Optional[List[str]] = None,
    progress_callback: Optional[Callable] = None
) -> Dict[str, List[str]]:
    """
    Find duplicate files in a folder.
    
    Args:
        folder_path: Path to search
        recursive: Search subdirectories
        min_size: Minimum file size in bytes
        extensions: Only check these extensions (e.g., ['.jpg', '.png'])
        progress_callback: Optional callback(current, total, current_file)
        
    Returns:
        Dictionary mapping hash -> list of duplicate file paths
    """
    # First pass: group by size
    size_groups = defaultdict(list)
    
    if recursive:
        walker = os.walk(folder_path)
    else:
        walker = [(folder_path, [], os.listdir(folder_path))]
    
    # Collect files
    all_files = []
    for root, dirs, files in walker:
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # Check extension filter
            if extensions:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in extensions:
                    continue
            
            try:
                size = os.path.getsize(filepath)
                if size >= min_size:
                    all_files.append((filepath, size))
            except (OSError, PermissionError):
                continue
    
    # Group by size (potential duplicates must be same size)
    for filepath, size in all_files:
        size_groups[size].append(filepath)
    
    # Keep only groups with potential duplicates
    potential_duplicates = {
        size: files for size, files in size_groups.items()
        if len(files) > 1
    }
    
    # Second pass: hash files with same size
    hash_groups = defaultdict(list)
    total_to_check = sum(len(files) for files in potential_duplicates.values())
    checked = 0
    
    for size, files in potential_duplicates.items():
        for filepath in files:
            try:
                file_hash = compute_hash(filepath)
                hash_groups[file_hash].append(filepath)
            except (OSError, PermissionError):
                continue
            
            checked += 1
            if progress_callback:
                progress_callback(checked, total_to_check, os.path.basename(filepath))
    
    # Filter to only actual duplicates
    duplicates = {
        hash_val: files for hash_val, files in hash_groups.items()
        if len(files) > 1
    }
    
    return duplicates


def compute_hash(filepath: str, chunk_size: int = 65536) -> str:
    """
    Compute MD5 hash of a file.
    
    Args:
        filepath: Path to file
        chunk_size: Size of chunks to read
        
    Returns:
        MD5 hash string
    """
    hasher = hashlib.md5()
    
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            hasher.update(data)
    
    return hasher.hexdigest()


def get_duplicate_stats(duplicates: Dict[str, List[str]]) -> Dict:
    """
    Get statistics about found duplicates.
    
    Args:
        duplicates: Dictionary from find_duplicates()
        
    Returns:
        Statistics dictionary
    """
    total_groups = len(duplicates)
    total_files = sum(len(files) for files in duplicates.values())
    wasted_files = total_files - total_groups  # Files that are duplicates of others
    
    wasted_space = 0
    for files in duplicates.values():
        if files:
            try:
                file_size = os.path.getsize(files[0])
                wasted_space += file_size * (len(files) - 1)
            except (OSError, PermissionError):
                continue
    
    return {
        "groups": total_groups,
        "total_files": total_files,
        "duplicate_files": wasted_files,
        "wasted_space": wasted_space,
        "wasted_space_formatted": format_size(wasted_space),
    }


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

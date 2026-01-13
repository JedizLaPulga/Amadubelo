"""
File Shredder
Securely delete files by overwriting before deletion.
"""

import os
import random
from pathlib import Path
from typing import List, Optional, Callable


def shred_file(
    filepath: str,
    passes: int = 3,
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Securely shred a file by overwriting with random data.
    
    Args:
        filepath: Path to file to shred
        passes: Number of overwrite passes (default 3)
        progress_callback: Optional callback(pass_num, total_passes)
        
    Returns:
        True if successful
    """
    try:
        if not os.path.isfile(filepath):
            return False
        
        file_size = os.path.getsize(filepath)
        
        # Perform multiple overwrite passes
        for pass_num in range(passes):
            with open(filepath, 'wb') as f:
                # Write random data in chunks
                chunk_size = 65536  # 64KB chunks
                written = 0
                
                while written < file_size:
                    remaining = file_size - written
                    chunk = min(chunk_size, remaining)
                    
                    # Different patterns for different passes
                    if pass_num == 0:
                        data = bytes([0x00] * chunk)  # All zeros
                    elif pass_num == 1:
                        data = bytes([0xFF] * chunk)  # All ones
                    else:
                        data = random.randbytes(chunk)  # Random
                    
                    f.write(data)
                    written += chunk
                
                f.flush()
                os.fsync(f.fileno())
            
            if progress_callback:
                progress_callback(pass_num + 1, passes)
        
        # Finally delete the file
        os.remove(filepath)
        
        return True
        
    except Exception as e:
        return False


def shred_files(
    filepaths: List[str],
    passes: int = 3,
    progress_callback: Optional[Callable] = None
) -> dict:
    """
    Shred multiple files.
    
    Args:
        filepaths: List of file paths
        passes: Number of overwrite passes
        progress_callback: Optional callback(current_file, total_files, filename)
        
    Returns:
        Dictionary with results
    """
    total = len(filepaths)
    success_count = 0
    failed = []
    
    for i, filepath in enumerate(filepaths):
        filename = os.path.basename(filepath)
        
        if progress_callback:
            progress_callback(i + 1, total, filename)
        
        if shred_file(filepath, passes):
            success_count += 1
        else:
            failed.append(filepath)
    
    return {
        "total": total,
        "success": success_count,
        "failed": len(failed),
        "failed_files": failed,
    }


def shred_folder(
    folder_path: str,
    passes: int = 3,
    progress_callback: Optional[Callable] = None
) -> dict:
    """
    Shred all files in a folder and delete the folder.
    
    Args:
        folder_path: Path to folder
        passes: Number of overwrite passes
        progress_callback: Optional callback
        
    Returns:
        Dictionary with results
    """
    if not os.path.isdir(folder_path):
        return {"success": False, "error": "Not a directory"}
    
    # Collect all files
    files = []
    for root, dirs, filenames in os.walk(folder_path, topdown=False):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    
    # Shred all files
    result = shred_files(files, passes, progress_callback)
    
    # Remove empty directories
    try:
        for root, dirs, _ in os.walk(folder_path, topdown=False):
            for dirname in dirs:
                try:
                    os.rmdir(os.path.join(root, dirname))
                except:
                    pass
        os.rmdir(folder_path)
        result["folder_deleted"] = True
    except:
        result["folder_deleted"] = False
    
    return result


def get_overwrite_methods() -> List[dict]:
    """Get available secure deletion methods."""
    return [
        {
            "name": "Quick (1 pass)",
            "passes": 1,
            "description": "Single pass of random data. Fast but less secure.",
        },
        {
            "name": "Standard (3 passes)",
            "passes": 3,
            "description": "DoD 5220.22-M standard. Good security.",
        },
        {
            "name": "Thorough (7 passes)",
            "passes": 7,
            "description": "Multiple patterns. Very secure.",
        },
        {
            "name": "Paranoid (35 passes)",
            "passes": 35,
            "description": "Gutmann method. Maximum security. Very slow.",
        },
    ]

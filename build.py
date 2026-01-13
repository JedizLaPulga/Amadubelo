"""
Amadubelo Build Script
Creates a standalone .exe using PyInstaller.
"""

import subprocess
import sys
import os
from pathlib import Path


def build():
    """Build the Amadubelo executable."""
    
    # Paths
    root_dir = Path(__file__).parent
    src_dir = root_dir / "src"
    img_dir = root_dir / "img"
    main_script = src_dir / "main.py"
    icon_path = img_dir / "amadubelo.ico"  # Need to convert PNG to ICO
    
    # Check if icon exists (try both ico and png)
    if not icon_path.exists():
        icon_path = img_dir / "amadubelo.png"
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single exe
        "--windowed",                   # No console
        "--name", "Amadubelo",
        "--add-data", f"{src_dir};src",  # Include source
    ]
    
    # Add icon if exists
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    
    # Add the main script
    cmd.append(str(main_script))
    
    print("🔨 Building Amadubelo...")
    print(f"   Command: {' '.join(cmd)}")
    print()
    
    # Run PyInstaller
    result = subprocess.run(cmd, cwd=root_dir)
    
    if result.returncode == 0:
        print()
        print("✅ Build successful!")
        print(f"📦 Executable: {root_dir / 'dist' / 'Amadubelo.exe'}")
    else:
        print()
        print("❌ Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    build()

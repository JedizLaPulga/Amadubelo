"""
Amadubelo - All-in-One Offline Utility Toolkit
Entry point for the application.
"""

import sys
import os


def get_base_path():
    """Get base path for bundled or development mode."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return sys._MEIPASS
    else:
        # Running in development
        return os.path.dirname(os.path.abspath(__file__))


# Add the correct path for imports
base_path = get_base_path()
src_path = os.path.join(base_path, 'src') if getattr(sys, 'frozen', False) else base_path
sys.path.insert(0, src_path)

# Now import the app module
from app import AmaduebeloApp


def main():
    """Launch the Amadubelo application."""
    application = AmaduebeloApp()
    application.mainloop()


if __name__ == "__main__":
    main()

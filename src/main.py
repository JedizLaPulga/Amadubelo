"""
Amadubelo - All-in-One Offline Utility Toolkit
Entry point for the application.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import AmaduebeloApp


def main():
    """Launch the Amadubelo application."""
    app = AmaduebeloApp()
    app.mainloop()


if __name__ == "__main__":
    main()

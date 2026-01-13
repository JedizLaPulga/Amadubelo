"""
Amadubelo - Main Application Window
Modern tabbed interface with File Utilities and System Utilities.
"""

import customtkinter as ctk
from ui.file_utilities.tab_view import FileUtilitiesTab
from ui.system_utilities.tab_view import SystemUtilitiesTab


class AmaduebeloApp(ctk.CTk):
    """Main application window with tabbed interface."""
    
    # Purple accent color scheme
    COLORS = {
        "primary": "#8B5CF6",        # Purple
        "primary_hover": "#7C3AED",  # Darker purple
        "primary_light": "#A78BFA",  # Lighter purple
        "bg_dark": "#0F0F1A",        # Very dark blue-black
        "bg_card": "#1A1A2E",        # Card background
        "bg_card_hover": "#252542",  # Card hover
        "text": "#FFFFFF",           # White text
        "text_secondary": "#A0A0B0", # Gray text
        "success": "#10B981",        # Green
        "warning": "#F59E0B",        # Orange
        "error": "#EF4444",          # Red
    }
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Amadubelo")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Apply dark background
        self.configure(fg_color=self.COLORS["bg_dark"])
        
        # Create UI
        self._create_header()
        self._create_tabs()
        
    def _create_header(self):
        """Create the header with app title."""
        header = ctk.CTkFrame(self, fg_color=self.COLORS["bg_card"], height=60)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(0, weight=1)
        
        # App title
        title = ctk.CTkLabel(
            header,
            text="⚡ AMADUBELO",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.COLORS["primary_light"]
        )
        title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            header,
            text="Offline Utility GUI Project",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.COLORS["text_secondary"]
        )
        subtitle.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
    def _create_tabs(self):
        """Create the main tabbed interface."""
        # Tab view
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=self.COLORS["bg_dark"],
            segmented_button_fg_color=self.COLORS["bg_card"],
            segmented_button_selected_color=self.COLORS["primary"],
            segmented_button_selected_hover_color=self.COLORS["primary_hover"],
            segmented_button_unselected_color=self.COLORS["bg_card"],
            segmented_button_unselected_hover_color=self.COLORS["bg_card_hover"],
            text_color=self.COLORS["text"],
            corner_radius=10
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        
        # Add tabs
        self.tabview.add("📂  File Utilities")
        self.tabview.add("🖥️  System Utilities")
        
        # Configure tab content
        self.tabview.tab("📂  File Utilities").grid_columnconfigure(0, weight=1)
        self.tabview.tab("📂  File Utilities").grid_rowconfigure(0, weight=1)
        self.tabview.tab("🖥️  System Utilities").grid_columnconfigure(0, weight=1)
        self.tabview.tab("🖥️  System Utilities").grid_rowconfigure(0, weight=1)
        
        # File Utilities Tab
        self.file_utilities = FileUtilitiesTab(
            self.tabview.tab("📂  File Utilities"),
            colors=self.COLORS
        )
        self.file_utilities.grid(row=0, column=0, sticky="nsew")
        
        # System Utilities Tab
        self.system_utilities = SystemUtilitiesTab(
            self.tabview.tab("🖥️  System Utilities"),
            colors=self.COLORS
        )
        self.system_utilities.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    app = AmaduebeloApp()
    app.mainloop()

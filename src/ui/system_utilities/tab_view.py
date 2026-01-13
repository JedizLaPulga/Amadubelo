"""
System Utilities Tab View
Main container for system utility tools.
"""

import customtkinter as ctk
from typing import Optional
from ui.components.tool_card import ToolCard


class SystemUtilitiesTab(ctk.CTkFrame):
    """Main view for System Utilities tab with tool cards."""
    
    TOOLS = [
        {
            "id": "disk_cleanup",
            "icon": "🧹",
            "title": "Disk Cleanup",
            "description": "Delete temp files and cache"
        },
        {
            "id": "system_info",
            "icon": "📊",
            "title": "System Info",
            "description": "View hardware and OS info"
        },
        {
            "id": "startup_manager",
            "icon": "🚀",
            "title": "Startup Manager",
            "description": "Manage startup programs"
        },
        {
            "id": "secure_shredder",
            "icon": "🔒",
            "title": "Secure Shredder",
            "description": "Permanently delete files"
        },
        {
            "id": "duplicate_finder",
            "icon": "📁",
            "title": "Duplicate Finder",
            "description": "Find duplicate files"
        },
        {
            "id": "battery_health",
            "icon": "🔋",
            "title": "Battery Health",
            "description": "Check battery status"
        },
        {
            "id": "network_info",
            "icon": "📶",
            "title": "Network Info",
            "description": "View IP and connection"
        },
        {
            "id": "recycle_bin",
            "icon": "🗑️",
            "title": "Recycle Bin",
            "description": "Empty recycle bin"
        },
        {
            "id": "drive_analyzer",
            "icon": "💾",
            "title": "Drive Analyzer",
            "description": "Analyze disk space"
        },
    ]
    
    def __init__(self, parent, colors: dict, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.colors = colors
        self.current_view = None
        
        self.configure(fg_color=colors["bg_dark"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Container for switching views
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Show tool grid
        self._show_tool_grid()
        
    def _show_tool_grid(self):
        """Show the grid of tool cards."""
        # Clear current view
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            scrollbar_button_color=self.colors["primary"],
            scrollbar_button_hover_color=self.colors["primary_hover"]
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid for cards
        for i in range(4):
            scroll_frame.grid_columnconfigure(i, weight=1, uniform="col")
        
        # Create tool cards
        for i, tool in enumerate(self.TOOLS):
            row = i // 4
            col = i % 4
            
            card = ToolCard(
                scroll_frame,
                title=tool["title"],
                icon=tool["icon"],
                description=tool["description"],
                colors=self.colors,
                command=lambda t=tool: self._open_tool(t["id"])
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    def _open_tool(self, tool_id: str):
        """Open a specific tool view."""
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Import and create the tool view
        view = None
        
        if tool_id == "disk_cleanup":
            from ui.system_utilities.disk_cleanup import DiskCleanupView
            view = DiskCleanupView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "system_info":
            from ui.system_utilities.system_info import SystemInfoView
            view = SystemInfoView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "startup_manager":
            from ui.system_utilities.startup_manager import StartupManagerView
            view = StartupManagerView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "secure_shredder":
            from ui.system_utilities.secure_shredder import SecureShredderView
            view = SecureShredderView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "duplicate_finder":
            from ui.system_utilities.duplicate_finder import DuplicateFinderView
            view = DuplicateFinderView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "battery_health":
            from ui.system_utilities.battery_health import BatteryHealthView
            view = BatteryHealthView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "network_info":
            from ui.system_utilities.network_info import NetworkInfoView
            view = NetworkInfoView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "recycle_bin":
            from ui.system_utilities.recycle_bin import RecycleBinView
            view = RecycleBinView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "drive_analyzer":
            from ui.system_utilities.drive_analyzer import DriveAnalyzerView
            view = DriveAnalyzerView(self.container, self.colors, on_back=self._show_tool_grid)
        
        if view:
            view.grid(row=0, column=0, sticky="nsew")
            self.current_view = view

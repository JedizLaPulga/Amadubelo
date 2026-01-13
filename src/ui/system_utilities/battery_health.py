"""
Battery Health View
Check battery status.
"""

import customtkinter as ctk
import threading
from ui.components.tool_view_base import ToolViewBase


class BatteryHealthView(ToolViewBase):
    """View for battery health information."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Battery Health",
            icon="🔋",
            description="Check battery status and remaining time",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self._create_content()
        self._load_battery_info()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        
        # Main battery display
        battery_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=15)
        battery_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        battery_frame.grid_columnconfigure(0, weight=1)
        
        # Battery icon and percentage
        self.battery_icon = ctk.CTkLabel(
            battery_frame,
            text="🔋",
            font=ctk.CTkFont(size=72),
            text_color=self.colors["primary_light"]
        )
        self.battery_icon.grid(row=0, column=0, pady=(30, 10))
        
        self.percent_label = ctk.CTkLabel(
            battery_frame,
            text="---%",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=self.colors["text"]
        )
        self.percent_label.grid(row=1, column=0, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            battery_frame,
            text="Loading...",
            font=ctk.CTkFont(size=16),
            text_color=self.colors["text_secondary"]
        )
        self.status_label.grid(row=2, column=0, pady=(0, 30))
        
        # Details frame
        details_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        details_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        details_frame.grid_columnconfigure(0, weight=1)
        
        # Details container
        self.details_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        self.details_container.grid(row=0, column=0, padx=20, pady=20)
        self.details_container.grid_columnconfigure((0, 1), weight=1)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            content,
            text="🔄 Refresh",
            height=40,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._load_battery_info
        )
        refresh_btn.grid(row=2, column=0)
        
    def _load_battery_info(self):
        """Load battery information."""
        thread = threading.Thread(target=self._do_load)
        thread.daemon = True
        thread.start()
        
    def _do_load(self):
        """Perform loading."""
        try:
            from core.battery_utils import get_battery_info, has_battery
            
            if not has_battery():
                self.after(0, self._show_no_battery)
                return
                
            info = get_battery_info()
            self.after(0, lambda: self._display_info(info))
            
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))
            
    def _show_no_battery(self):
        """Show no battery message."""
        self.battery_icon.configure(text="🔌")
        self.percent_label.configure(text="N/A")
        self.status_label.configure(text="No battery detected (Desktop PC)")
        self.set_status("No battery found")
        
    def _display_info(self, info):
        """Display battery information."""
        if info is None:
            self._show_no_battery()
            return
            
        # Update main display
        percent = info.get("percent", 0)
        self.percent_label.configure(text=f"{percent}%")
        
        # Update icon based on level
        if info.get("power_plugged"):
            self.battery_icon.configure(text="🔌", text_color=self.colors["success"])
        elif percent > 80:
            self.battery_icon.configure(text="🔋", text_color=self.colors["success"])
        elif percent > 40:
            self.battery_icon.configure(text="🔋", text_color=self.colors["warning"])
        elif percent > 20:
            self.battery_icon.configure(text="🪫", text_color=self.colors["warning"])
        else:
            self.battery_icon.configure(text="🪫", text_color=self.colors["error"])
        
        # Status
        status = info.get("status", "Unknown")
        time_left = info.get("time_left")
        
        if time_left:
            self.status_label.configure(text=f"{status} • {time_left} remaining")
        else:
            self.status_label.configure(text=status)
        
        # Clear details
        for widget in self.details_container.winfo_children():
            widget.destroy()
        
        # Add details
        details = [
            ("Status", status),
            ("Power Plugged", "Yes" if info.get("power_plugged") else "No"),
            ("Battery Level", f"{percent}%"),
        ]
        
        if time_left:
            details.append(("Time Remaining", time_left))
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = i % 2
            
            item_frame = ctk.CTkFrame(self.details_container, fg_color="transparent")
            item_frame.grid(row=row, column=col, padx=20, pady=10)
            
            label_widget = ctk.CTkLabel(
                item_frame,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_secondary"]
            )
            label_widget.pack()
            
            value_widget = ctk.CTkLabel(
                item_frame,
                text=value,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors["text"]
            )
            value_widget.pack()
        
        self.set_status("Battery info loaded")

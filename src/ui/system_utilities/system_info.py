"""
System Info View
Display system information.
"""

import customtkinter as ctk
import threading
from ui.components.tool_view_base import ToolViewBase


class SystemInfoView(ToolViewBase):
    """View for system information."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="System Info",
            icon="📊",
            description="View detailed information about your system hardware and software",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self._create_content()
        self._load_info()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        
        # OS Info Card
        self.os_card = self._create_info_card(content, "🖥️ Operating System", 0, 0)
        
        # CPU Info Card
        self.cpu_card = self._create_info_card(content, "⚡ Processor", 0, 1)
        
        # Memory Info Card
        self.memory_card = self._create_info_card(content, "🧠 Memory", 1, 0)
        
        # Storage Info Card
        self.storage_card = self._create_info_card(content, "💾 Storage", 1, 1)
        
        # Uptime Card
        self.uptime_card = self._create_info_card(content, "⏱️ Uptime", 2, 0)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            content,
            text="🔄 Refresh",
            height=40,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._load_info
        )
        refresh_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
    def _create_info_card(self, parent, title: str, row: int, col: int):
        """Create an info card."""
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["primary_light"]
        )
        title_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        return content_frame
        
    def _load_info(self):
        """Load system information."""
        self.set_status("Loading system information...")
        
        thread = threading.Thread(target=self._do_load)
        thread.daemon = True
        thread.start()
        
    def _do_load(self):
        """Perform info loading."""
        try:
            from core.system_info import get_system_info
            info = get_system_info()
            self.after(0, lambda: self._display_info(info))
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))
            
    def _display_info(self, info: dict):
        """Display system information."""
        self.set_status("Ready")
        
        # Clear cards
        for card in [self.os_card, self.cpu_card, self.memory_card, self.storage_card, self.uptime_card]:
            for widget in card.winfo_children():
                widget.destroy()
        
        # OS Info
        os_info = info.get("os", {})
        self._add_info_row(self.os_card, "System", os_info.get("system", "Unknown"))
        self._add_info_row(self.os_card, "Release", os_info.get("release", "Unknown"))
        self._add_info_row(self.os_card, "Machine", os_info.get("machine", "Unknown"))
        self._add_info_row(self.os_card, "Hostname", os_info.get("hostname", "Unknown"))
        
        # CPU Info
        cpu_info = info.get("cpu", {})
        self._add_info_row(self.cpu_card, "Cores", f"{cpu_info.get('physical_cores', '?')} physical, {cpu_info.get('total_cores', '?')} logical")
        self._add_info_row(self.cpu_card, "Frequency", cpu_info.get("current_frequency", "Unknown"))
        self._add_info_row(self.cpu_card, "Usage", f"{cpu_info.get('usage_percent', 0):.1f}%")
        
        # Memory Info
        mem_info = info.get("memory", {})
        self._add_info_row(self.memory_card, "Total", mem_info.get("total", "Unknown"))
        self._add_info_row(self.memory_card, "Used", mem_info.get("used", "Unknown"))
        self._add_info_row(self.memory_card, "Available", mem_info.get("available", "Unknown"))
        self._add_info_row(self.memory_card, "Usage", f"{mem_info.get('percent', 0):.1f}%")
        
        # Storage Info
        disks = info.get("disks", [])
        for disk in disks[:3]:  # Show max 3 disks
            self._add_info_row(
                self.storage_card,
                disk.get("mountpoint", "Unknown"),
                f"{disk.get('used', '?')} / {disk.get('total', '?')} ({disk.get('percent', 0):.0f}%)"
            )
        
        # Uptime
        self._add_info_row(self.uptime_card, "Boot Time", info.get("boot_time", "Unknown"))
        self._add_info_row(self.uptime_card, "Uptime", info.get("uptime", "Unknown"))
        
    def _add_info_row(self, parent, label: str, value: str):
        """Add an info row to a card."""
        row = len(parent.winfo_children())
        
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", pady=2)
        frame.grid_columnconfigure(1, weight=1)
        
        label_widget = ctk.CTkLabel(
            frame,
            text=f"{label}:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        label_widget.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        value_widget = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text"]
        )
        value_widget.grid(row=0, column=1, sticky="e")

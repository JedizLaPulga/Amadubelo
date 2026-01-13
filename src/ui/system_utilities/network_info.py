"""
Network Info View
Display network information.
"""

import customtkinter as ctk
import threading
from ui.components.tool_view_base import ToolViewBase


class NetworkInfoView(ToolViewBase):
    """View for network information."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Network Info",
            icon="📶",
            description="View your network connection details and IP addresses",
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
        
        # Connection status card
        self.status_card = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        self.status_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.status_card.grid_columnconfigure(0, weight=1)
        
        self.connection_icon = ctk.CTkLabel(
            self.status_card,
            text="📶",
            font=ctk.CTkFont(size=48),
            text_color=self.colors["primary_light"]
        )
        self.connection_icon.grid(row=0, column=0, pady=(20, 5))
        
        self.connection_label = ctk.CTkLabel(
            self.status_card,
            text="Checking connection...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        self.connection_label.grid(row=1, column=0, pady=(0, 20))
        
        # Local IP card
        self.ip_card = self._create_info_card(content, "🌐 Local IP", 1, 0)
        
        # Hostname card
        self.hostname_card = self._create_info_card(content, "💻 Hostname", 1, 1)
        
        # Interfaces frame
        self.interfaces_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        self.interfaces_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 20))
        self.interfaces_frame.grid_columnconfigure(0, weight=1)
        
        interfaces_title = ctk.CTkLabel(
            self.interfaces_frame,
            text="📡 Network Interfaces",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["primary_light"]
        )
        interfaces_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        self.interfaces_container = ctk.CTkFrame(self.interfaces_frame, fg_color="transparent")
        self.interfaces_container.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.interfaces_container.grid_columnconfigure(0, weight=1)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            content,
            text="🔄 Refresh",
            height=40,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._load_info
        )
        refresh_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
    def _create_info_card(self, parent, title: str, row: int, col: int):
        """Create an info card."""
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        title_label.grid(row=0, column=0, padx=15, pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text="...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text"]
        )
        value_label.grid(row=1, column=0, padx=15, pady=(0, 15))
        
        return value_label
        
    def _load_info(self):
        """Load network information."""
        self.set_status("Loading network info...")
        
        thread = threading.Thread(target=self._do_load)
        thread.daemon = True
        thread.start()
        
    def _do_load(self):
        """Perform loading."""
        try:
            from core.network_utils import get_network_info, is_connected
            
            connected = is_connected()
            info = get_network_info()
            
            self.after(0, lambda: self._display_info(info, connected))
            
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))
            
    def _display_info(self, info, connected):
        """Display network information."""
        # Connection status
        if connected:
            self.connection_icon.configure(text="✅", text_color=self.colors["success"])
            self.connection_label.configure(text="Connected to Internet")
        else:
            self.connection_icon.configure(text="❌", text_color=self.colors["error"])
            self.connection_label.configure(text="No Internet Connection")
        
        # IP and hostname
        self.ip_card.configure(text=info.get("local_ip", "Unknown"))
        self.hostname_card.configure(text=info.get("hostname", "Unknown"))
        
        # Clear interfaces
        for widget in self.interfaces_container.winfo_children():
            widget.destroy()
        
        # Display interfaces
        interfaces = info.get("interfaces", [])
        for i, iface in enumerate(interfaces):
            if not iface.get("is_up"):
                continue
                
            iface_frame = ctk.CTkFrame(
                self.interfaces_container,
                fg_color=self.colors["bg_dark"],
                corner_radius=8
            )
            iface_frame.grid(row=i, column=0, sticky="ew", pady=3)
            iface_frame.grid_columnconfigure(1, weight=1)
            
            # Name
            name = ctk.CTkLabel(
                iface_frame,
                text=iface.get("name", "Unknown"),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["text"]
            )
            name.grid(row=0, column=0, padx=10, pady=8, sticky="w")
            
            # Addresses
            addresses = iface.get("addresses", [])
            for addr in addresses:
                if addr.get("family") == "AF_INET":  # IPv4
                    ip = ctk.CTkLabel(
                        iface_frame,
                        text=addr.get("address", ""),
                        font=ctk.CTkFont(size=12),
                        text_color=self.colors["primary_light"]
                    )
                    ip.grid(row=0, column=1, padx=10, pady=8, sticky="e")
                    break
        
        self.set_status("Network info loaded")

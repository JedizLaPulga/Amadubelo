"""
Startup Manager View
Manage Windows startup programs.
"""

import customtkinter as ctk
import threading
from tkinter import messagebox
from ui.components.tool_view_base import ToolViewBase


class StartupManagerView(ToolViewBase):
    """View for managing startup programs."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Startup Manager",
            icon="🚀",
            description="View and manage programs that run at Windows startup",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.items = []
        self._create_content()
        self._load_items()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # Items frame with scrolling
        self.items_frame = ctk.CTkScrollableFrame(
            content,
            fg_color=self.colors["bg_card"],
            corner_radius=10
        )
        self.items_frame.grid(row=0, column=0, sticky="nsew")
        self.items_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(self.items_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(0, weight=2)
        header.grid_columnconfigure(1, weight=3)
        header.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(
            header,
            text="Program",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Location",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Action",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=2, sticky="e")
        
        # Items container
        self.list_frame = ctk.CTkFrame(self.items_frame, fg_color="transparent")
        self.list_frame.grid(row=1, column=0, sticky="ew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh",
            height=40,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._load_items
        )
        refresh_btn.pack(side="left")
        
    def _load_items(self):
        """Load startup items."""
        self.set_status("Loading startup items...")
        
        # Clear list
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        thread = threading.Thread(target=self._do_load)
        thread.daemon = True
        thread.start()
        
    def _do_load(self):
        """Perform loading."""
        try:
            from core.startup_manager import get_startup_items
            self.items = get_startup_items()
            self.after(0, self._display_items)
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))
            
    def _display_items(self):
        """Display startup items."""
        self.set_status(f"Found {len(self.items)} startup items")
        
        for i, item in enumerate(self.items):
            frame = ctk.CTkFrame(
                self.list_frame,
                fg_color=self.colors["bg_dark"] if i % 2 == 0 else "transparent",
                corner_radius=5
            )
            frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            frame.grid_columnconfigure(0, weight=2)
            frame.grid_columnconfigure(1, weight=3)
            frame.grid_columnconfigure(2, weight=1)
            
            # Name
            name = ctk.CTkLabel(
                frame,
                text=item["name"][:30],
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text"],
                anchor="w"
            )
            name.grid(row=0, column=0, padx=10, pady=8, sticky="w")
            
            # Location
            loc = ctk.CTkLabel(
                frame,
                text=item["location"],
                font=ctk.CTkFont(size=11),
                text_color=self.colors["text_secondary"],
                anchor="w"
            )
            loc.grid(row=0, column=1, padx=10, pady=8, sticky="w")
            
            # Disable button (only for registry items)
            if not item.get("is_folder_item"):
                disable_btn = ctk.CTkButton(
                    frame,
                    text="Disable",
                    width=70,
                    height=28,
                    fg_color=self.colors["error"],
                    hover_color="#dc2626",
                    font=ctk.CTkFont(size=11),
                    command=lambda i=item: self._disable_item(i)
                )
                disable_btn.grid(row=0, column=2, padx=10, pady=5)
            
    def _disable_item(self, item):
        """Disable a startup item."""
        if messagebox.askyesno(
            "Confirm",
            f"Are you sure you want to disable '{item['name']}' from startup?"
        ):
            try:
                from core.startup_manager import disable_startup_item
                success = disable_startup_item(
                    item["name"],
                    item["root_key"],
                    item["subkey"]
                )
                
                if success:
                    self.show_success(f"Disabled: {item['name']}")
                    self._load_items()  # Refresh
                else:
                    self.show_error("Failed to disable item")
                    
            except Exception as e:
                self.show_error(str(e))

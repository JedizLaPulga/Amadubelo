"""
Disk Cleanup View
Clean temporary files and caches.
"""

import customtkinter as ctk
import threading
from ui.components.tool_view_base import ToolViewBase


class DiskCleanupView(ToolViewBase):
    """View for disk cleanup."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Disk Cleanup",
            icon="🧹",
            description="Clean temporary files, cache, and junk to free up disk space",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.locations = []
        self._create_content()
        self._scan_locations()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        
        # Locations frame
        self.locations_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        self.locations_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.locations_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            self.locations_frame,
            text="Cleanable Locations",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text"]
        )
        title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Loading label
        self.loading_label = ctk.CTkLabel(
            self.locations_frame,
            text="Scanning...",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        self.loading_label.grid(row=1, column=0, padx=15, pady=10)
        
        # Container for location items
        self.items_frame = ctk.CTkFrame(self.locations_frame, fg_color="transparent")
        self.items_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.items_frame.grid_columnconfigure(0, weight=1)
        
        # Total space label
        self.total_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["primary_light"]
        )
        self.total_label.grid(row=1, column=0, pady=(0, 20))
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Rescan button
        self.rescan_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Rescan",
            height=45,
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["bg_card_hover"],
            text_color=self.colors["text"],
            command=self._scan_locations
        )
        self.rescan_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        # Clean button
        self.clean_btn = ctk.CTkButton(
            btn_frame,
            text="⚡ Clean Now",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._start_cleanup
        )
        self.clean_btn.grid(row=0, column=1, sticky="ew")
        
    def _scan_locations(self):
        """Scan temp locations."""
        self.loading_label.configure(text="Scanning...")
        self.loading_label.grid()
        
        # Clear items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        # Scan in thread
        thread = threading.Thread(target=self._do_scan)
        thread.daemon = True
        thread.start()
        
    def _do_scan(self):
        """Perform the scan."""
        try:
            from core.disk_cleaner import scan_temp_locations
            self.locations = scan_temp_locations()
            self.after(0, self._display_locations)
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))
            
    def _display_locations(self):
        """Display scanned locations."""
        self.loading_label.grid_remove()
        
        total_size = 0
        self.checkboxes = []
        
        for i, loc in enumerate(self.locations):
            if not loc.get("exists"):
                continue
                
            frame = ctk.CTkFrame(self.items_frame, fg_color="transparent")
            frame.grid(row=i, column=0, sticky="ew", pady=2)
            frame.grid_columnconfigure(1, weight=1)
            
            # Checkbox
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(
                frame,
                text="",
                variable=var,
                fg_color=self.colors["primary"],
                hover_color=self.colors["primary_hover"],
                width=24
            )
            cb.grid(row=0, column=0, padx=(5, 10))
            
            # Name
            name = ctk.CTkLabel(
                frame,
                text=loc["name"],
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text"]
            )
            name.grid(row=0, column=1, sticky="w")
            
            # Size
            size = ctk.CTkLabel(
                frame,
                text=loc["size_formatted"],
                font=ctk.CTkFont(size=12),
                text_color=self.colors["primary_light"]
            )
            size.grid(row=0, column=2, padx=10)
            
            self.checkboxes.append((var, loc))
            total_size += loc["size"]
        
        # Update total
        from core.disk_cleaner import format_size
        self.total_label.configure(text=f"Total: {format_size(total_size)}")
        
    def _start_cleanup(self):
        """Start cleanup process."""
        # Get selected locations
        selected = [loc for var, loc in self.checkboxes if var.get()]
        
        if not selected:
            self.show_error("No locations selected")
            return
        
        self.clean_btn.configure(state="disabled", text="Cleaning...")
        self.show_progress(True)
        
        thread = threading.Thread(target=self._do_cleanup, args=(selected,))
        thread.daemon = True
        thread.start()
        
    def _do_cleanup(self, locations):
        """Perform cleanup."""
        try:
            from core.disk_cleaner import clean_folder, format_size
            
            total = len(locations)
            total_freed = 0
            
            for i, loc in enumerate(locations):
                self.set_progress((i + 1) / total)
                self.set_status(f"Cleaning {loc['name']}...")
                
                result = clean_folder(loc["path"])
                if result["success"]:
                    total_freed += result["freed_space"]
            
            freed_str = format_size(total_freed)
            self.after(0, lambda: self._cleanup_complete(freed_str))
            
        except Exception as e:
            self.after(0, lambda: self._cleanup_error(str(e)))
            
    def _cleanup_complete(self, freed):
        """Handle cleanup completion."""
        self.show_progress(False)
        self.clean_btn.configure(state="normal", text="⚡ Clean Now")
        self.show_success(f"Freed {freed}!")
        self._scan_locations()  # Rescan
        
    def _cleanup_error(self, error):
        """Handle cleanup error."""
        self.show_progress(False)
        self.clean_btn.configure(state="normal", text="⚡ Clean Now")
        self.show_error(error)

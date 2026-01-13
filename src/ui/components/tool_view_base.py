"""
Tool View Base Component
Base class for all tool views with common functionality.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional
import threading
import os


class ToolViewBase(ctk.CTkFrame):
    """Base class for tool views with common UI elements."""
    
    def __init__(
        self,
        parent,
        title: str,
        icon: str,
        description: str,
        colors: dict,
        on_back: Optional[callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.colors = colors
        self.on_back = on_back
        self.output_path: Optional[str] = None
        
        self.configure(fg_color=colors["bg_dark"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        self._create_header(title, icon, description)
        
        # Status bar (at bottom)
        self._create_status_bar()
        
    def _create_header(self, title: str, icon: str, description: str):
        """Create the header section."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))
        header.grid_columnconfigure(1, weight=1)
        
        # Back button
        back_btn = ctk.CTkButton(
            header,
            text="← Back",
            width=80,
            height=32,
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["bg_card_hover"],
            text_color=self.colors["text"],
            command=self._go_back
        )
        back_btn.grid(row=0, column=0, sticky="w")
        
        # Title with icon
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", padx=(20, 0))
        
        icon_label = ctk.CTkLabel(
            title_frame,
            text=icon,
            font=ctk.CTkFont(size=28),
            text_color=self.colors["primary_light"]
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=self.colors["text"]
        )
        title_label.pack(side="left")
        
        # Description
        desc_label = ctk.CTkLabel(
            self,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors["text_secondary"]
        )
        desc_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))
        
    def _create_status_bar(self):
        """Create the status bar at bottom."""
        self.status_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_card"], height=50)
        self.status_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 10))
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors["text_secondary"]
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=10)
        
        # Progress bar (hidden initially)
        self.progress = ctk.CTkProgressBar(
            self.status_frame,
            progress_color=self.colors["primary"],
            fg_color=self.colors["bg_dark"]
        )
        self.progress.set(0)
        # Don't show initially
        
    def _go_back(self):
        """Go back to tool selection."""
        if self.on_back:
            self.on_back()
            
    def set_status(self, text: str, color: Optional[str] = None):
        """Update status message."""
        self.status_label.configure(
            text=text,
            text_color=color or self.colors["text_secondary"]
        )
        
    def show_progress(self, show: bool = True):
        """Show or hide progress bar."""
        if show:
            self.progress.grid(row=0, column=1, padx=15, pady=10, sticky="ew")
        else:
            self.progress.grid_forget()
            
    def set_progress(self, value: float):
        """Set progress bar value (0.0 to 1.0)."""
        self.progress.set(value)
        
    def browse_output_folder(self) -> Optional[str]:
        """Open folder browser for output location."""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_path = folder
        return folder
    
    def run_in_thread(self, func, *args, **kwargs):
        """Run a function in a separate thread."""
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        
    def show_success(self, message: str):
        """Show success message."""
        self.set_status(f"✓ {message}", self.colors["success"])
        
    def show_error(self, message: str):
        """Show error message."""
        self.set_status(f"✗ {message}", self.colors["error"])
        messagebox.showerror("Error", message)

"""
File Drop Zone Component
A drag-and-drop area for file selection.
"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional, List
import os


class FileDropZone(ctk.CTkFrame):
    """A drag-and-drop zone for file selection."""
    
    def __init__(
        self,
        parent,
        colors: dict,
        file_types: List[tuple] = None,
        multiple: bool = False,
        on_files_selected: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.colors = colors
        self.file_types = file_types or [("All files", "*.*")]
        self.multiple = multiple
        self.on_files_selected = on_files_selected
        self.selected_files: List[str] = []
        
        # Configure
        self.configure(
            fg_color=colors["bg_card"],
            corner_radius=12,
            border_width=2,
            border_color=colors["primary"]
        )
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Content frame
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=0, padx=40, pady=40)
        
        # Icon
        self.icon = ctk.CTkLabel(
            self.content,
            text="📁",
            font=ctk.CTkFont(size=48),
            text_color=colors["primary_light"]
        )
        self.icon.pack(pady=(0, 10))
        
        # Main text
        self.main_text = ctk.CTkLabel(
            self.content,
            text="Drag files here",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=colors["text"]
        )
        self.main_text.pack()
        
        # Sub text
        self.sub_text = ctk.CTkLabel(
            self.content,
            text="or click to browse",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=colors["text_secondary"]
        )
        self.sub_text.pack()
        
        # File count label (hidden initially)
        self.file_count = ctk.CTkLabel(
            self.content,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=colors["success"]
        )
        self.file_count.pack(pady=(10, 0))
        
        # Bind events
        self._bind_events()
        
    def _bind_events(self):
        """Bind click events."""
        widgets = [self, self.content, self.icon, self.main_text, self.sub_text]
        for widget in widgets:
            widget.bind("<Button-1>", self._browse_files)
            widget.configure(cursor="hand2")
            
    def _browse_files(self, event=None):
        """Open file browser dialog."""
        if self.multiple:
            files = filedialog.askopenfilenames(
                title="Select files",
                filetypes=self.file_types
            )
            if files:
                self.selected_files = list(files)
        else:
            file = filedialog.askopenfilename(
                title="Select file",
                filetypes=self.file_types
            )
            if file:
                self.selected_files = [file]
                
        self._update_display()
        
        if self.selected_files and self.on_files_selected:
            self.on_files_selected(self.selected_files)
            
    def _update_display(self):
        """Update the display after file selection."""
        if self.selected_files:
            count = len(self.selected_files)
            if count == 1:
                filename = os.path.basename(self.selected_files[0])
                self.file_count.configure(text=f"✓ {filename}")
            else:
                self.file_count.configure(text=f"✓ {count} files selected")
            self.configure(border_color=self.colors["success"])
        else:
            self.file_count.configure(text="")
            self.configure(border_color=self.colors["primary"])
            
    def get_files(self) -> List[str]:
        """Get selected files."""
        return self.selected_files
    
    def clear(self):
        """Clear selected files."""
        self.selected_files = []
        self._update_display()

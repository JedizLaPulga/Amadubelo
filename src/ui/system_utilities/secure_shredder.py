"""
Secure Shredder View
Permanently delete files.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from ui.components.tool_view_base import ToolViewBase
from ui.components.file_drop_zone import FileDropZone


class SecureShredderView(ToolViewBase):
    """View for secure file deletion."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Secure Shredder",
            icon="🔒",
            description="Permanently delete files by overwriting them with random data (unrecoverable)",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.selected_files = []
        self._create_content()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        
        # Warning
        warning_frame = ctk.CTkFrame(content, fg_color="#7f1d1d", corner_radius=10)
        warning_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        warning = ctk.CTkLabel(
            warning_frame,
            text="⚠️ WARNING: Shredded files CANNOT be recovered! Make sure you have backups.",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#fecaca"
        )
        warning.grid(row=0, column=0, padx=15, pady=15)
        
        # File drop zone
        self.drop_zone = FileDropZone(
            content,
            colors=self.colors,
            file_types=[("All files", "*.*")],
            multiple=True,
            on_files_selected=self._on_files_selected
        )
        self.drop_zone.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Security level
        level_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        level_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        level_frame.grid_columnconfigure(1, weight=1)
        
        level_label = ctk.CTkLabel(
            level_frame,
            text="Security Level:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        level_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.level_var = ctk.StringVar(value="3")
        levels_frame = ctk.CTkFrame(level_frame, fg_color="transparent")
        levels_frame.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        
        levels = [
            ("Quick (1 pass)", "1"),
            ("Standard (3 passes)", "3"),
            ("Thorough (7 passes)", "7"),
        ]
        
        for text, value in levels:
            radio = ctk.CTkRadioButton(
                levels_frame,
                text=text,
                variable=self.level_var,
                value=value,
                fg_color=self.colors["primary"],
                hover_color=self.colors["primary_hover"],
                text_color=self.colors["text"]
            )
            radio.pack(side="left", padx=(0, 20))
        
        # Shred button
        self.shred_btn = ctk.CTkButton(
            content,
            text="🔥 Shred Files Permanently",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            text_color=self.colors["text"],
            command=self._start_shred
        )
        self.shred_btn.grid(row=3, column=0, sticky="ew")
        
    def _on_files_selected(self, files):
        """Handle files selection."""
        self.selected_files = files
        self.set_status(f"Selected {len(files)} files for shredding")
            
    def _start_shred(self):
        """Start shredding process."""
        if not self.selected_files:
            self.show_error("Please select files first")
            return
        
        # Confirm
        if not messagebox.askyesno(
            "⚠️ Confirm Permanent Deletion",
            f"Are you sure you want to PERMANENTLY DELETE {len(self.selected_files)} files?\n\n"
            "This action CANNOT be undone!"
        ):
            return
        
        self.shred_btn.configure(state="disabled", text="Shredding...")
        self.show_progress(True)
        
        thread = threading.Thread(target=self._do_shred)
        thread.daemon = True
        thread.start()
        
    def _do_shred(self):
        """Perform shredding."""
        try:
            from core.file_shredder import shred_files
            
            passes = int(self.level_var.get())
            
            def progress(current, total, filename):
                self.set_progress(current / total)
                self.set_status(f"Shredding: {filename}")
            
            result = shred_files(self.selected_files, passes, progress)
            
            self.after(0, lambda: self._shred_complete(result))
            
        except Exception as e:
            self.after(0, lambda: self._shred_error(str(e)))
            
    def _shred_complete(self, result):
        """Handle shred completion."""
        self.show_progress(False)
        self.shred_btn.configure(state="normal", text="🔥 Shred Files Permanently")
        self.drop_zone.clear()
        self.selected_files = []
        
        if result["failed"] > 0:
            self.show_error(f"Shredded {result['success']}, failed {result['failed']}")
        else:
            self.show_success(f"Permanently deleted {result['success']} files!")
        
    def _shred_error(self, error):
        """Handle shred error."""
        self.show_progress(False)
        self.shred_btn.configure(state="normal", text="🔥 Shred Files Permanently")
        self.show_error(error)

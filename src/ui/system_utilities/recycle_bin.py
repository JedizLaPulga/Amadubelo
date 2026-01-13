"""
Recycle Bin View
Empty recycle bin.
"""

import customtkinter as ctk
import threading
from tkinter import messagebox
from ui.components.tool_view_base import ToolViewBase
import send2trash
import os


class RecycleBinView(ToolViewBase):
    """View for recycle bin operations."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Recycle Bin",
            icon="🗑️",
            description="Empty the Windows Recycle Bin to free up disk space",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self._create_content()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        
        # Big recycle bin display
        bin_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=15)
        bin_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        bin_frame.grid_columnconfigure(0, weight=1)
        
        # Icon
        self.bin_icon = ctk.CTkLabel(
            bin_frame,
            text="🗑️",
            font=ctk.CTkFont(size=100),
            text_color=self.colors["primary_light"]
        )
        self.bin_icon.grid(row=0, column=0, pady=(40, 20))
        
        # Info text
        self.info_label = ctk.CTkLabel(
            bin_frame,
            text="Click the button below to empty your Recycle Bin",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        self.info_label.grid(row=1, column=0, pady=(0, 40))
        
        # Warning
        warning_frame = ctk.CTkFrame(content, fg_color="#7f1d1d", corner_radius=10)
        warning_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        warning = ctk.CTkLabel(
            warning_frame,
            text="⚠️ This action is permanent. All items in the Recycle Bin will be deleted.",
            font=ctk.CTkFont(size=12),
            text_color="#fecaca"
        )
        warning.grid(row=0, column=0, padx=15, pady=15)
        
        # Empty button
        self.empty_btn = ctk.CTkButton(
            content,
            text="🗑️ Empty Recycle Bin",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            text_color=self.colors["text"],
            command=self._empty_bin
        )
        self.empty_btn.grid(row=2, column=0, sticky="ew")
        
    def _empty_bin(self):
        """Empty the recycle bin."""
        if not messagebox.askyesno(
            "Confirm",
            "Are you sure you want to permanently empty the Recycle Bin?\n\n"
            "This action cannot be undone."
        ):
            return
        
        self.empty_btn.configure(state="disabled", text="Emptying...")
        self.show_progress(True)
        self.set_progress(0.5)
        
        thread = threading.Thread(target=self._do_empty)
        thread.daemon = True
        thread.start()
        
    def _do_empty(self):
        """Perform emptying."""
        try:
            import subprocess
            
            # Use PowerShell to empty recycle bin
            result = subprocess.run(
                ["powershell", "-Command", "Clear-RecycleBin", "-Force"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.after(0, self._empty_complete)
            else:
                # Try alternative method
                self.after(0, self._empty_complete)
                
        except Exception as e:
            self.after(0, lambda: self._empty_error(str(e)))
            
    def _empty_complete(self):
        """Handle completion."""
        self.show_progress(False)
        self.empty_btn.configure(state="normal", text="🗑️ Empty Recycle Bin")
        self.bin_icon.configure(text="✨")
        self.info_label.configure(text="Recycle Bin has been emptied!")
        self.show_success("Recycle Bin emptied!")
        
        # Reset icon after a few seconds
        self.after(3000, lambda: self.bin_icon.configure(text="🗑️"))
        self.after(3000, lambda: self.info_label.configure(
            text="Click the button below to empty your Recycle Bin"
        ))
        
    def _empty_error(self, error):
        """Handle error."""
        self.show_progress(False)
        self.empty_btn.configure(state="normal", text="🗑️ Empty Recycle Bin")
        self.show_error(f"Failed: {error}")

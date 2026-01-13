"""
Duplicate Finder View  
Find duplicate files.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from ui.components.tool_view_base import ToolViewBase


class DuplicateFinderView(ToolViewBase):
    """View for finding duplicate files."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Duplicate Finder",
            icon="📁",
            description="Find duplicate files to free up disk space",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.folder_path = None
        self.duplicates = {}
        self._create_content()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        
        # Folder selection
        folder_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        folder_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        folder_frame.grid_columnconfigure(1, weight=1)
        
        folder_label = ctk.CTkLabel(
            folder_frame,
            text="Scan Folder:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        folder_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame,
            placeholder_text="Select folder to scan...",
            fg_color=self.colors["bg_dark"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        self.folder_entry.grid(row=0, column=1, padx=(0, 10), pady=15, sticky="ew")
        
        browse_btn = ctk.CTkButton(
            folder_frame,
            text="Browse",
            width=80,
            fg_color=self.colors["bg_card_hover"],
            hover_color=self.colors["primary"],
            command=self._browse_folder
        )
        browse_btn.grid(row=0, column=2, padx=(0, 10), pady=15)
        
        self.scan_btn = ctk.CTkButton(
            folder_frame,
            text="Scan",
            width=80,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._start_scan
        )
        self.scan_btn.grid(row=0, column=3, padx=(0, 15), pady=15)
        
        # Results frame
        self.results_frame = ctk.CTkScrollableFrame(
            content,
            fg_color=self.colors["bg_card"],
            corner_radius=10
        )
        self.results_frame.grid(row=1, column=0, sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder
        self.placeholder = ctk.CTkLabel(
            self.results_frame,
            text="Select a folder and click Scan to find duplicates",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_secondary"]
        )
        self.placeholder.grid(row=0, column=0, pady=50)
        
        # Stats label
        self.stats_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["primary_light"]
        )
        self.stats_label.grid(row=2, column=0, pady=10)
        
    def _browse_folder(self):
        """Browse for folder."""
        folder = filedialog.askdirectory(title="Select folder to scan")
        if folder:
            self.folder_path = folder
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            
    def _start_scan(self):
        """Start scanning for duplicates."""
        if not self.folder_entry.get():
            self.show_error("Please select a folder first")
            return
            
        self.folder_path = self.folder_entry.get()
        
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.show_progress(True)
        self.placeholder.grid()
        self.placeholder.configure(text="Scanning...")
        
        # Clear results
        for widget in self.results_frame.winfo_children():
            if widget != self.placeholder:
                widget.destroy()
        
        thread = threading.Thread(target=self._do_scan)
        thread.daemon = True
        thread.start()
        
    def _do_scan(self):
        """Perform the scan."""
        try:
            from core.duplicate_finder import find_duplicates, get_duplicate_stats
            
            def progress(current, total, filename):
                self.set_progress(current / total)
                self.set_status(f"Checking: {filename[:40]}...")
            
            self.duplicates = find_duplicates(
                self.folder_path,
                recursive=True,
                progress_callback=progress
            )
            
            stats = get_duplicate_stats(self.duplicates)
            
            self.after(0, lambda: self._display_results(stats))
            
        except Exception as e:
            self.after(0, lambda: self._scan_error(str(e)))
            
    def _display_results(self, stats):
        """Display scan results."""
        self.show_progress(False)
        self.scan_btn.configure(state="normal", text="Scan")
        self.placeholder.grid_remove()
        
        if not self.duplicates:
            self.placeholder.configure(text="🎉 No duplicates found!")
            self.placeholder.grid()
            self.stats_label.configure(text="")
            return
        
        # Stats
        self.stats_label.configure(
            text=f"Found {stats['groups']} groups of duplicates • "
                 f"{stats['duplicate_files']} duplicate files • "
                 f"Wasted space: {stats['wasted_space_formatted']}"
        )
        
        # Display groups
        row = 0
        for hash_val, files in list(self.duplicates.items())[:20]:  # Limit display
            group_frame = ctk.CTkFrame(
                self.results_frame,
                fg_color=self.colors["bg_dark"],
                corner_radius=8
            )
            group_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
            group_frame.grid_columnconfigure(0, weight=1)
            
            # Group header
            try:
                size = os.path.getsize(files[0])
                from core.duplicate_finder import format_size
                size_str = format_size(size)
            except:
                size_str = "Unknown"
                
            header = ctk.CTkLabel(
                group_frame,
                text=f"📄 {len(files)} identical files • {size_str} each",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["primary_light"]
            )
            header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
            
            # File list
            for i, filepath in enumerate(files):
                file_label = ctk.CTkLabel(
                    group_frame,
                    text=filepath,
                    font=ctk.CTkFont(size=11),
                    text_color=self.colors["text_secondary"],
                    anchor="w"
                )
                file_label.grid(row=i+1, column=0, padx=20, pady=2, sticky="w")
            
            row += 1
            
        self.set_status(f"Found {stats['groups']} duplicate groups")
        
    def _scan_error(self, error):
        """Handle scan error."""
        self.show_progress(False)
        self.scan_btn.configure(state="normal", text="Scan")
        self.show_error(error)

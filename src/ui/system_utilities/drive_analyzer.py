"""
Drive Analyzer View
Analyze disk space usage.
"""

import customtkinter as ctk
from tkinter import filedialog
import threading
from ui.components.tool_view_base import ToolViewBase


class DriveAnalyzerView(ToolViewBase):
    """View for drive space analysis."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Drive Analyzer",
            icon="💾",
            description="Analyze disk space usage and find large files/folders",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.folder_path = None
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
            text="Analyze:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        folder_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame,
            placeholder_text="Select folder or drive to analyze...",
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
        
        self.analyze_btn = ctk.CTkButton(
            folder_frame,
            text="Analyze",
            width=80,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._start_analyze
        )
        self.analyze_btn.grid(row=0, column=3, padx=(0, 15), pady=15)
        
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
            text="Select a folder or drive and click Analyze",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_secondary"]
        )
        self.placeholder.grid(row=0, column=0, pady=50)
        
        # Total size label
        self.total_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["primary_light"]
        )
        self.total_label.grid(row=2, column=0, pady=10)
        
    def _browse_folder(self):
        """Browse for folder."""
        folder = filedialog.askdirectory(title="Select folder to analyze")
        if folder:
            self.folder_path = folder
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            
    def _start_analyze(self):
        """Start analysis."""
        if not self.folder_entry.get():
            self.show_error("Please select a folder first")
            return
            
        self.folder_path = self.folder_entry.get()
        
        self.analyze_btn.configure(state="disabled", text="Analyzing...")
        self.show_progress(True)
        self.placeholder.configure(text="Analyzing...")
        
        # Clear results
        for widget in self.results_frame.winfo_children():
            if widget != self.placeholder:
                widget.destroy()
        
        thread = threading.Thread(target=self._do_analyze)
        thread.daemon = True
        thread.start()
        
    def _do_analyze(self):
        """Perform analysis."""
        try:
            from core.drive_analyzer import analyze_folder
            
            def progress(current_folder):
                self.set_status(f"Scanning: {current_folder[:50]}...")
            
            result = analyze_folder(self.folder_path, progress_callback=progress)
            
            self.after(0, lambda: self._display_results(result))
            
        except Exception as e:
            self.after(0, lambda: self._analyze_error(str(e)))
            
    def _display_results(self, result):
        """Display analysis results."""
        self.show_progress(False)
        self.analyze_btn.configure(state="normal", text="Analyze")
        self.placeholder.grid_remove()
        
        if "error" in result:
            self.show_error(result["error"])
            return
        
        # Total size
        self.total_label.configure(
            text=f"Total Size: {result.get('total_size_formatted', 'Unknown')} • "
                 f"{result.get('file_count', 0)} files • "
                 f"{result.get('folder_count', 0)} folders"
        )
        
        # Display children (folders by size)
        children = result.get("children", [])
        
        for i, child in enumerate(children[:20]):  # Limit display
            self._create_folder_bar(i, child, result.get("total_size", 1))
        
        self.set_status("Analysis complete")
        
    def _create_folder_bar(self, row: int, child: dict, total_size: int):
        """Create a folder size bar."""
        frame = ctk.CTkFrame(
            self.results_frame,
            fg_color="transparent",
            height=40
        )
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=3)
        frame.grid_columnconfigure(1, weight=1)
        
        # Folder icon and name
        name = child.get("name", "Unknown")
        name_label = ctk.CTkLabel(
            frame,
            text=f"📁 {name}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text"],
            anchor="w",
            width=200
        )
        name_label.grid(row=0, column=0, sticky="w")
        
        # Progress bar showing percentage
        percent = child.get("percent", 0)
        progress = ctk.CTkProgressBar(
            frame,
            progress_color=self.colors["primary"],
            fg_color=self.colors["bg_dark"],
            height=12
        )
        progress.set(percent / 100)
        progress.grid(row=0, column=1, sticky="ew", padx=10)
        
        # Size
        size_label = ctk.CTkLabel(
            frame,
            text=f"{child.get('size_formatted', '?')} ({percent:.1f}%)",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["primary_light"],
            width=120
        )
        size_label.grid(row=0, column=2, sticky="e")
        
    def _analyze_error(self, error):
        """Handle analysis error."""
        self.show_progress(False)
        self.analyze_btn.configure(state="normal", text="Analyze")
        self.show_error(error)

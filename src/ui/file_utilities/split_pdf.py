"""
Split PDF View
Split a PDF into separate files.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from ui.components.tool_view_base import ToolViewBase
from ui.components.file_drop_zone import FileDropZone


class SplitPdfView(ToolViewBase):
    """View for splitting PDFs."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Split PDF",
            icon="✂️",
            description="Extract pages from a PDF into separate files",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.selected_file = None
        self.pdf_info = None
        
        self._create_content()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        
        # File drop zone
        self.drop_zone = FileDropZone(
            content,
            colors=self.colors,
            file_types=[("PDF files", "*.pdf")],
            multiple=False,
            on_files_selected=self._on_file_selected
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # PDF info frame
        self.info_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        self.info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.info_frame.grid_columnconfigure(1, weight=1)
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Select a PDF to see page count",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_secondary"]
        )
        self.info_label.grid(row=0, column=0, padx=15, pady=15)
        
        # Split mode selection
        mode_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        mode_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        mode_frame.grid_columnconfigure(1, weight=1)
        
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="Split Mode:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        mode_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.mode_var = ctk.StringVar(value="all")
        modes_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        modes_frame.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        
        all_radio = ctk.CTkRadioButton(
            modes_frame,
            text="All pages (separate files)",
            variable=self.mode_var,
            value="all",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"]
        )
        all_radio.pack(side="left", padx=(0, 20))
        
        range_radio = ctk.CTkRadioButton(
            modes_frame,
            text="Page range",
            variable=self.mode_var,
            value="range",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"]
        )
        range_radio.pack(side="left")
        
        # Page range input
        range_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        range_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        range_frame.grid_columnconfigure(1, weight=1)
        
        range_label = ctk.CTkLabel(
            range_frame,
            text="Page Range:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        range_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.range_entry = ctk.CTkEntry(
            range_frame,
            placeholder_text="e.g., 1-5 or 1,3,5-10",
            fg_color=self.colors["bg_dark"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        self.range_entry.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="ew")
        
        # Output folder selection
        output_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        output_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        output_frame.grid_columnconfigure(1, weight=1)
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Output Folder:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        output_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            placeholder_text="Select output folder...",
            fg_color=self.colors["bg_dark"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        self.output_entry.grid(row=0, column=1, padx=(0, 10), pady=15, sticky="ew")
        
        browse_btn = ctk.CTkButton(
            output_frame,
            text="Browse",
            width=80,
            fg_color=self.colors["bg_card_hover"],
            hover_color=self.colors["primary"],
            text_color=self.colors["text"],
            command=self._browse_output
        )
        browse_btn.grid(row=0, column=2, padx=(0, 15), pady=15)
        
        # Split button
        self.split_btn = ctk.CTkButton(
            content,
            text="⚡ Split PDF",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._start_split
        )
        self.split_btn.grid(row=5, column=0, sticky="ew")
        
    def _on_file_selected(self, files):
        """Handle file selection."""
        if files:
            self.selected_file = files[0]
            self.set_status(f"Selected: {os.path.basename(self.selected_file)}")
            
            # Get PDF info
            try:
                from core.pdf_tools import get_pdf_info
                self.pdf_info = get_pdf_info(self.selected_file)
                self.info_label.configure(
                    text=f"📄 {self.pdf_info['pages']} pages",
                    text_color=self.colors["success"]
                )
            except Exception as e:
                self.info_label.configure(
                    text=f"Error reading PDF",
                    text_color=self.colors["error"]
                )
            
    def _browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder)
            
    def _start_split(self):
        """Start the split process."""
        if not self.selected_file:
            self.show_error("Please select a PDF file first")
            return
            
        output_folder = self.output_entry.get()
        if not output_folder:
            self.show_error("Please select an output folder")
            return
        
        self.split_btn.configure(state="disabled", text="Splitting...")
        self.show_progress(True)
        self.set_status("Splitting PDF...")
        
        # Run in thread
        thread = threading.Thread(target=self._do_split, args=(output_folder,))
        thread.daemon = True
        thread.start()
        
    def _do_split(self, output_folder):
        """Perform the actual split."""
        try:
            from core.pdf_tools import split_pdf
            
            page_ranges = None
            if self.mode_var.get() == "range":
                # Parse page range
                range_str = self.range_entry.get().strip()
                if range_str:
                    page_ranges = self._parse_range(range_str)
            
            def progress(current, total):
                self.set_progress(current / total)
                self.set_status(f"Extracting page {current} of {total}...")
            
            output_files = split_pdf(
                self.selected_file,
                output_folder,
                page_ranges=page_ranges,
                progress_callback=progress
            )
            
            self.after(0, lambda: self._split_complete(len(output_files)))
            
        except Exception as e:
            self.after(0, lambda: self._split_error(str(e)))
            
    def _parse_range(self, range_str: str):
        """Parse page range string like '1-5,7,10-12'."""
        ranges = []
        parts = range_str.replace(' ', '').split(',')
        
        for part in parts:
            if '-' in part:
                start, end = part.split('-')
                ranges.append((int(start), int(end)))
            else:
                page = int(part)
                ranges.append((page, page))
        
        return ranges
            
    def _split_complete(self, count):
        """Handle split completion."""
        self.show_progress(False)
        self.split_btn.configure(state="normal", text="⚡ Split PDF")
        self.show_success(f"Created {count} PDF files!")
        
    def _split_error(self, error):
        """Handle split error."""
        self.show_progress(False)
        self.split_btn.configure(state="normal", text="⚡ Split PDF")
        self.show_error(f"Failed: {error}")

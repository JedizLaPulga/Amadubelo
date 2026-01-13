"""
Merge PDF View
Merge multiple PDFs into one.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from ui.components.tool_view_base import ToolViewBase
from ui.components.file_drop_zone import FileDropZone


class MergePdfView(ToolViewBase):
    """View for merging PDFs."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Merge PDFs",
            icon="🔗",
            description="Combine multiple PDF files into a single document",
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
        
        # File drop zone
        self.drop_zone = FileDropZone(
            content,
            colors=self.colors,
            file_types=[("PDF files", "*.pdf")],
            multiple=True,
            on_files_selected=self._on_files_selected
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Files list
        list_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        list_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        list_frame.grid_columnconfigure(0, weight=1)
        
        list_label = ctk.CTkLabel(
            list_frame,
            text="Selected Files (in order):",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        list_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.files_textbox = ctk.CTkTextbox(
            list_frame,
            height=100,
            fg_color=self.colors["bg_dark"],
            text_color=self.colors["text_secondary"],
            state="disabled"
        )
        self.files_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # Output file selection
        output_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        output_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        output_frame.grid_columnconfigure(1, weight=1)
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Save As:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        output_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            placeholder_text="Select output file...",
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
        
        # Merge button
        self.merge_btn = ctk.CTkButton(
            content,
            text="⚡ Merge PDFs",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._start_merge
        )
        self.merge_btn.grid(row=3, column=0, sticky="ew")
        
    def _on_files_selected(self, files):
        """Handle files selection."""
        self.selected_files = files
        self.set_status(f"Selected {len(files)} PDFs")
        
        # Update textbox
        self.files_textbox.configure(state="normal")
        self.files_textbox.delete("1.0", "end")
        for i, f in enumerate(files, 1):
            self.files_textbox.insert("end", f"{i}. {os.path.basename(f)}\n")
        self.files_textbox.configure(state="disabled")
            
    def _browse_output(self):
        """Browse for output file."""
        file = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def _start_merge(self):
        """Start the merge process."""
        if len(self.selected_files) < 2:
            self.show_error("Please select at least 2 PDF files")
            return
            
        output_path = self.output_entry.get()
        if not output_path:
            self.show_error("Please specify an output file")
            return
        
        self.merge_btn.configure(state="disabled", text="Merging...")
        self.show_progress(True)
        self.set_status("Merging PDFs...")
        
        # Run in thread
        thread = threading.Thread(target=self._do_merge, args=(output_path,))
        thread.daemon = True
        thread.start()
        
    def _do_merge(self, output_path):
        """Perform the actual merge."""
        try:
            from core.pdf_tools import merge_pdfs
            
            def progress(current, total):
                self.set_progress(current / total)
                self.set_status(f"Processing PDF {current} of {total}...")
            
            merge_pdfs(self.selected_files, output_path, progress_callback=progress)
            
            self.after(0, lambda: self._merge_complete(output_path))
            
        except Exception as e:
            self.after(0, lambda: self._merge_error(str(e)))
            
    def _merge_complete(self, output_path):
        """Handle merge completion."""
        self.show_progress(False)
        self.merge_btn.configure(state="normal", text="⚡ Merge PDFs")
        self.show_success(f"Created: {os.path.basename(output_path)}")
        
    def _merge_error(self, error):
        """Handle merge error."""
        self.show_progress(False)
        self.merge_btn.configure(state="normal", text="⚡ Merge PDFs")
        self.show_error(f"Failed: {error}")

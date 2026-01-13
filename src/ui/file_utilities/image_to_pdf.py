"""
Image to PDF View
Combine images into a PDF.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from ui.components.tool_view_base import ToolViewBase
from ui.components.file_drop_zone import FileDropZone


class ImageToPdfView(ToolViewBase):
    """View for combining images into PDF."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Images to PDF",
            icon="🖼️",
            description="Combine multiple images into a single PDF document",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.selected_files = []
        self.output_folder = None
        
        self._create_content()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        
        # File drop zone (multiple files)
        self.drop_zone = FileDropZone(
            content,
            colors=self.colors,
            file_types=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
            ],
            multiple=True,
            on_files_selected=self._on_files_selected
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Options frame
        options_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Page size selection
        size_label = ctk.CTkLabel(
            options_frame,
            text="Page Size:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        size_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.size_var = ctk.StringVar(value="A4")
        size_menu = ctk.CTkSegmentedButton(
            options_frame,
            values=["A4", "letter"],
            variable=self.size_var,
            fg_color=self.colors["bg_dark"],
            selected_color=self.colors["primary"],
            selected_hover_color=self.colors["primary_hover"],
            unselected_color=self.colors["bg_dark"],
            unselected_hover_color=self.colors["bg_card_hover"]
        )
        size_menu.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        
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
        
        # Convert button
        self.convert_btn = ctk.CTkButton(
            content,
            text="⚡ Create PDF",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._start_conversion
        )
        self.convert_btn.grid(row=3, column=0, sticky="ew")
        
    def _on_files_selected(self, files):
        """Handle files selection."""
        self.selected_files = files
        self.set_status(f"Selected {len(files)} images")
            
    def _browse_output(self):
        """Browse for output file."""
        file = filedialog.asksaveasfilename(
            title="Save PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file:
            self.output_path = file
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def _start_conversion(self):
        """Start the conversion process."""
        if not self.selected_files:
            self.show_error("Please select images first")
            return
            
        output_path = self.output_entry.get()
        if not output_path:
            self.show_error("Please specify an output file")
            return
        
        self.convert_btn.configure(state="disabled", text="Creating PDF...")
        self.show_progress(True)
        self.set_status("Creating PDF from images...")
        
        # Run in thread
        thread = threading.Thread(target=self._do_conversion, args=(output_path,))
        thread.daemon = True
        thread.start()
        
    def _do_conversion(self, output_path):
        """Perform the actual conversion."""
        try:
            from core.file_converters import images_to_pdf
            
            def progress(current, total):
                self.set_progress(current / total)
                self.set_status(f"Processing image {current} of {total}...")
            
            images_to_pdf(
                self.selected_files,
                output_path,
                page_size=self.size_var.get(),
                progress_callback=progress
            )
            
            # Update UI on main thread
            self.after(0, lambda: self._conversion_complete(output_path))
            
        except Exception as e:
            self.after(0, lambda: self._conversion_error(str(e)))
            
    def _conversion_complete(self, output_path):
        """Handle conversion completion."""
        self.show_progress(False)
        self.convert_btn.configure(state="normal", text="⚡ Create PDF")
        self.show_success(f"Created: {os.path.basename(output_path)}")
        
    def _conversion_error(self, error):
        """Handle conversion error."""
        self.show_progress(False)
        self.convert_btn.configure(state="normal", text="⚡ Create PDF")
        self.show_error(f"Failed: {error}")

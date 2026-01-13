"""
DOCX to PDF View
Convert Word documents to PDF.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from ui.components.tool_view_base import ToolViewBase
from ui.components.file_drop_zone import FileDropZone


class DocxToPdfView(ToolViewBase):
    """View for DOCX to PDF conversion."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="DOCX to PDF",
            icon="📝",
            description="Convert Word documents (.docx) to PDF format",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.selected_file = None
        self.output_folder = None
        
        self._create_content()
        
    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        
        # File drop zone
        self.drop_zone = FileDropZone(
            content,
            colors=self.colors,
            file_types=[("Word documents", "*.docx")],
            multiple=False,
            on_files_selected=self._on_file_selected
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Output folder selection
        output_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        output_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
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
        
        # Note about conversion
        note_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        note_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        note_label = ctk.CTkLabel(
            note_frame,
            text="ℹ️ Note: This extracts text from DOCX and creates a formatted PDF.\n"
                 "   Complex formatting may not be preserved.",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"],
            justify="left"
        )
        note_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Convert button
        self.convert_btn = ctk.CTkButton(
            content,
            text="⚡ Convert to PDF",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._start_conversion
        )
        self.convert_btn.grid(row=3, column=0, sticky="ew")
        
    def _on_file_selected(self, files):
        """Handle file selection."""
        if files:
            self.selected_file = files[0]
            self.set_status(f"Selected: {os.path.basename(self.selected_file)}")
            
    def _browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_folder = folder
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder)
            
    def _start_conversion(self):
        """Start the conversion process."""
        if not self.selected_file:
            self.show_error("Please select a DOCX file first")
            return
            
        if not self.output_folder:
            self.show_error("Please select an output folder")
            return
        
        self.convert_btn.configure(state="disabled", text="Converting...")
        self.show_progress(True)
        self.set_progress(0.5)  # Indeterminate
        self.set_status("Converting DOCX to PDF...")
        
        # Run in thread
        thread = threading.Thread(target=self._do_conversion)
        thread.daemon = True
        thread.start()
        
    def _do_conversion(self):
        """Perform the actual conversion."""
        try:
            from core.file_converters import docx_to_pdf
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(self.selected_file))[0]
            output_path = os.path.join(self.output_folder, f"{base_name}.pdf")
            
            docx_to_pdf(self.selected_file, output_path)
            
            # Update UI on main thread
            self.after(0, lambda: self._conversion_complete(output_path))
            
        except Exception as e:
            self.after(0, lambda: self._conversion_error(str(e)))
            
    def _conversion_complete(self, output_path):
        """Handle conversion completion."""
        self.show_progress(False)
        self.convert_btn.configure(state="normal", text="⚡ Convert to PDF")
        self.show_success(f"Created: {os.path.basename(output_path)}")
        
    def _conversion_error(self, error):
        """Handle conversion error."""
        self.show_progress(False)
        self.convert_btn.configure(state="normal", text="⚡ Convert to PDF")
        self.show_error(f"Conversion failed: {error}")

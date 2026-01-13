"""
PDF to Image View
Convert PDF pages to images.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from ui.components.tool_view_base import ToolViewBase
from ui.components.file_drop_zone import FileDropZone


class PdfToImageView(ToolViewBase):
    """View for PDF to Image conversion."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="PDF to Images",
            icon="📄",
            description="Convert each page of a PDF to an image file (PNG or JPG)",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.selected_file = None
        self.output_folder = None
        
        self._create_content()
        
    def _create_content(self):
        """Create the main content area."""
        # Use scrollable frame to ensure all content is accessible
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        
        # Main layout frame
        main_frame = ctk.CTkFrame(content, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="ew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # File drop zone
        self.drop_zone = FileDropZone(
            main_frame,
            colors=self.colors,
            file_types=[("PDF files", "*.pdf")],
            multiple=False,
            on_files_selected=self._on_file_selected
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Options frame
        options_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["bg_card"], corner_radius=10)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Format selection
        format_label = ctk.CTkLabel(
            options_frame,
            text="Output Format:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        format_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.format_var = ctk.StringVar(value="png")
        format_menu = ctk.CTkSegmentedButton(
            options_frame,
            values=["png", "jpg"],
            variable=self.format_var,
            fg_color=self.colors["bg_dark"],
            selected_color=self.colors["primary"],
            selected_hover_color=self.colors["primary_hover"],
            unselected_color=self.colors["bg_dark"],
            unselected_hover_color=self.colors["bg_card_hover"]
        )
        format_menu.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        
        # DPI selection
        dpi_label = ctk.CTkLabel(
            options_frame,
            text="Quality (DPI):",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        dpi_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
        
        self.dpi_var = ctk.StringVar(value="200")
        dpi_menu = ctk.CTkSegmentedButton(
            options_frame,
            values=["100", "150", "200", "300"],
            variable=self.dpi_var,
            fg_color=self.colors["bg_dark"],
            selected_color=self.colors["primary"],
            selected_hover_color=self.colors["primary_hover"],
            unselected_color=self.colors["bg_dark"],
            unselected_hover_color=self.colors["bg_card_hover"]
        )
        dpi_menu.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="w")
        
        # Output folder selection
        output_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["bg_card"], corner_radius=10)
        output_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
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
        
        # Convert button
        self.convert_btn = ctk.CTkButton(
            main_frame,
            text="⚡ Convert to Images",
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
            self.show_error("Please select a PDF file first")
            return
            
        if not self.output_folder:
            self.show_error("Please select an output folder")
            return
        
        self.convert_btn.configure(state="disabled", text="Converting...")
        self.show_progress(True)
        self.set_status("Converting PDF to images...")
        
        # Run in thread
        thread = threading.Thread(target=self._do_conversion)
        thread.daemon = True
        thread.start()
        
    def _do_conversion(self):
        """Perform the actual conversion."""
        try:
            from core.file_converters import pdf_to_images
            
            def progress(current, total):
                self.set_progress(current / total)
                self.set_status(f"Converting page {current} of {total}...")
            
            output_files = pdf_to_images(
                self.selected_file,
                self.output_folder,
                format=self.format_var.get(),
                dpi=int(self.dpi_var.get()),
                progress_callback=progress
            )
            
            # Update UI on main thread
            self.after(0, lambda: self._conversion_complete(len(output_files)))
            
        except Exception as e:
            self.after(0, lambda: self._conversion_error(str(e)))
            
    def _conversion_complete(self, count):
        """Handle conversion completion."""
        self.show_progress(False)
        self.convert_btn.configure(state="normal", text="⚡ Convert to Images")
        self.show_success(f"Created {count} images!")
        
    def _conversion_error(self, error):
        """Handle conversion error."""
        self.show_progress(False)
        self.convert_btn.configure(state="normal", text="⚡ Convert to Images")
        self.show_error(f"Conversion failed: {error}")

"""
Compress View
Compress images and PDFs.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from ui.components.tool_view_base import ToolViewBase
from ui.components.file_drop_zone import FileDropZone


class CompressView(ToolViewBase):
    """View for file compression."""
    
    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Compress Files",
            icon="📉",
            description="Reduce file sizes for images and PDFs",
            colors=colors,
            on_back=on_back,
            **kwargs
        )
        
        self.selected_files = []
        
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
            file_types=[
                ("Supported files", "*.png *.jpg *.jpeg *.pdf"),
                ("Images", "*.png *.jpg *.jpeg"),
                ("PDF files", "*.pdf"),
            ],
            multiple=True,
            on_files_selected=self._on_files_selected
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Options frame
        options_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Quality slider
        quality_label = ctk.CTkLabel(
            options_frame,
            text="Quality:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        quality_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        slider_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        slider_frame.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        slider_frame.grid_columnconfigure(0, weight=1)
        
        self.quality_var = ctk.IntVar(value=70)
        self.quality_slider = ctk.CTkSlider(
            slider_frame,
            from_=10,
            to=100,
            variable=self.quality_var,
            progress_color=self.colors["primary"],
            button_color=self.colors["primary"],
            button_hover_color=self.colors["primary_hover"],
            command=self._update_quality_label
        )
        self.quality_slider.grid(row=0, column=0, sticky="ew")
        
        self.quality_value_label = ctk.CTkLabel(
            slider_frame,
            text="70%",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["primary_light"],
            width=50
        )
        self.quality_value_label.grid(row=0, column=1, padx=(10, 0))
        
        # Output folder selection
        output_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
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
        
        # Compress button
        self.compress_btn = ctk.CTkButton(
            content,
            text="⚡ Compress Files",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._start_compression
        )
        self.compress_btn.grid(row=3, column=0, sticky="ew")
        
    def _update_quality_label(self, value):
        """Update the quality label."""
        self.quality_value_label.configure(text=f"{int(value)}%")
        
    def _on_files_selected(self, files):
        """Handle files selection."""
        self.selected_files = files
        self.set_status(f"Selected {len(files)} files")
            
    def _browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder)
            
    def _start_compression(self):
        """Start the compression process."""
        if not self.selected_files:
            self.show_error("Please select files first")
            return
            
        output_folder = self.output_entry.get()
        if not output_folder:
            self.show_error("Please select an output folder")
            return
        
        self.compress_btn.configure(state="disabled", text="Compressing...")
        self.show_progress(True)
        self.set_status("Compressing files...")
        
        # Run in thread
        thread = threading.Thread(target=self._do_compression, args=(output_folder,))
        thread.daemon = True
        thread.start()
        
    def _do_compression(self, output_folder):
        """Perform the actual compression."""
        try:
            from core.file_compressor import compress_image, compress_pdf, format_file_size, calculate_savings
            
            quality = self.quality_var.get()
            total = len(self.selected_files)
            total_saved = 0
            
            for i, filepath in enumerate(self.selected_files):
                self.set_progress((i + 1) / total)
                self.set_status(f"Compressing {os.path.basename(filepath)}...")
                
                ext = os.path.splitext(filepath)[1].lower()
                
                if ext in ['.png', '.jpg', '.jpeg']:
                    base = os.path.splitext(os.path.basename(filepath))[0]
                    output_path = os.path.join(output_folder, f"{base}_compressed.jpg")
                    _, original, compressed = compress_image(filepath, output_path, quality)
                    total_saved += original - compressed
                elif ext == '.pdf':
                    base = os.path.splitext(os.path.basename(filepath))[0]
                    output_path = os.path.join(output_folder, f"{base}_compressed.pdf")
                    _, original, compressed = compress_pdf(filepath, output_path)
                    total_saved += original - compressed
            
            saved_str = format_file_size(total_saved)
            self.after(0, lambda: self._compression_complete(total, saved_str))
            
        except Exception as e:
            self.after(0, lambda: self._compression_error(str(e)))
            
    def _compression_complete(self, count, saved):
        """Handle compression completion."""
        self.show_progress(False)
        self.compress_btn.configure(state="normal", text="⚡ Compress Files")
        self.show_success(f"Compressed {count} files! Saved {saved}")
        
    def _compression_error(self, error):
        """Handle compression error."""
        self.show_progress(False)
        self.compress_btn.configure(state="normal", text="⚡ Compress Files")
        self.show_error(f"Failed: {error}")

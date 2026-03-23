"""
Image Converter View
Convert images between different formats.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from ui.components.tool_view_base import ToolViewBase
from ui.components.file_drop_zone import FileDropZone


class ImageConverterView(ToolViewBase):
    """View for image format conversion."""

    SUPPORTED_FORMATS = [
        ("PNG", "*.png"),
        ("JPEG", "*.jpg"),
        ("BMP", "*.bmp"),
        ("TIFF", "*.tiff"),
        ("GIF", "*.gif"),
        ("WEBP", "*.webp")
    ]

    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Image Converter",
            icon="🔄",
            description="Convert images between different formats",
            colors=colors,
            on_back=on_back,
            **kwargs
        )

        self.selected_files = []
        self.target_format = ctk.StringVar(value="PNG")

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
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tiff"),
                ("GIF", "*.gif"),
                ("WEBP", "*.webp"),
            ],
            multiple=True,
            on_files_selected=self._on_files_selected
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Format selection
        format_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        format_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        format_frame.grid_columnconfigure(1, weight=1)

        format_label = ctk.CTkLabel(
            format_frame,
            text="Convert to:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        format_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.format_menu = ctk.CTkOptionMenu(
            format_frame,
            values=[fmt[0] for fmt in self.SUPPORTED_FORMATS],
            variable=self.target_format,
            fg_color=self.colors["bg_dark"],
            button_color=self.colors["primary"],
            button_hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            dropdown_fg_color=self.colors["bg_card"],
            dropdown_text_color=self.colors["text"],
            dropdown_hover_color=self.colors["bg_card_hover"]
        )
        self.format_menu.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="ew")

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

        # Convert button
        self.convert_btn = ctk.CTkButton(
            content,
            text="🔄 Convert Images",
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
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder)

    def _start_conversion(self):
        """Start the conversion process."""
        if not self.selected_files:
            self.show_error("Please select image files first")
            return

        output_folder = self.output_entry.get()
        if not output_folder:
            self.show_error("Please select an output folder")
            return

        target_format = self.target_format.get().lower()
        if target_format == "jpeg":
            target_format = "jpg"

        self.convert_btn.configure(state="disabled", text="Converting...")
        self.show_progress(True)
        self.set_status("Converting images...")

        # Run in thread
        thread = threading.Thread(target=self._do_conversion, args=(output_folder, target_format))
        thread.daemon = True
        thread.start()

    def _do_conversion(self, output_folder, target_format):
        """Perform the actual conversion."""
        try:
            from PIL import Image
            import os

            total = len(self.selected_files)
            converted = 0

            for i, filepath in enumerate(self.selected_files):
                self.set_progress((i + 1) / total)
                filename = os.path.basename(filepath)
                name_without_ext = os.path.splitext(filename)[0]
                self.set_status(f"Converting {filename}...")

                try:
                    # Open image
                    with Image.open(filepath) as img:
                        # Convert to RGB if necessary (for JPEG)
                        if target_format in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')

                        # Save with new format
                        output_path = os.path.join(output_folder, f"{name_without_ext}.{target_format}")
                        img.save(output_path, target_format.upper() if target_format != 'jpg' else 'JPEG')
                        converted += 1

                except Exception as e:
                    print(f"Error converting {filename}: {e}")
                    continue

            self.after(0, lambda: self._conversion_complete(converted, total))

        except Exception as e:
            self.after(0, lambda: self._conversion_error(str(e)))

    def _conversion_complete(self, converted, total):
        """Handle conversion completion."""
        self.show_progress(False)
        self.convert_btn.configure(state="normal", text="🔄 Convert Images")
        if converted == total:
            self.show_success(f"Successfully converted {converted} images!")
        else:
            self.show_warning(f"Converted {converted} out of {total} images")

    def _conversion_error(self, error):
        """Handle conversion error."""
        self.show_progress(False)
        self.convert_btn.configure(state="normal", text="🔄 Convert Images")
        self.show_error(f"Conversion failed: {error}")
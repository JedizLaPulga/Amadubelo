"""
QR Code Generator View
Generate QR codes from text input.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from ui.components.tool_view_base import ToolViewBase


class QrGeneratorView(ToolViewBase):
    """View for QR code generation."""

    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="QR Code Generator",
            icon="📱",
            description="Generate QR codes from text or URLs",
            colors=colors,
            on_back=on_back,
            **kwargs
        )

        self.text_content = ctk.StringVar()
        self.qr_size = ctk.IntVar(value=10)  # QR code size (1-40)

        self._create_content()

    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)

        # Text input
        text_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        text_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        text_frame.grid_columnconfigure(0, weight=1)

        text_label = ctk.CTkLabel(
            text_frame,
            text="Text to encode:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text"]
        )
        text_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.text_entry = ctk.CTkTextbox(
            text_frame,
            height=100,
            fg_color=self.colors["bg_dark"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"],
            wrap="word"
        )
        self.text_entry.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Options frame
        options_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        options_frame.grid_columnconfigure(1, weight=1)

        # Size slider
        size_label = ctk.CTkLabel(
            options_frame,
            text="QR Code Size:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        size_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        size_slider_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        size_slider_frame.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        size_slider_frame.grid_columnconfigure(0, weight=1)

        self.size_slider = ctk.CTkSlider(
            size_slider_frame,
            from_=1,
            to=40,
            variable=self.qr_size,
            progress_color=self.colors["primary"],
            button_color=self.colors["primary"],
            button_hover_color=self.colors["primary_hover"],
            command=self._update_size_label
        )
        self.size_slider.grid(row=0, column=0, sticky="ew")

        self.size_value_label = ctk.CTkLabel(
            size_slider_frame,
            text="10",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["primary_light"],
            width=30
        )
        self.size_value_label.grid(row=0, column=1, padx=(10, 0))

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

        # Generate button
        self.generate_btn = ctk.CTkButton(
            content,
            text="📱 Generate QR Code",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._start_generation
        )
        self.generate_btn.grid(row=3, column=0, sticky="ew")

    def _update_size_label(self, value):
        """Update the size label."""
        self.size_value_label.configure(text=str(int(value)))

    def _browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder)

    def _start_generation(self):
        """Start the QR code generation process."""
        text = self.text_entry.get("1.0", "end-1c").strip()
        if not text:
            self.show_error("Please enter text to encode")
            return

        output_folder = self.output_entry.get()
        if not output_folder:
            self.show_error("Please select an output folder")
            return

        self.generate_btn.configure(state="disabled", text="Generating...")
        self.show_progress(True)
        self.set_status("Generating QR code...")

        # Run in thread
        thread = threading.Thread(target=self._do_generation, args=(text, output_folder))
        thread.daemon = True
        thread.start()

    def _do_generation(self, text, output_folder):
        """Perform the actual QR code generation."""
        try:
            import qrcode
            from PIL import Image

            # Create QR code
            qr = qrcode.QRCode(
                version=None,  # Auto-size
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=self.qr_size.get(),
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Save the image
            output_path = os.path.join(output_folder, "qr_code.png")
            img.save(output_path)

            self.after(0, lambda: self._generation_complete(output_path))

        except Exception as e:
            self.after(0, lambda: self._generation_error(str(e)))

    def _generation_complete(self, output_path):
        """Handle generation completion."""
        self.show_progress(False)
        self.generate_btn.configure(state="normal", text="📱 Generate QR Code")
        self.show_success(f"QR code saved to: {os.path.basename(output_path)}")

    def _generation_error(self, error):
        """Handle generation error."""
        self.show_progress(False)
        self.generate_btn.configure(state="normal", text="📱 Generate QR Code")
        self.show_error(f"Failed to generate QR code: {error}")
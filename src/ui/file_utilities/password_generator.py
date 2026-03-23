"""
Password Generator View
Generate secure passwords with customizable options.
"""

import customtkinter as ctk
import secrets
import string
import pyperclip
from ui.components.tool_view_base import ToolViewBase


class PasswordGeneratorView(ToolViewBase):
    """View for password generation."""

    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Password Generator",
            icon="🔐",
            description="Generate secure passwords with custom options",
            colors=colors,
            on_back=on_back,
            **kwargs
        )

        # Password options
        self.length = ctk.IntVar(value=16)
        self.use_uppercase = ctk.BooleanVar(value=True)
        self.use_lowercase = ctk.BooleanVar(value=True)
        self.use_digits = ctk.BooleanVar(value=True)
        self.use_symbols = ctk.BooleanVar(value=True)
        self.generated_password = ctk.StringVar()

        self._create_content()

    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)

        # Password display
        display_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        display_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        display_frame.grid_columnconfigure(0, weight=1)

        display_label = ctk.CTkLabel(
            display_frame,
            text="Generated Password:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text"]
        )
        display_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.password_entry = ctk.CTkEntry(
            display_frame,
            textvariable=self.generated_password,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["bg_dark"],
            border_color=self.colors["primary"],
            text_color=self.colors["primary_light"],
            state="readonly"
        )
        self.password_entry.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Copy button
        copy_btn = ctk.CTkButton(
            display_frame,
            text="📋 Copy",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._copy_password
        )
        copy_btn.grid(row=1, column=1, padx=(0, 15), pady=(0, 15))

        # Options frame
        options_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        # Length slider
        length_label = ctk.CTkLabel(
            options_frame,
            text="Password Length:",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"]
        )
        length_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w", columnspan=2)

        length_slider_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        length_slider_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew", columnspan=2)
        length_slider_frame.grid_columnconfigure(0, weight=1)

        self.length_slider = ctk.CTkSlider(
            length_slider_frame,
            from_=8,
            to=64,
            variable=self.length,
            progress_color=self.colors["primary"],
            button_color=self.colors["primary"],
            button_hover_color=self.colors["primary_hover"],
            command=self._update_length_label
        )
        self.length_slider.grid(row=0, column=0, sticky="ew")

        self.length_value_label = ctk.CTkLabel(
            length_slider_frame,
            text="16",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["primary_light"],
            width=30
        )
        self.length_value_label.grid(row=0, column=1, padx=(10, 0))

        # Character type checkboxes
        char_types_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        char_types_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew", columnspan=2)
        char_types_frame.grid_columnconfigure((0, 1), weight=1)

        # Uppercase
        uppercase_cb = ctk.CTkCheckBox(
            char_types_frame,
            text="Uppercase (A-Z)",
            variable=self.use_uppercase,
            text_color=self.colors["text"],
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"]
        )
        uppercase_cb.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        # Lowercase
        lowercase_cb = ctk.CTkCheckBox(
            char_types_frame,
            text="Lowercase (a-z)",
            variable=self.use_lowercase,
            text_color=self.colors["text"],
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"]
        )
        lowercase_cb.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="w")

        # Digits
        digits_cb = ctk.CTkCheckBox(
            char_types_frame,
            text="Digits (0-9)",
            variable=self.use_digits,
            text_color=self.colors["text"],
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"]
        )
        digits_cb.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")

        # Symbols
        symbols_cb = ctk.CTkCheckBox(
            char_types_frame,
            text="Symbols (!@#$%)",
            variable=self.use_symbols,
            text_color=self.colors["text"],
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"]
        )
        symbols_cb.grid(row=1, column=1, padx=(10, 0), pady=5, sticky="w")

        # Generate button
        self.generate_btn = ctk.CTkButton(
            content,
            text="🔐 Generate Password",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._generate_password
        )
        self.generate_btn.grid(row=2, column=0, sticky="ew")

        # Generate initial password
        self._generate_password()

    def _update_length_label(self, value):
        """Update the length label."""
        self.length_value_label.configure(text=str(int(value)))

    def _generate_password(self):
        """Generate a new password."""
        length = self.length.get()

        # Build character set
        chars = ""
        if self.use_uppercase.get():
            chars += string.ascii_uppercase
        if self.use_lowercase.get():
            chars += string.ascii_lowercase
        if self.use_digits.get():
            chars += string.digits
        if self.use_symbols.get():
            chars += string.punctuation

        if not chars:
            self.show_error("Please select at least one character type")
            return

        # Generate password
        password = ''.join(secrets.choice(chars) for _ in range(length))
        self.generated_password.set(password)

        # Show strength indicator
        strength = self._calculate_strength(password)
        self.set_status(f"Generated {strength} password")

    def _calculate_strength(self, password):
        """Calculate password strength."""
        length = len(password)
        char_sets = 0

        if any(c.isupper() for c in password):
            char_sets += 1
        if any(c.islower() for c in password):
            char_sets += 1
        if any(c.isdigit() for c in password):
            char_sets += 1
        if any(c in string.punctuation for c in password):
            char_sets += 1

        # Simple strength calculation
        if length >= 20 and char_sets >= 4:
            return "Very Strong"
        elif length >= 16 and char_sets >= 3:
            return "Strong"
        elif length >= 12 and char_sets >= 2:
            return "Medium"
        elif length >= 8 and char_sets >= 1:
            return "Weak"
        else:
            return "Very Weak"

    def _copy_password(self):
        """Copy password to clipboard."""
        password = self.generated_password.get()
        if password:
            try:
                pyperclip.copy(password)
                self.show_success("Password copied to clipboard!")
            except Exception as e:
                self.show_error(f"Failed to copy: {str(e)}")
        else:
            self.show_error("No password to copy")
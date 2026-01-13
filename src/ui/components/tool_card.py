"""
Tool Card Component
A clickable card that represents a tool/feature.
"""

import customtkinter as ctk
from typing import Callable, Optional


class ToolCard(ctk.CTkFrame):
    """A clickable card widget for displaying a tool."""
    
    def __init__(
        self,
        parent,
        title: str,
        icon: str,
        description: str,
        colors: dict,
        command: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.colors = colors
        self.command = command
        
        # Card styling
        self.configure(
            fg_color=colors["bg_card"],
            corner_radius=12,
            cursor="hand2"
        )
        
        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=36),
            text_color=colors["primary_light"]
        )
        self.icon_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=colors["text"]
        )
        self.title_label.grid(row=1, column=0, padx=20, pady=(5, 2))
        
        # Description
        self.desc_label = ctk.CTkLabel(
            self,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=colors["text_secondary"],
            wraplength=140
        )
        self.desc_label.grid(row=2, column=0, padx=20, pady=(0, 20))
        
        # Bind hover effects
        self._bind_hover_events()
        
    def _bind_hover_events(self):
        """Bind hover and click events to all widgets."""
        widgets = [self, self.icon_label, self.title_label, self.desc_label]
        
        for widget in widgets:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)
            
    def _on_enter(self, event):
        """Handle mouse enter."""
        self.configure(fg_color=self.colors["bg_card_hover"])
        self.icon_label.configure(text_color=self.colors["primary"])
        
    def _on_leave(self, event):
        """Handle mouse leave."""
        self.configure(fg_color=self.colors["bg_card"])
        self.icon_label.configure(text_color=self.colors["primary_light"])
        
    def _on_click(self, event):
        """Handle click."""
        if self.command:
            self.command()

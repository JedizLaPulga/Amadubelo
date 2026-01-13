"""
File Utilities Tab View
Main container for file utility tools.
"""

import customtkinter as ctk
from typing import Optional
from ui.components.tool_card import ToolCard


class FileUtilitiesTab(ctk.CTkFrame):
    """Main view for File Utilities tab with tool cards."""
    
    TOOLS = [
        {
            "id": "pdf_to_image",
            "icon": "📄",
            "title": "PDF → Images",
            "description": "Convert PDF pages to PNG or JPG"
        },
        {
            "id": "docx_to_pdf",
            "icon": "📝",
            "title": "DOCX → PDF",
            "description": "Word documents to PDF"
        },
        {
            "id": "image_to_pdf",
            "icon": "🖼️",
            "title": "Images → PDF",
            "description": "Combine images into PDF"
        },
        {
            "id": "text_to_pdf",
            "icon": "✍️",
            "title": "Text → PDF",
            "description": "Create PDFs from text files"
        },
        {
            "id": "compress",
            "icon": "📉",
            "title": "Compress",
            "description": "Reduce image/PDF sizes"
        },
        {
            "id": "merge_pdf",
            "icon": "🔗",
            "title": "Merge PDFs",
            "description": "Combine multiple PDFs"
        },
        {
            "id": "split_pdf",
            "icon": "✂️",
            "title": "Split PDF",
            "description": "Extract pages from PDF"
        },
    ]
    
    def __init__(self, parent, colors: dict, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.colors = colors
        self.current_view = None
        
        self.configure(fg_color=colors["bg_dark"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Container for switching views
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Show tool grid
        self._show_tool_grid()
        
    def _show_tool_grid(self):
        """Show the grid of tool cards."""
        # Clear current view
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            scrollbar_button_color=self.colors["primary"],
            scrollbar_button_hover_color=self.colors["primary_hover"]
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid for cards
        for i in range(4):
            scroll_frame.grid_columnconfigure(i, weight=1, uniform="col")
        
        # Create tool cards
        for i, tool in enumerate(self.TOOLS):
            row = i // 4
            col = i % 4
            
            card = ToolCard(
                scroll_frame,
                title=tool["title"],
                icon=tool["icon"],
                description=tool["description"],
                colors=self.colors,
                command=lambda t=tool: self._open_tool(t["id"])
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    def _open_tool(self, tool_id: str):
        """Open a specific tool view."""
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Import and create the tool view
        view = None
        
        if tool_id == "pdf_to_image":
            from ui.file_utilities.pdf_to_image import PdfToImageView
            view = PdfToImageView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "docx_to_pdf":
            from ui.file_utilities.docx_to_pdf import DocxToPdfView
            view = DocxToPdfView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "image_to_pdf":
            from ui.file_utilities.image_to_pdf import ImageToPdfView
            view = ImageToPdfView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "text_to_pdf":
            from ui.file_utilities.text_to_pdf import TextToPdfView
            view = TextToPdfView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "compress":
            from ui.file_utilities.compress_view import CompressView
            view = CompressView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "merge_pdf":
            from ui.file_utilities.merge_pdf import MergePdfView
            view = MergePdfView(self.container, self.colors, on_back=self._show_tool_grid)
        elif tool_id == "split_pdf":
            from ui.file_utilities.split_pdf import SplitPdfView
            view = SplitPdfView(self.container, self.colors, on_back=self._show_tool_grid)
        
        if view:
            view.grid(row=0, column=0, sticky="nsew")
            self.current_view = view

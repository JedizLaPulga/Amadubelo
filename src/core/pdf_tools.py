"""
PDF Tools
Merge and split PDF files.
"""

import os
from pathlib import Path
from typing import List, Optional, Callable, Tuple
from pypdf import PdfReader, PdfWriter


def merge_pdfs(
    pdf_paths: List[str],
    output_path: str,
    progress_callback: Optional[Callable] = None
) -> str:
    """
    Merge multiple PDF files into one.
    
    Args:
        pdf_paths: List of PDF file paths
        output_path: Output PDF path
        progress_callback: Optional callback(current, total)
        
    Returns:
        Output PDF path
    """
    if not pdf_paths:
        raise ValueError("No PDF files provided")
    
    writer = PdfWriter()
    total = len(pdf_paths)
    
    for i, pdf_path in enumerate(pdf_paths):
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)
            
        if progress_callback:
            progress_callback(i + 1, total)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    return output_path


def split_pdf(
    pdf_path: str,
    output_folder: str,
    page_ranges: Optional[List[Tuple[int, int]]] = None,
    progress_callback: Optional[Callable] = None
) -> List[str]:
    """
    Split a PDF into separate files.
    
    Args:
        pdf_path: Path to PDF file
        output_folder: Folder to save split PDFs
        page_ranges: List of (start, end) page tuples (1-indexed).
                     If None, splits into individual pages.
        progress_callback: Optional callback(current, total)
        
    Returns:
        List of output PDF paths
    """
    os.makedirs(output_folder, exist_ok=True)
    
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    base_name = Path(pdf_path).stem
    
    output_files = []
    
    if page_ranges is None:
        # Split into individual pages
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            
            output_path = os.path.join(output_folder, f"{base_name}_page_{i+1}.pdf")
            with open(output_path, 'wb') as f:
                writer.write(f)
                
            output_files.append(output_path)
            
            if progress_callback:
                progress_callback(i + 1, total_pages)
    else:
        # Split by ranges
        total = len(page_ranges)
        for i, (start, end) in enumerate(page_ranges):
            writer = PdfWriter()
            
            # Convert to 0-indexed
            start_idx = max(0, start - 1)
            end_idx = min(total_pages, end)
            
            for page_idx in range(start_idx, end_idx):
                writer.add_page(reader.pages[page_idx])
            
            output_path = os.path.join(output_folder, f"{base_name}_pages_{start}-{end}.pdf")
            with open(output_path, 'wb') as f:
                writer.write(f)
                
            output_files.append(output_path)
            
            if progress_callback:
                progress_callback(i + 1, total)
    
    return output_files


def get_pdf_info(pdf_path: str) -> dict:
    """
    Get information about a PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary with PDF information
    """
    reader = PdfReader(pdf_path)
    
    info = {
        "pages": len(reader.pages),
        "encrypted": reader.is_encrypted,
        "metadata": {}
    }
    
    if reader.metadata:
        info["metadata"] = {
            "title": reader.metadata.get("/Title", ""),
            "author": reader.metadata.get("/Author", ""),
            "subject": reader.metadata.get("/Subject", ""),
            "creator": reader.metadata.get("/Creator", ""),
        }
    
    return info

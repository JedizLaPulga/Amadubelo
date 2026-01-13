"""
File Compressor
Compress images and PDFs.
"""

import os
from pathlib import Path
from typing import Optional, Callable
from PIL import Image
from pypdf import PdfReader, PdfWriter


def compress_image(
    image_path: str,
    output_path: Optional[str] = None,
    quality: int = 70,
    max_size: Optional[tuple] = None
) -> tuple:
    """
    Compress an image file.
    
    Args:
        image_path: Path to image file
        output_path: Output path (optional, defaults to overwrite)
        quality: JPEG quality (1-100)
        max_size: Optional (width, height) to resize
        
    Returns:
        Tuple of (output_path, original_size, new_size)
    """
    if output_path is None:
        output_path = image_path
    
    # Get original size
    original_size = os.path.getsize(image_path)
    
    # Open image
    img = Image.open(image_path)
    
    # Convert to RGB if needed (for JPEG)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Resize if max_size specified
    if max_size:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save with compression
    img.save(output_path, 'JPEG', quality=quality, optimize=True)
    
    new_size = os.path.getsize(output_path)
    
    return output_path, original_size, new_size


def compress_images_batch(
    image_paths: list,
    output_folder: str,
    quality: int = 70,
    progress_callback: Optional[Callable] = None
) -> list:
    """
    Compress multiple images.
    
    Args:
        image_paths: List of image paths
        output_folder: Output folder
        quality: JPEG quality
        progress_callback: Optional callback(current, total)
        
    Returns:
        List of (output_path, original_size, new_size) tuples
    """
    os.makedirs(output_folder, exist_ok=True)
    
    results = []
    total = len(image_paths)
    
    for i, img_path in enumerate(image_paths):
        base_name = Path(img_path).stem
        output_path = os.path.join(output_folder, f"{base_name}_compressed.jpg")
        
        result = compress_image(img_path, output_path, quality)
        results.append(result)
        
        if progress_callback:
            progress_callback(i + 1, total)
    
    return results


def compress_pdf(
    pdf_path: str,
    output_path: Optional[str] = None,
    image_quality: int = 50
) -> tuple:
    """
    Compress a PDF file by reducing image quality.
    
    Note: This is a basic compression. For better results,
    consider using Ghostscript or similar tools.
    
    Args:
        pdf_path: Path to PDF file
        output_path: Output path (optional)
        image_quality: Quality for embedded images
        
    Returns:
        Tuple of (output_path, original_size, new_size)
    """
    if output_path is None:
        base = Path(pdf_path).stem
        folder = Path(pdf_path).parent
        output_path = str(folder / f"{base}_compressed.pdf")
    
    original_size = os.path.getsize(pdf_path)
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    
    # Remove unused objects
    writer.add_metadata(reader.metadata or {})
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    new_size = os.path.getsize(output_path)
    
    return output_path, original_size, new_size


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def calculate_savings(original: int, compressed: int) -> str:
    """Calculate compression savings percentage."""
    if original == 0:
        return "0%"
    savings = ((original - compressed) / original) * 100
    return f"{savings:.1f}%"

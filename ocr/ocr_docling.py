from docling.document_converter import DocumentConverter
from ocr.base_ocr import BaseOCREngine
from pathlib import Path
import fitz  # PyMuPDF
import tempfile
import os
from typing import Union, Tuple


class DoclingOCR(BaseOCREngine):
    def __init__(self, name="docling_ocr"):
        """
        Initialize Docling OCR processor
        
        Args:
            name: Name identifier for this OCR processor
        """
        self.converter = DocumentConverter()
        self.name = name
    
    def extract_text(self, file_path: Union[str, Path, object]) -> Union[str, Tuple[str, dict]]:
        """
        Extract text from document using Docling.
        
        Can be called with:
        - A file path (str or Path): Returns markdown string (base class interface)
        - An Invoice object: Returns tuple (markdown, markdown_by_page) (Invoice interface)
        
        Args:
            file_path: File path string/Path, or Invoice object
            
        Returns:
            If file_path is string/Path: markdown string
            If file_path is Invoice object: tuple (markdown, markdown_by_page)
        """
        # Check if it's an Invoice object (has filename attribute)
        if hasattr(file_path, 'filename'):
            # Invoice interface: return (markdown, markdown_by_page)
            invoice = file_path
            file_path_str = str(invoice.filename)
            
            # Get full markdown
            result = self.converter.convert(file_path_str)
            markdown = result.document.export_to_markdown()
            
            # Get page-by-page markdown
            markdown_by_page = self._extract_by_page(file_path_str)
            
            return markdown, markdown_by_page
        else:
            # Base class interface: return markdown string
            file_path_str = str(file_path)
            result = self.converter.convert(file_path_str)
            markdown = result.document.export_to_markdown()
            return markdown
    
    def _extract_by_page(self, file_path: str) -> dict[int, str]:
        """
        Extract markdown for each page separately
        
        Args:
            file_path: Path to PDF or image file
            
        Returns:
            Dictionary mapping page number (1-indexed) to markdown content
        """
        markdown_by_page = {}
        
        # Check if it's a PDF
        if file_path.lower().endswith('.pdf'):
            try:
                with fitz.open(file_path) as doc:
                    num_pages = len(doc)
                    
                    # Process each page separately
                    for page_num in range(num_pages):
                        # Create a temporary PDF with just this page
                        temp_pdf = tempfile.mktemp(suffix=".pdf")
                        temp_doc = fitz.open()
                        temp_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                        temp_doc.save(temp_pdf)
                        temp_doc.close()
                        
                        try:
                            # Convert this single page
                            result = self.converter.convert(temp_pdf)
                            page_markdown = result.document.export_to_markdown()
                            markdown_by_page[page_num + 1] = page_markdown
                        finally:
                            # Clean up temporary file
                            if os.path.exists(temp_pdf):
                                os.remove(temp_pdf)
            except Exception as e:
                raise Exception(f"Error processing PDF pages {file_path}: {str(e)}")
        else:
            # For images, there's only one page
            try:
                result = self.converter.convert(file_path)
                markdown = result.document.export_to_markdown()
                markdown_by_page[1] = markdown
            except Exception as e:
                raise Exception(f"Error processing image {file_path}: {str(e)}")
        
        return markdown_by_page


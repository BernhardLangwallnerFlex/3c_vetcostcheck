from ocr.base_ocr import BaseOCREngine
from markitdown import MarkItDown

class MarkitdownOCR(BaseOCREngine):
    def __init__(self, enable_plugins=False, docintel_endpoint=None, llm_client=None, llm_model=None):
        """Initialize Markitdown OCR
        
        Args:
            enable_plugins: Enable 3rd-party plugins
            docintel_endpoint: Azure Document Intelligence endpoint (optional)
            llm_client: LLM client for image descriptions (optional)
            llm_model: LLM model name (optional)
        """
        self.md = MarkItDown(
            enable_plugins=enable_plugins,
            docintel_endpoint=docintel_endpoint,
            llm_client=llm_client,
            llm_model=llm_model
        )
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from file using Markitdown"""
        try:
            result = self.md.convert(file_path)
            return result.text_content.strip()
        except Exception as e:
            raise Exception(f"Error processing file {file_path}: {str(e)}")

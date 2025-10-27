from ocr.ocr_markitdown import MarkitdownOCR
from ocr.ocr_googlevision import GoogleOCR

#ocr_engine = MarkitdownOCR()# enable_plugins=True, docintel_endpoint=None, llm_client=None, llm_model=None)
ocr_engine = GoogleOCR()

print(ocr_engine.extract_text("test_docs/1.jpg"))
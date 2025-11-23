from storage.file_storage import get_file_path
from pathlib import Path
import os
from processors.gpt_processor import GPTInvoiceProcessor
from ocr.ocr_agentic import OCRAgenticProcessor
from invoice import Invoice
from dotenv import load_dotenv
from utils import ensure_json_serializable
load_dotenv()

def process_file(file_id: str):
    file_path = get_file_path(file_id)

    agentic_ocr_engine = OCRAgenticProcessor(name = "agentic_ocr")

    invoice = Invoice(filename=Path(file_path), ocr_engine=agentic_ocr_engine)

    # initialize GPT processor and extract data from subdocuments
    processor = GPTInvoiceProcessor(
        name="gpt_processor",
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4",
        vision_model="gpt-4o"  # or "gpt-4.1", or whatever OpenAI supports for vision in your account
    )

    invoice.extract_markdown()
    invoice.analyze_document()
    invoice.split_document_into_invoices()
    invoice.extract_data_from_subdocuments(processor)

    return ensure_json_serializable(invoice.extraction_result_json)

"""
    # Load your central class
    invoice = InvoiceDocument(file_path)

    # Your existing pipeline – adapt to your class
    invoice.load()
    invoice.split()
    invoice.run_pipeline()   # OCR + LLM stages
    invoice.cleanup()

    return invoice.to_dict()   # whatever your final JSON output is"""

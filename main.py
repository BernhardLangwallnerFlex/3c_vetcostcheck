from processors.gpt_processor import GPTInvoiceProcessor
from ocr.ocr_tesseract import TesseractOCR
from ocr.ocr_mistral import MistralOCR
from ocr.ocr_googlevision import GoogleOCR
from ocr.ocr_agentic import OCRAgenticProcessor
from invoice import Invoice
from dotenv import load_dotenv
import os
from pathlib import Path
# Load API key from .env
load_dotenv()

input_folder = "3C_testdaten_pdf/"
output_folder = "3C_testdaten_json/"

# get list of image files (.jpg, .jpeg, .png) in input_folder
files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.pdf'))]
files.sort()
file = "230041495V_Splitt.pdf"
file_string = file.split(".")[0]
file_path = input_folder + file


# initialize OCR engines
#google_ocr_engine = GoogleOCR()
agentic_ocr_engine = OCRAgenticProcessor(name = "agentic_ocr")
# mistral_ocr_engine = MistralOCR()

invoice = Invoice(filename=Path(file_path), ocr_engine=agentic_ocr_engine)

invoice.extract_markdown()
invoice.analyze_document()
print(invoice.analysis_dict)
invoice.split_document_into_invoices()

# initialize GPT processor
processor = GPTInvoiceProcessor(
    name="gpt_processor",
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",
    vision_model="gpt-4o"  # or "gpt-4.1", or whatever OpenAI supports for vision in your account
)

invoice.extract_data_from_subdocuments(processor)
print(invoice.extraction_result_json)
print(type(invoice.extraction_result_json))
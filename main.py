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

from storage.storage import S3Storage

storage = S3Storage(region_name="eu-central-1")

inv = Invoice(
    file_key="s3://3c-vetcostcheck/230041495V_Splitt.pdf",
    ocr_engine=agentic_ocr_engine,
    storage=storage,
    output_prefix="s3://3c-vetcostcheck/processed/"  # see note below
)

inv.extract_markdown()
inv.analyze_document()
print(inv.analysis_dict)
inv.split_document_into_invoices()

# initialize GPT processor
processor = GPTInvoiceProcessor(
    name="gpt_processor",
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",
    vision_model="gpt-4o"  # or "gpt-4.1", or whatever OpenAI supports for vision in your account
)

inv.extract_data_from_subdocuments(processor)
print(inv.extraction_result_json)
print(type(inv.extraction_result_json))
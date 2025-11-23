from processors.gpt_processor import GPTInvoiceProcessor
from ocr.ocr_tesseract import TesseractOCR
from ocr.ocr_mistral import MistralOCR
from ocr.ocr_googlevision import GoogleOCR
from ocr.ocr_agentic import OCRAgenticProcessor
from processors.agentic_processor import AgenticDocInvoiceProcessor
from invoice import Invoice
from utils import dict_of_dicts_to_csv
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from prompt_building.prompt_building import get_full_prompt
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







exit()

########################################################

exit()
results_dict = {
    "gpt_ocr_google": result_gpt_ocr_google
}
dict_of_dicts_to_csv(results_dict, "results.csv")

exit()


agentic_processor = AgenticDocInvoiceProcessor(
    model_id="dpt-2-latest"
)


# OCR + text pipeline
result_extraction_dict, parse_result_markdown = agentic_processor.extract(prompt, file_path)
#print("Text mode result:\n", result_text)
#print("Extraction result:\n", result_extraction)
print(result_extraction_dict)




exit()

result_text = agentic_processor.extract_from_file_direct(prompt, file_path)
print("Vision only mode result:\n", result_text)

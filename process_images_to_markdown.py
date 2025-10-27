from ocr.ocr_mistral import MistralOCR
from ocr.ocr_agentic import OCRAgenticProcessor

import os

three_c_folder = "3C_testdaten_jpg/"
files = os.listdir(three_c_folder)
files.sort()
mistral_ocr_engine = MistralOCR()
agentic_ocr_engine = OCRAgenticProcessor()


for file in files:
    file_path = three_c_folder + file
    markdown1 = mistral_ocr_engine.extract_text(file_path)
    markdown2 = agentic_ocr_engine.extract_text(file_path)
    with open(file_path.replace(".jpg", "mistral_ocr.md"), "w") as f:
        f.write(markdown1)
    with open(file_path.replace(".jpg", "agentic_ocr.md"), "w") as f:
        f.write(markdown2)
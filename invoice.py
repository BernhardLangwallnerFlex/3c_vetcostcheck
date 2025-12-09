from pathlib import Path
import fitz  
from ocr.base_ocr import BaseOCREngine
from openai import OpenAI
import os
from utils import extract_json_from_response
from PIL import Image
from dotenv import load_dotenv
from prompt_building.prompt_building import build_prompt_for_analyze_document, get_full_prompt
import json
load_dotenv()


class Invoice():
    filename: Path
    page_number: int
    file_type: str
    # optional fields
    markdown: str
    markdown_by_page: dict[int, str]
    extraction_dict: dict
    subdocuments: list[dict]
    extraction_dict_by_subdocument: dict[int, dict]


    def __init__(self, filename: Path, ocr_engine: BaseOCREngine):
        self.filename = filename
        self.ocr_engine = ocr_engine
        self.markdown = ""
        self.markdown_by_page = {}
        self.extraction_dict = {}
        self.analysis_dict = {}
        self.file_type = "pdf" if filename.suffix =='.pdf' else "image"
        if self.file_type == "pdf":
            # get number of pages
            with fitz.open(filename) as doc:
                self.page_number = len(doc)
        else:
            self.page_number = 1
        
    def extract_markdown(self):
        markdown, markdown_by_page = self.ocr_engine.extract_text(self)
        self.markdown = markdown
        self.markdown_by_page = markdown_by_page
        self.markdown_with_pages_numbers = "\n\n---\n\n".join([f"--- PAGE {page} ---\n: {markdown}" for page, markdown in markdown_by_page.items()])

        
    def analyze_document(self):

        prompt = build_prompt_for_analyze_document(config_path="configs/extraction_config.json",
                                                    markdown_text=self.markdown_with_pages_numbers)

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        self.analysis_dict = extract_json_from_response(response.choices[0].message.content)
    

    def split_document_into_invoices(self):
        subdocuments = []
        with fitz.open(self.filename) as doc:
            for document_number, page_numbers in self.analysis_dict["invoice_pages"].items():
                subdocument = dict()
                subdocument_markdown = "\n\n".join([self.markdown_by_page[page_number] for page_number in page_numbers])
                subdocument["markdown"] = subdocument_markdown
                # save markdown for subdocument to file
                with open("temp/" + f"{self.filename.stem}_subdocument_{document_number}.md", "w") as f:
                    f.write(subdocument_markdown)
                subdocument["page_numbers"] = page_numbers
                subdocument["pdf_filename"] = "temp/" + f"{self.filename.stem}_subdocument_{document_number}.pdf"
                subdocument["image_filename"] = "temp/" + f"{self.filename.stem}_subdocument_{document_number}.png"
                # save subdocument as pdf
                subdoc = fitz.open()
                subdoc.insert_pdf(doc, from_page=page_numbers[0]-1, to_page=page_numbers[-1]-1)
                subdoc.save(subdocument["pdf_filename"])

                # save subdocument pages as images and concatenate them into one image
                page_images = []
                for page in subdoc:
                    pix = page.get_pixmap(dpi=300)
                    mode = "RGB" if pix.alpha == 0 else "RGBA"
                    pil_image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                    page_images.append(pil_image)
                # Concatenate vertically
                total_height = sum(img.height for img in page_images)
                max_width = max(img.width for img in page_images)
                concatenated_image = Image.new("RGB", (max_width, total_height), color=(255, 255, 255))
                y_offset = 0
                for img in page_images:
                    concatenated_image.paste(img, (0, y_offset))
                    y_offset += img.height
                concatenated_image.save(subdocument["image_filename"])
                subdoc.close()

                subdocuments.append(subdocument)
        self.subdocuments = subdocuments


    def extract_data_from_subdocuments(self, processor):
        extraction_dicts = []
        extraction_result_json = {'number_of_subdocuments': len(self.subdocuments)}
        for i, subdocument in enumerate(self.subdocuments):
            extraction_dict = processor.extract(
                                                subdocument["image_filename"],
                                                use_ocr=True,
                                                use_vision=True,
                                                markdown_text=subdocument["markdown"],
                                                prompt=get_full_prompt(ocr_text=subdocument["markdown"], animal_information=self.analysis_dict["animals"]),
                                                animal_information=self.analysis_dict["animals"])
            extraction_dicts.append(extraction_dict)
        
            #print(extraction_dict)
        extraction_result_json['subdocuments'] = extraction_dicts
        self.extraction_result_json = extraction_result_json

        # save extracted_data to json file with indent 4
        with open(f'extracted_data_{self.filename.stem}.json', 'w+') as f:
            json.dump(extraction_result_json, f, indent=4)
    

    def cleanup_temporary_files(self):
        for subdocument in self.subdocuments:
            os.remove(subdocument["pdf_filename"])
            os.remove(subdocument["image_filename"])
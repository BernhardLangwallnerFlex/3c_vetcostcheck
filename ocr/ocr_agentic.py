import os
from landingai_ade import LandingAIADE
from dotenv import load_dotenv
import json

from openai.types import auto_file_chunking_strategy_param
from invoice import Invoice
from pathlib import Path
load_dotenv()

class OCRAgenticProcessor:
    def __init__(self, model_id="dpt-2-latest", name="agentic_ocr"):

        self.client = LandingAIADE(
            apikey = os.environ["VISION_AGENT_API_KEY"],
            environment = "eu"  # or "production" or as needed
        )
        self.model_id = model_id
        self.name = name
        
    def extract_text(self, invoice: Invoice) -> None:
        parse_res = self.client.parse(
                                        document = invoice.filename,
                                        model = self.model_id,
                                        split="page"
        )
        markdown = parse_res.markdown
        n_pages = len(parse_res.splits)
        markdown_by_page = {i+1:parse_res.splits[i].markdown for i in range(n_pages)}
        
        #with open(f"{self.name}_parse_res.json", "w+") as f:
        #    json.dump(parse_res.model_dump(), f, indent=4)

        #with open(f"{self.name}_markdown.md", "w+") as f:
        #    f.write(markdown)
        #for page, markdown in markdown_by_page.items():
        #    with open(f"{self.name}_markdown_page_{page}.md", "w+") as f:
        #        f.write(markdown)

        return markdown, markdown_by_page
    

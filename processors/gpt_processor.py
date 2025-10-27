from openai import OpenAI
from utils import convert_file_to_images, extract_text_from_file
import base64
from prompt_building import build_prompt_from_config
import json
import re


class GPTInvoiceProcessor:
    def __init__(self, model="gpt-4", vision_model=None, api_key=None, ocr_engine=None):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.vision_model = vision_model
        self.ocr_engine = ocr_engine  # should be a BaseOCREngine instance


    def extract(self, file_path: str, use_ocr=True, use_vision=True) -> str:
        if use_ocr and not self.ocr_engine:
            raise ValueError("No OCR engine provided for text extraction.")
        if use_vision and not self.vision_model:
            raise ValueError("No vision model configured")

        # if OCR engine is a list, extract text from each engine
        if use_ocr:
            if isinstance(self.ocr_engine, list):
                ocr_text = "\n\n---\n\n".join([engine.extract_text(file_path) for engine in self.ocr_engine])
            else:
                ocr_text = self.ocr_engine.extract_text(file_path)
        else:
            ocr_text = ""


        prompt = build_prompt_from_config("configs/extraction_config.json", use_ocr=True, use_vision=True, ocr_text=ocr_text)

        #print(full_prompt)
        content_blocks = [{"type": "text", "text": prompt}]

        if use_vision:
            images = convert_file_to_images(file_path)      
            for img_path in images:
                with open(img_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                    content_blocks.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64}",
                            "detail": "auto"
                        }
                    }
                )
        model = self.vision_model if use_vision else self.model
        response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content_blocks}],
                temperature=0
            )

        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        # Model-specific pricing (USD per 1K tokens)
        PROMPT_RATE = 0.00015
        COMPLETION_RATE = 0.0006
        cost = (prompt_tokens / 1000 * PROMPT_RATE) + (completion_tokens / 1000 * COMPLETION_RATE)
        print(f"Cost of this call: ${cost:.6f}")

        #result = response.choices[0].message.content
        clean = re.sub(r"^```json|^'''json|```$|'''$", "", response.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
    

        result = json.loads(clean)

        return result

import os
from landingai_ade import LandingAIADE
from dotenv import load_dotenv
from ocr_agentic import OCRAgenticProcessor

load_dotenv()
file_path = "3C_testdaten_jpg/230074893V_Splitt.jpg"
client = LandingAIADE(
            apikey = os.environ["VISION_AGENT_API_KEY"],
            environment = "eu"  # or "production" or as needed
        )
parse_res = client.parse(document_url = file_path)
print(parse_res.markdown)


ocr_engine = OCRAgenticProcessor()
print(ocr_engine.extract_text(file_path))
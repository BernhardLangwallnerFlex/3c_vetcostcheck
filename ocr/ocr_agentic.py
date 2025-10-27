import os
from landingai_ade import LandingAIADE
from dotenv import load_dotenv
load_dotenv()

class OCRAgenticProcessor:
    def __init__(self, model_id="dpt-2-latest"):

        self.client = LandingAIADE(
            apikey = os.environ["VISION_AGENT_API_KEY"],
            environment = "eu"  # or "production" or as needed
        )
        self.model_id = model_id

        
    def extract_text(self, file_path: str) -> str:
        parse_res = self.client.parse(
                                        document_url = file_path,
                                        model = self.model_id
        )
        return parse_res.markdown
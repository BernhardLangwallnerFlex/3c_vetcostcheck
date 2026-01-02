import os
from pathlib import Path
from dotenv import load_dotenv

from storage.file_storage import get_file_key  # <-- NEW (was get_file_path)

from storage.storage import LocalStorage, S3Storage  # adjust import to your actual module names
from invoice import Invoice

from ocr.ocr_agentic import OCRAgenticProcessor
from processors.gpt_processor import GPTInvoiceProcessor
from utils import ensure_json_serializable

load_dotenv()


def _build_storage():
    """
    Decide storage backend from env. Keep it dead simple:
    STORAGE_BACKEND=local|s3
    """
    backend = os.getenv("STORAGE_BACKEND", "local").lower()

    if backend == "s3":
        region = os.getenv("AWS_DEFAULT_REGION", "eu-central-1")
        return S3Storage(region_name=region)

    # default: local
    base_dir = Path(os.getenv("LOCAL_STORAGE_BASE_DIR", Path.cwd()))
    return LocalStorage(base_dir=base_dir)


def process_file(file_id: str):
    # 1) Resolve file_id -> storage key (local path or s3://...)
    file_key = get_file_key(file_id)

    # 2) Build storage backend
    storage = _build_storage()

    # 3) Engines / processors
    agentic_ocr_engine = OCRAgenticProcessor(name="agentic_ocr")

    processor = GPTInvoiceProcessor(
        name="gpt_processor",
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4"),
        vision_model=os.getenv("OPENAI_VISION_MODEL", "gpt-4o"),
    )

    # 4) Output prefix (local folder or s3 prefix)
    #    Examples:
    #      local: output_prefix="outputs"
    #      s3:    output_prefix="s3://my-bucket/processed/invoices"
    output_prefix = os.getenv("OUTPUT_PREFIX", "outputs")

    # 5) Run pipeline
    invoice = Invoice(
        file_key=file_key,
        ocr_engine=agentic_ocr_engine,
        storage=storage,
        output_prefix=output_prefix,
    )

    invoice.extract_markdown()
    invoice.analyze_document()
    invoice.split_document_into_invoices()
    invoice.extract_data_from_subdocuments(processor)

    # (optional) keep artifacts in S3 but remove local temps
    # invoice.cleanup_temporary_files()  # enable if desired

    return ensure_json_serializable(invoice.extraction_result_json)
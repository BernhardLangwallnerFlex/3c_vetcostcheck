# storage/file_storage.py
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional

from storage.storage import LocalStorage, S3Storage  # adjust to your actual module


def _build_storage():
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    if backend == "s3":
        region = os.getenv("AWS_DEFAULT_REGION", "eu-central-1")
        return S3Storage(region_name=region)
    return LocalStorage(base_dir=Path(os.getenv("LOCAL_STORAGE_BASE_DIR", Path.cwd())))


def _uploads_prefix() -> str:
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    prefix = os.getenv("UPLOADS_PREFIX", "uploads").rstrip("/")

    # Guardrail: don't allow s3:// prefix in local mode (common 500 cause)
    if backend != "s3" and prefix.startswith("s3://"):
        raise RuntimeError(
            f"UPLOADS_PREFIX is '{prefix}' but STORAGE_BACKEND is '{backend}'. "
            "Set STORAGE_BACKEND=s3 or change UPLOADS_PREFIX to a local folder like 'uploads'."
        )

    # Guardrail: in s3 mode, require s3:// prefix
    if backend == "s3" and not prefix.startswith("s3://"):
        raise RuntimeError(
            f"STORAGE_BACKEND is 's3' but UPLOADS_PREFIX is '{prefix}'. "
            "Set UPLOADS_PREFIX like 's3://<bucket>/uploads'."
        )

    return prefix


def get_file_key(file_id: str) -> str:
    return f"{_uploads_prefix()}/{file_id}"


def save_upload(file_bytes: bytes, original_filename: Optional[str] = None, content_type: Optional[str] = None) -> str:
    storage = _build_storage()

    # determine extension (optional but helpful)
    ext = ""
    if original_filename:
        ext = Path(original_filename).suffix.lower()
        # basic allowlist to avoid weird stuff
        if ext and ext not in {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
            ext = ""  # or raise if you want strict

    file_id = f"{uuid.uuid4().hex}{ext}"
    key = get_file_key(file_id)

    storage.write_bytes(key, file_bytes, content_type=content_type)
    return file_id
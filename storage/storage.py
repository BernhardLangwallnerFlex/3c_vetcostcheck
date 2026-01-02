# storage.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Union, Optional
import io
import os
import shutil
import tempfile

# S3 is optional until you use it
try:
    import boto3
except Exception:  # pragma: no cover
    boto3 = None


StorageKey = str  # could be "local:/abs/path/file.pdf" or "s3://bucket/key.pdf" or just a plain path


class StorageBackend(Protocol):
    def read_bytes(self, key: StorageKey) -> bytes: ...
    def write_bytes(self, key: StorageKey, data: bytes, content_type: Optional[str] = None) -> None: ...
    def write_text(self, key: StorageKey, text: str, encoding: str = "utf-8") -> None: ...
    def delete(self, key: StorageKey) -> None: ...
    def exists(self, key: StorageKey) -> bool: ...

    def materialize_to_local(self, key: StorageKey, suffix: str = "") -> Path:
        """
        Ensure key is available as a local file path and return that path.
        For LocalStorage it's the original path; for S3 it downloads to temp.
        """


def is_s3_uri(key: str) -> bool:
    return key.startswith("s3://")


def parse_s3_uri(uri: str) -> tuple[str, str]:
    # s3://bucket/some/path/file.pdf -> ("bucket", "some/path/file.pdf")
    if not uri.startswith("s3://"):
        raise ValueError(f"Not an s3 uri: {uri}")
    without = uri[len("s3://") :]
    bucket, _, key = without.partition("/")
    if not bucket or not key:
        raise ValueError(f"Invalid s3 uri: {uri}")
    return bucket, key


@dataclass
class LocalStorage(StorageBackend):
    base_dir: Optional[Path] = None

    def _resolve(self, key: StorageKey) -> Path:
        p = Path(key)
        if self.base_dir and not p.is_absolute():
            p = self.base_dir / p
        return p

    def read_bytes(self, key: StorageKey) -> bytes:
        return self._resolve(key).read_bytes()

    def write_bytes(self, key: StorageKey, data: bytes, content_type: Optional[str] = None) -> None:
        p = self._resolve(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def write_text(self, key: StorageKey, text: str, encoding: str = "utf-8") -> None:
        p = self._resolve(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding=encoding)

    def delete(self, key: StorageKey) -> None:
        p = self._resolve(key)
        if p.exists():
            p.unlink()

    def exists(self, key: StorageKey) -> bool:
        return self._resolve(key).exists()

    def materialize_to_local(self, key: StorageKey, suffix: str = "") -> Path:
        # already local
        return self._resolve(key)


@dataclass
class S3Storage(StorageBackend):
    """
    key is expected as s3://bucket/path/to/file.ext
    """
    region_name: Optional[str] = None

    def __post_init__(self):
        if boto3 is None:
            raise ImportError("boto3 not installed. `pip install boto3`")
        self.s3 = boto3.client("s3", region_name=self.region_name)
        self._tmp_dir = Path(tempfile.mkdtemp(prefix="invoice_s3_"))

    def read_bytes(self, key: StorageKey) -> bytes:
        bucket, obj_key = parse_s3_uri(key)
        buf = io.BytesIO()
        self.s3.download_fileobj(bucket, obj_key, buf)
        return buf.getvalue()

    def write_bytes(self, key: StorageKey, data: bytes, content_type: Optional[str] = None) -> None:
        bucket, obj_key = parse_s3_uri(key)
        extra = {}
        if content_type:
            extra["ContentType"] = content_type
        self.s3.put_object(Bucket=bucket, Key=obj_key, Body=data, **extra)

    def write_text(self, key: StorageKey, text: str, encoding: str = "utf-8") -> None:
        self.write_bytes(key, text.encode(encoding), content_type="text/plain; charset=utf-8")

    def delete(self, key: StorageKey) -> None:
        bucket, obj_key = parse_s3_uri(key)
        self.s3.delete_object(Bucket=bucket, Key=obj_key)

    def exists(self, key: StorageKey) -> bool:
        bucket, obj_key = parse_s3_uri(key)
        try:
            self.s3.head_object(Bucket=bucket, Key=obj_key)
            return True
        except Exception:
            return False

    def materialize_to_local(self, key: StorageKey, suffix: str = "") -> Path:
        bucket, obj_key = parse_s3_uri(key)
        filename = Path(obj_key).name
        if suffix and not filename.endswith(suffix):
            # if caller wants a suffix, enforce it (helpful if key has no extension)
            filename = filename + suffix
        local_path = self._tmp_dir / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with local_path.open("wb") as f:
            self.s3.download_fileobj(bucket, obj_key, f)
        return local_path

    def cleanup_tmp(self) -> None:
        if self._tmp_dir.exists():
            shutil.rmtree(self._tmp_dir, ignore_errors=True)
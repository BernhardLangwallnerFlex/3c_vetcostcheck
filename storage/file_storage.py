import uuid
import os
from config import FILES_DIR

def save_upload(file) -> str:
    """Save uploaded file and return file_id."""
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    path = os.path.join(FILES_DIR, filename)

    with open(path, "wb") as f:
        f.write(file)

    return file_id


def get_file_path(file_id: str) -> str:
    return os.path.join(FILES_DIR, f"{file_id}.pdf")
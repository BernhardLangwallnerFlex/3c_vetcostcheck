from fastapi import APIRouter, UploadFile, File
from storage.file_storage import save_upload

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_bytes = await file.read()
    file_id = save_upload(file_bytes)
    return {"file_id": file_id}
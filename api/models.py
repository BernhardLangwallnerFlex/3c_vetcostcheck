from pydantic import BaseModel

class ProcessRequest(BaseModel):
    file_id: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None
    error: str | None = None
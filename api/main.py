from fastapi import FastAPI
from api.routes import upload, process, job

app = FastAPI(title="Invoice Extraction API")

app.include_router(upload.router)
app.include_router(process.router)
app.include_router(job.router)
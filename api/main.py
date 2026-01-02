from fastapi import FastAPI, Depends
from api.routes import upload, process, job, health
from api.dependencies import verify_api_key

app = FastAPI(title="Invoice Extraction API")

# Apply to all routers
app.include_router(upload.router, dependencies=[Depends(verify_api_key)])
app.include_router(process.router, dependencies=[Depends(verify_api_key)])
app.include_router(job.router, dependencies=[Depends(verify_api_key)])
app.include_router(health.router)
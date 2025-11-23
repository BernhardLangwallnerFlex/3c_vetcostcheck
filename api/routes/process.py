from fastapi import APIRouter
from redis import Redis
from rq import Queue
from jobs.tasks import process_file
from api.models import ProcessRequest
from config import REDIS_URL

router = APIRouter()
redis_conn = Redis.from_url(REDIS_URL)
queue = Queue("invoice-jobs", connection=redis_conn)

@router.post("/process")
async def process_document(req: ProcessRequest):
    job = queue.enqueue(process_file, req.file_id)
    return {"job_id": job.get_id(), "status": "queued"}
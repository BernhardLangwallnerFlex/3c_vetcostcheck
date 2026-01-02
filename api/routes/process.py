import os
from fastapi import APIRouter
from redis import Redis
from rq import Queue

from jobs.tasks import process_file
from api.models import ProcessRequest

router = APIRouter()

QUEUE_NAME = os.getenv("RQ_QUEUE_NAME", "invoice-jobs")


def get_queue() -> Queue:
    redis_url = os.environ["REDIS_URL"]  # fail fast if missing
    redis_conn = Redis.from_url(redis_url)
    return Queue(QUEUE_NAME, connection=redis_conn)


@router.post("/process")
async def process_document(req: ProcessRequest):
    queue = get_queue()
    job = queue.enqueue(process_file, req.file_id)

    return {
        "job_id": job.get_id(),
        "status": "queued",
        "queue": QUEUE_NAME,
    }
from fastapi import APIRouter
from redis import Redis
from rq.job import Job
from config import REDIS_URL
from api.models import JobStatusResponse


router = APIRouter()
redis_conn = Redis.from_url(REDIS_URL)

@router.get("/job/{job_id}", response_model=JobStatusResponse)
async def get_job(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except:
        return {"job_id": job_id, "status": "not_found", "result": None}

    if job.is_finished:
        return {"job_id": job_id, "status": "finished", "result": job.result}

    if job.is_failed:
        return {"job_id": job_id, "status": "failed", "error": str(job.exc_info)}

    return {"job_id": job_id, "status": job.get_status()}
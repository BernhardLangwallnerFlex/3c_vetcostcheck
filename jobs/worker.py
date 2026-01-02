import os
from redis import Redis
from rq import Worker, Queue

queue_name = os.getenv("RQ_QUEUE_NAME", "invoice-jobs")

if __name__ == "__main__":
    redis_conn = Redis.from_url(os.environ["REDIS_URL"])
    queues = [Queue(queue_name, connection=redis_conn)]
    worker = Worker(queues, connection=redis_conn)
    worker.work()
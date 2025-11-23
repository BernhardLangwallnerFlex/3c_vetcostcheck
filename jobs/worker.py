from redis import Redis
from rq import Worker, Queue
from config import REDIS_URL

listen = ["invoice-jobs"]

if __name__ == "__main__":
    redis_conn = Redis.from_url(REDIS_URL)

    # Create queues with explicit connection
    queues = [Queue(name, connection=redis_conn) for name in listen]

    # Create worker with explicit connection
    worker = Worker(queues, connection=redis_conn)

    worker.work()
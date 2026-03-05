from backend.tasks import celery


if __name__ == "__main__":
    celery.worker_main([
        "worker",
        "--loglevel=INFO",
        "--concurrency=4",
    ])

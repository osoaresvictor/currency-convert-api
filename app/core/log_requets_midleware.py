from time import time

from fastapi import Request

from app.core.logger import Logger


async def log_requests(request: Request, call_next):  # pragma: no cover
    start_time = time()

    method = request.method
    url = request.url
    headers = dict(request.headers)

    Logger.info(f"Received HTTP request: {method} {url} - Headers: {headers}")

    response = await call_next(request)
    process_time = time() - start_time
    Logger.info(
        f"Response: {method} {url} \
        - Status: {response.status_code} \
        - Processing Time: {process_time:.4f}s"
    )

    return response

import requests
from pybreaker import CircuitBreaker


class HttpCircuitBreaker:
    def __init__(self, fail_max: int = 5, reset_timeout: int = 60):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout

    @CircuitBreaker(fail_max=3, reset_timeout=10)
    def fetch_data(self, url, params: dict):  # pragma: no cover
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response

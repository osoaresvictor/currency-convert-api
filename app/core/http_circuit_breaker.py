import requests
from pybreaker import CircuitBreaker


class HttpCircuitBreaker:
    fail_max: int = 0
    reset_timeout: int = 0

    def __init__(self, fail_max: int = 5, reset_timeout: int = 60):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout

    @CircuitBreaker(fail_max=fail_max, reset_timeout=reset_timeout)
    def fetch_data(self, url, params: dict):
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response

import time
import threading

class RateLimiter:
    def __init__(self, max_calls, interval):
        """
        Initialize the rate limiter.

        Args:
            max_calls (int): Maximum number of calls allowed within the interval.
            interval (float): Time window in seconds for the allowed calls.
        """
        self.max_calls = max_calls
        self.interval = interval
        self.call_times = []
        self.lock = threading.Lock()

    def allow_request(self):
        """
        Check if the request can be allowed based on the rate limit.

        Returns:
            bool: True if allowed, False otherwise.
        """
        with self.lock:
            current_time = time.time()
            self.call_times = [t for t in self.call_times if t > current_time - self.interval]

            if len(self.call_times) < self.max_calls:
                self.call_times.append(current_time)
                return True
            else:
                return False

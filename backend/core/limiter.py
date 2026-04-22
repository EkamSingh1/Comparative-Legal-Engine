from __future__ import annotations

import asyncio
import time
from collections import deque


class ProviderRateLimiter:
    """Small in-process limiter for free-tier Gemini model calls."""

    def __init__(self, calls_per_minute: int, min_spacing_seconds: float) -> None:
        self.calls_per_minute = max(1, calls_per_minute)
        self.min_spacing_seconds = max(0.0, min_spacing_seconds)
        self._calls: deque[float] = deque()
        self._last_call_at = 0.0
        self._lock = asyncio.Lock()

    async def wait_for_turn(self) -> None:
        async with self._lock:
            while True:
                now = time.monotonic()
                while self._calls and now - self._calls[0] >= 60.0:
                    self._calls.popleft()

                spacing_wait = max(0.0, self.min_spacing_seconds - (now - self._last_call_at))
                quota_wait = 0.0
                if len(self._calls) >= self.calls_per_minute:
                    quota_wait = max(0.0, 60.0 - (now - self._calls[0]))

                wait_for = max(spacing_wait, quota_wait)
                if wait_for <= 0.0:
                    self._last_call_at = time.monotonic()
                    self._calls.append(self._last_call_at)
                    return

                await asyncio.sleep(wait_for)

"""Tests for the Decorator pattern implementation."""

import time

from design_patterns.structural.decorator import (
    CachingDecorator,
    DataService,
    LoggingDecorator,
    RemoteDatabaseService,
    rate_limit,
)


class TestGoFDecorator:
    def test_raw_service(self) -> None:
        service: DataService = RemoteDatabaseService()
        result = service.fetch_data("SELECT 1")
        assert result == "Results for 'SELECT 1' from DB"

    def test_caching_decorator(self) -> None:
        service = RemoteDatabaseService()
        cached = CachingDecorator(service)

        res1 = cached.fetch_data("query_a")
        res2 = cached.fetch_data("query_a")

        assert res1 == res2
        assert cached.hits == 1
        assert cached.misses == 1

    def test_logging_decorator(self) -> None:
        service = RemoteDatabaseService()
        logged = LoggingDecorator(service)

        logged.fetch_data("query_b")
        assert len(logged.logs) == 2
        assert "[LOG START]" in logged.logs[0]
        assert "[LOG END]" in logged.logs[1]

    def test_stacked_decorators(self) -> None:
        service = RemoteDatabaseService()
        cached = CachingDecorator(service)
        logged = LoggingDecorator(cached)

        # First query executes
        logged.fetch_data("q1")
        # Second query should hit cache
        logged.fetch_data("q1")

        assert cached.hits == 1
        assert cached.misses == 1
        assert len(logged.logs) == 4


class TestPythonicRateLimitDecorator:
    def test_rate_limiter(self) -> None:
        calls = []

        @rate_limit(max_per_second=20.0)
        def sample_call() -> None:
            calls.append(time.monotonic())

        sample_call()
        sample_call()

        assert len(calls) == 2
        diff = calls[1] - calls[0]
        assert diff >= 0.04

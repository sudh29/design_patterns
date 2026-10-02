"""Decorator Design Pattern.

Classification: Structural
Intent:
    Attach additional responsibilities to an object dynamically.
    Decorators provide a flexible alternative to subclassing for extending functionality.

Motivation & Real-World Analogy:
    In web service APIs or data retrieval pipelines, cross-cutting concerns such as
    logging, in-memory caching, authorization, and execution timing are required.
    Creating subclasses for every combination (`CachedSecureDataService`, `LoggedCachedDataService`, etc.)
    causes an unmaintainable combinatorial explosion.
    A Decorator wraps the core service, intercepting calls to inject behavior while
    preserving the exact same interface.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class DataService {
            <<protocol>>
            +fetch_data(query: str) str
        }
        class DatabaseService {
            +fetch_data(query: str) str
        }
        class BaseServiceDecorator {
            <<abstract>>
            #wrapped: DataService
            +fetch_data(query: str) str
        }
        class CachingDecorator {
            -cache: dict
            +fetch_data(query: str) str
        }
        class LoggingDecorator {
            -logger: list
            +fetch_data(query: str) str
        }
        DataService <|.. DatabaseService
        DataService <|.. BaseServiceDecorator
        BaseServiceDecorator <|-- CachingDecorator
        BaseServiceDecorator <|-- LoggingDecorator
        BaseServiceDecorator o--> DataService : wraps
    ```
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import Any, Protocol


# ==============================================================================
# 1. Component Protocol: Common Interface
# ==============================================================================
class DataService(Protocol):
    """Component Interface: Declares operations that can be dynamically altered by decorators."""

    def fetch_data(self, query: str) -> str: ...


# ==============================================================================
# 2. Concrete Component
# ==============================================================================
class RemoteDatabaseService:
    """Core Concrete Component performing expensive queries."""

    def fetch_data(self, query: str) -> str:
        # Simulate latency or expensive I/O
        return f"Results for '{query}' from DB"


# ==============================================================================
# 3. GoF Class Decorators
# ==============================================================================
class BaseServiceDecorator:
    """Base Decorator holding a reference to a wrapped DataService."""

    def __init__(self, wrapped: DataService) -> None:
        self._wrapped = wrapped

    def fetch_data(self, query: str) -> str:
        return self._wrapped.fetch_data(query)


class CachingDecorator(BaseServiceDecorator):
    """Concrete Decorator adding in-memory memoization/caching."""

    def __init__(self, wrapped: DataService) -> None:
        super().__init__(wrapped)
        self._cache: dict[str, str] = {}
        self.hits: int = 0
        self.misses: int = 0

    def fetch_data(self, query: str) -> str:
        if query in self._cache:
            self.hits += 1
            return self._cache[query]

        self.misses += 1
        result = self._wrapped.fetch_data(query)
        self._cache[query] = result
        return result


class LoggingDecorator(BaseServiceDecorator):
    """Concrete Decorator recording request/response history."""

    def __init__(self, wrapped: DataService) -> None:
        super().__init__(wrapped)
        self.logs: list[str] = []

    def fetch_data(self, query: str) -> str:
        self.logs.append(f"[LOG START] Executing query: {query}")
        result = self._wrapped.fetch_data(query)
        self.logs.append(f"[LOG END] Query completed: {query}")
        return result


# ==============================================================================
# 4. Pythonic Twist: Function Decorators via functools.wraps
# ==============================================================================
def rate_limit(max_per_second: float) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Pythonic decorator syntax: Enhances callable behavior via higher-order functions."""
    min_interval = 1.0 / max_per_second
    last_called: list[float] = [0.0]

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            elapsed = time.monotonic() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.monotonic()
            return result

        return wrapper

    return decorator


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    raw_service = RemoteDatabaseService()

    # Stack decorators dynamically: Raw -> Cached -> Logged
    cached_service = CachingDecorator(raw_service)
    pipeline = LoggingDecorator(cached_service)

    # First call: Cache miss, executed via DB
    res1 = pipeline.fetch_data("SELECT * FROM users")
    print(f"Call 1: {res1}")

    # Second call: Cache hit, DB bypassed
    res2 = pipeline.fetch_data("SELECT * FROM users")
    print(f"Call 2: {res2}")

    print(f"Cache Hits: {cached_service.hits}, Misses: {cached_service.misses}")
    print(f"Recorded Logs: {pipeline.logs}")

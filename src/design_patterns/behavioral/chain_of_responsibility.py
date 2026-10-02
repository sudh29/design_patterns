"""Chain of Responsibility Design Pattern.

Classification: Behavioral
Intent:
    Avoid coupling the sender of a request to its receiver by giving more than
    one object a chance to handle the request. Chain the receiving objects and
    pass the request along the chain until an object handles it.

Motivation & Real-World Analogy:
    In HTTP web application servers, incoming requests pass through a sequence of
    middleware filters before hitting the core endpoint handler:
    1. Authentication (verifies bearer token / credentials)
    2. Rate Limiting (verifies request quota)
    3. Content Validation (verifies payload schema)
    If any middleware encounters a failure, the pipeline is terminated immediately
    without reaching downstream handlers.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class RequestContext {
            +token: str
            +ip_address: str
            +body: dict
        }
        class MiddlewareHandler {
            <<protocol>>
            +set_next(handler: MiddlewareHandler) MiddlewareHandler
            +handle(request: RequestContext) bool
        }
        class BaseMiddleware {
            <<abstract>>
            -_next_handler: MiddlewareHandler | None
            +set_next(handler: MiddlewareHandler) MiddlewareHandler
            +handle(request: RequestContext) bool
        }
        class AuthMiddleware {
            +handle(request: RequestContext) bool
        }
        class RateLimitMiddleware {
            +handle(request: RequestContext) bool
        }
        class SchemaValidationMiddleware {
            +handle(request: RequestContext) bool
        }
        MiddlewareHandler <|.. BaseMiddleware
        BaseMiddleware <|-- AuthMiddleware
        BaseMiddleware <|-- RateLimitMiddleware
        BaseMiddleware <|-- SchemaValidationMiddleware
        BaseMiddleware o--> MiddlewareHandler : passes along
    ```
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self


@dataclass
class HttpRequestContext:
    """The request object passed along the chain."""

    path: str
    token: str | None = None
    ip_address: str = "127.0.0.1"
    payload: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class BaseMiddleware:
    """Base Handler providing chaining infrastructure."""

    def __init__(self) -> None:
        self._next_handler: BaseMiddleware | None = None

    def set_next(self, handler: BaseMiddleware) -> BaseMiddleware:
        self._next_handler = handler
        return handler

    def handle(self, request: HttpRequestContext) -> bool:
        """Default behavior: Pass down the chain if next handler exists."""
        if self._next_handler:
            return self._next_handler.handle(request)
        return True


class AuthenticationMiddleware(BaseMiddleware):
    """Verifies that an authorized Bearer token is provided."""

    def __init__(self, valid_tokens: set[str]) -> None:
        super().__init__()
        self._valid_tokens = valid_tokens

    def handle(self, request: HttpRequestContext) -> bool:
        if not request.token or request.token not in self._valid_tokens:
            request.errors.append("401 Unauthorized: Invalid or missing bearer token")
            return False
        return super().handle(request)


class RateLimitMiddleware(BaseMiddleware):
    """Enforces request limits per IP address."""

    def __init__(self, max_requests_per_ip: int) -> None:
        super().__init__()
        self._max = max_requests_per_ip
        self._counts: dict[str, int] = {}

    def handle(self, request: HttpRequestContext) -> bool:
        current = self._counts.get(request.ip_address, 0)
        if current >= self._max:
            request.errors.append(
                f"429 Too Many Requests: Rate limit exceeded for {request.ip_address}"
            )
            return False
        self._counts[request.ip_address] = current + 1
        return super().handle(request)


class SchemaValidationMiddleware(BaseMiddleware):
    """Validates that mandatory fields are present in the JSON payload."""

    def __init__(self, required_fields: set[str]) -> None:
        super().__init__()
        self._required_fields = required_fields

    def handle(self, request: HttpRequestContext) -> bool:
        missing = self._required_fields - set(request.payload.keys())
        if missing:
            request.errors.append(f"400 Bad Request: Missing required fields: {sorted(missing)}")
            return False
        return super().handle(request)


# ==============================================================================
# Pipeline Builder Convenience Helper
# ==============================================================================
class MiddlewarePipeline:
    """Convenience pipeline builder connecting handlers fluently."""

    def __init__(self) -> None:
        self._first: BaseMiddleware | None = None
        self._last: BaseMiddleware | None = None

    def add(self, handler: BaseMiddleware) -> Self:
        if not self._first:
            self._first = handler
            self._last = handler
        else:
            assert self._last is not None
            self._last.set_next(handler)
            self._last = handler
        return self

    def execute(self, request: HttpRequestContext) -> bool:
        if not self._first:
            return True
        return self._first.handle(request)


# ==============================================================================
# Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    pipeline = (
        MiddlewarePipeline()
        .add(AuthenticationMiddleware(valid_tokens={"secret-token-xyz"}))
        .add(RateLimitMiddleware(max_requests_per_ip=2))
        .add(SchemaValidationMiddleware(required_fields={"username", "email"}))
    )

    # Valid request
    req1 = HttpRequestContext(
        path="/api/profile",
        token="secret-token-xyz",
        ip_address="192.168.1.10",
        payload={"username": "alice", "email": "alice@corp.com"},
    )
    print(f"Request 1 success: {pipeline.execute(req1)}, errors: {req1.errors}")

    # Invalid Token request
    req2 = HttpRequestContext(path="/api/profile", token="wrong-token")
    print(f"Request 2 success: {pipeline.execute(req2)}, errors: {req2.errors}")

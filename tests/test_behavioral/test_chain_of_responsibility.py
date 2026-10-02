"""Tests for Chain of Responsibility pattern implementation."""

from design_patterns.behavioral.chain_of_responsibility import (
    AuthenticationMiddleware,
    HttpRequestContext,
    MiddlewarePipeline,
    RateLimitMiddleware,
    SchemaValidationMiddleware,
)


class TestChainOfResponsibility:
    def test_empty_pipeline(self) -> None:
        pipeline = MiddlewarePipeline()
        req = HttpRequestContext(path="/")
        assert pipeline.execute(req) is True

    def test_full_successful_chain(self) -> None:
        pipeline = (
            MiddlewarePipeline()
            .add(AuthenticationMiddleware({"tok123"}))
            .add(RateLimitMiddleware(5))
            .add(SchemaValidationMiddleware({"id"}))
        )
        req = HttpRequestContext(path="/items", token="tok123", payload={"id": 1})
        assert pipeline.execute(req) is True
        assert len(req.errors) == 0

    def test_auth_failure_short_circuits(self) -> None:
        pipeline = (
            MiddlewarePipeline()
            .add(AuthenticationMiddleware({"tok123"}))
            .add(RateLimitMiddleware(1))
        )
        req = HttpRequestContext(path="/admin", token="bad-tok", ip_address="10.0.0.1")
        assert pipeline.execute(req) is False
        assert any("401 Unauthorized" in e for e in req.errors)

    def test_rate_limit_blocking(self) -> None:
        pipeline = (
            MiddlewarePipeline().add(AuthenticationMiddleware({"tok"})).add(RateLimitMiddleware(2))
        )
        req1 = HttpRequestContext(path="/", token="tok", ip_address="1.1.1.1")
        req2 = HttpRequestContext(path="/", token="tok", ip_address="1.1.1.1")
        req3 = HttpRequestContext(path="/", token="tok", ip_address="1.1.1.1")

        assert pipeline.execute(req1) is True
        assert pipeline.execute(req2) is True
        assert pipeline.execute(req3) is False
        assert any("429 Too Many Requests" in e for e in req3.errors)

    def test_schema_validation_failure(self) -> None:
        pipeline = MiddlewarePipeline().add(SchemaValidationMiddleware({"title", "author"}))
        req = HttpRequestContext(path="/books", payload={"title": "Design Patterns"})
        assert pipeline.execute(req) is False
        assert any("Missing required fields: ['author']" in e for e in req.errors)

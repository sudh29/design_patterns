"""Tests for the Builder pattern implementation."""

import json

import pytest

from design_patterns.creational.builder import (
    ConcreteHttpRequestBuilder,
    NaiveHttpRequest,
    PythonicRequestBuilder,
    RequestDirector,
)


class TestNaiveHttpRequest:
    def test_naive_construction(self) -> None:
        req = NaiveHttpRequest("https://example.com")
        assert req.url == "https://example.com"
        assert req.method == "GET"
        assert req.headers == {}


class TestConcreteHttpRequestBuilder:
    def test_minimal_valid_build(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        req = builder.set_url("https://api.test.com/v1").build()
        assert req.url == "https://api.test.com/v1"
        assert req.method == "GET"
        assert req.timeout == 30.0

    def test_missing_url_raises_error(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        with pytest.raises(ValueError, match="Cannot build HttpRequest without a valid URL"):
            builder.build()

    def test_invalid_url_scheme_raises_error(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            builder.set_url("ftp://files.example.com")

    def test_invalid_http_method(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        with pytest.raises(ValueError, match="Invalid HTTP method"):
            builder.set_method("INVALID")

    def test_get_with_body_invariant_violation(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        builder.set_url("https://api.test.com").set_method("GET").set_body(b"payload")
        with pytest.raises(ValueError, match="HTTP GET requests cannot contain a request body"):
            builder.build()

    def test_invalid_timeout(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        with pytest.raises(ValueError, match="Timeout must be strictly positive"):
            builder.set_timeout(-5.0)

    def test_invalid_retries(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        with pytest.raises(ValueError, match="Max retries cannot be negative"):
            builder.set_max_retries(-1)

    def test_full_fluent_configuration(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        req = (
            builder.set_url("https://service.org/data")
            .set_method("POST")
            .add_header("X-API-Key", "secret-123")
            .add_param("filter", "active")
            .set_body(b'{"query": "all"}')
            .set_timeout(5.0)
            .set_verify_ssl(False)
            .set_max_retries(2)
            .build()
        )
        assert req.headers["X-API-Key"] == "secret-123"
        assert req.params["filter"] == "active"
        assert req.body == b'{"query": "all"}'
        assert req.verify_ssl is False
        assert req.max_retries == 2


class TestRequestDirector:
    def test_construct_json_get(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        director = RequestDirector(builder)
        req = director.construct_json_get("https://api.test.com/users")
        assert req.method == "GET"
        assert req.headers["Accept"] == "application/json"

    def test_construct_json_post(self) -> None:
        builder = ConcreteHttpRequestBuilder()
        director = RequestDirector(builder)
        payload = {"name": "Antigravity", "active": True}
        req = director.construct_json_post("https://api.test.com/projects", payload)
        assert req.method == "POST"
        assert req.headers["Content-Type"] == "application/json"
        assert req.body is not None
        assert json.loads(req.body.decode("utf-8")) == payload


class TestPythonicRequestBuilder:
    def test_pythonic_chain(self) -> None:
        res = (
            PythonicRequestBuilder("https://example.com")
            .method("PUT")
            .header("X-Custom", "1")
            .build()
        )
        assert res["url"] == "https://example.com"
        assert res["method"] == "PUT"
        assert res["headers"] == {"X-Custom": "1"}

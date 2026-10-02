"""Global test configuration and fixtures."""

import logging

import pytest


@pytest.fixture(autouse=True)
def configure_caplog(caplog: pytest.LogCaptureFixture) -> None:
    """Sets default capture log level for testing logger output across all patterns."""
    caplog.set_level(logging.INFO)

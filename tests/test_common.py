"""Tests for common utilities."""

import logging

from design_patterns.common.logger import setup_logger


def test_setup_logger() -> None:
    logger = setup_logger("test_common_logger")
    assert logger.level == logging.INFO
    assert len(logger.handlers) >= 1

    # Calling again returns same logger without duplicating handlers
    handler_count = len(logger.handlers)
    logger2 = setup_logger("test_common_logger")
    assert logger2 is logger
    assert len(logger2.handlers) == handler_count

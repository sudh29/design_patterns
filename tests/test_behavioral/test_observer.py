"""Tests for the Observer pattern implementation."""

import pytest

from design_patterns.behavioral.observer import (
    AlgorithmicTradingBot,
    AuditLogger,
    StockTicker,
)


class TestObserverPattern:
    def test_ticker_invalid_price(self) -> None:
        ticker = StockTicker("AAPL", 150.0)
        with pytest.raises(ValueError, match="Stock price must be positive"):
            ticker.set_price(-1.0)

    def test_subscribe_and_notification(self) -> None:
        ticker = StockTicker("AAPL", 150.0)
        bot = AlgorithmicTradingBot(target_buy_price=140.0)
        audit = AuditLogger()

        ticker.subscribe(bot)
        ticker.subscribe(audit)
        assert ticker.subscriber_count() == 2

        ticker.set_price(145.0)
        assert len(audit.history) == 1
        assert audit.history[0] == ("AAPL", 145.0)
        assert len(bot.orders) == 0  # Not low enough

        ticker.set_price(139.0)
        assert len(audit.history) == 2
        assert len(bot.orders) == 1
        assert "BUY 100 shares of AAPL at $139.00" in bot.orders[0]

    def test_unsubscribe(self) -> None:
        ticker = StockTicker("MSFT", 300.0)
        audit = AuditLogger()

        ticker.subscribe(audit)
        ticker.set_price(310.0)
        assert len(audit.history) == 1

        ticker.unsubscribe(audit)
        assert ticker.subscriber_count() == 0

        ticker.set_price(320.0)
        assert len(audit.history) == 1  # No new updates received

    def test_identical_price_no_notification(self) -> None:
        ticker = StockTicker("TSLA", 200.0)
        audit = AuditLogger()
        ticker.subscribe(audit)

        ticker.set_price(200.0)  # Same price
        assert len(audit.history) == 0

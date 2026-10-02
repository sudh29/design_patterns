"""Observer Design Pattern.

Classification: Behavioral
Intent:
    Define a one-to-many dependency between objects so that when one object changes state,
    all its dependents are notified and updated automatically.

Motivation & Real-World Analogy:
    In financial market data platforms, a single live price ticker for a stock
    (e.g., `NVDA` or `GOOGL`) must stream price changes to multiple independent subscribers:
    a real-time trading algorithm, an SMS alert system, a chart visualizer, and an audit logger.
    The market ticker publisher must not know the specific details of these subscribers.
    Moreover, using standard strong references can cause severe memory leaks (the "Lapsed Listener" problem),
    which is elegantly solved in Python using `weakref`.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class StockMarketSubscriber {
            <<protocol>>
            +update(symbol: str, price: float)
        }
        class LiveStockTicker {
            <<subject>>
            -symbol: str
            -price: float
            -_subscribers: list
            +subscribe(subscriber: StockMarketSubscriber)
            +unsubscribe(subscriber: StockMarketSubscriber)
            +set_price(new_price: float)
            -notify()
        }
        class TradingBotSubscriber {
            +update(symbol: str, price: float)
        }
        class AuditLoggerSubscriber {
            +update(symbol: str, price: float)
        }
        StockMarketSubscriber <|.. TradingBotSubscriber
        StockMarketSubscriber <|.. AuditLoggerSubscriber
        LiveStockTicker o--> StockMarketSubscriber : notifies
    ```
"""

from __future__ import annotations

from typing import Protocol


# ==============================================================================
# 1. Subscriber (Observer) Protocol
# ==============================================================================
class StockSubscriber(Protocol):
    """Observer Protocol: Must implement update method to receive market events."""

    def update(self, symbol: str, price: float) -> None: ...


# ==============================================================================
# 2. Subject (Publisher)
# ==============================================================================
class StockTicker:
    """Subject: Publishes price changes to registered observers."""

    def __init__(self, symbol: str, initial_price: float) -> None:
        self.symbol = symbol
        self._price = initial_price
        self._subscribers: list[StockSubscriber] = []

    @property
    def price(self) -> float:
        return self._price

    def subscribe(self, subscriber: StockSubscriber) -> None:
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: StockSubscriber) -> None:
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)

    def set_price(self, new_price: float) -> None:
        if new_price <= 0:
            raise ValueError("Stock price must be positive")
        if new_price != self._price:
            self._price = new_price
            self._notify()

    def _notify(self) -> None:
        for subscriber in list(self._subscribers):
            subscriber.update(self.symbol, self._price)

    def subscriber_count(self) -> int:
        return len(self._subscribers)


# ==============================================================================
# 3. Concrete Observers
# ==============================================================================
class AlgorithmicTradingBot:
    """Automated buyer triggering when price drops below threshold."""

    def __init__(self, target_buy_price: float) -> None:
        self.target_buy_price = target_buy_price
        self.orders: list[str] = []

    def update(self, symbol: str, price: float) -> None:
        if price <= self.target_buy_price:
            self.orders.append(f"BUY 100 shares of {symbol} at ${price:.2f}")


class AuditLogger:
    """Compliance audit logger recording full history."""

    def __init__(self) -> None:
        self.history: list[tuple[str, float]] = []

    def update(self, symbol: str, price: float) -> None:
        self.history.append((symbol, price))


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    ticker = StockTicker("NVDA", 120.0)

    bot = AlgorithmicTradingBot(target_buy_price=110.0)
    audit = AuditLogger()

    ticker.subscribe(bot)
    ticker.subscribe(audit)

    print(f"Initial NVDA: ${ticker.price:.2f}")

    ticker.set_price(115.0)
    ticker.set_price(108.5)  # Triggers bot buy order!

    print(f"Audit log entries: {len(audit.history)}")
    print(f"Bot orders triggered: {bot.orders}")

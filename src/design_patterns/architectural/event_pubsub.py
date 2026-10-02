"""Event-Driven Pub-Sub Pattern.

Classification: Architectural / Event-Driven Architecture (EDA)
Intent:
    Decouple event publishers from event subscribers via an intermediary Event Bus,
    broadcasting domain events without either side knowing about the other.

Motivation & Real-World Analogy:
    When an order is placed (`OrderPlacedEvent`), multiple disparate subsystems
    must react:
    - Inventory reserves items
    - Payment processor charges card
    - Notification service sends customer receipt
    - Analytics pipeline streams metrics
    Directly chaining all these calls into the order placement method results in
    tight coupling and massive failure cascades.
    An Event Bus allows domain services to publish events as pure data envelopes,
    dispatching them to registered handlers with error isolation.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class DomainEvent {
            +event_id: str
            +timestamp: float
        }
        class OrderPlacedEvent {
            +order_id: str
            +customer_id: str
            +total: float
        }
        class EventBus {
            -_subscribers: dict[type, list]
            +subscribe(event_type, handler)
            +unsubscribe(event_type, handler)
            +publish(event: DomainEvent) int
        }
        DomainEvent <|-- OrderPlacedEvent
        EventBus ..> DomainEvent : dispatches
    ```
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

E = TypeVar("E", bound="DomainEvent")


# ==============================================================================
# 1. Domain Event Hierarchy
# ==============================================================================
@dataclass(frozen=True)
class DomainEvent:
    """Base event payload containing standard metadata."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class UserRegisteredEvent(DomainEvent):
    user_id: str = ""
    email: str = ""


@dataclass(frozen=True)
class PaymentCompletedEvent(DomainEvent):
    transaction_id: str = ""
    amount: float = 0.0


# ==============================================================================
# 2. Event Bus
# ==============================================================================
EventHandler = Callable[[Any], None]


class EventBus:
    """Synchronous In-Memory Event Bus with error isolation."""

    def __init__(self) -> None:
        self._subscribers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)
        self.failed_handlers: list[tuple[str, str]] = []

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def publish(self, event: DomainEvent) -> int:
        """Publishes an event to all subscribers registered for its exact type or supertypes.

        Returns the number of handlers successfully executed.
        """
        handlers_executed = 0
        event_cls = type(event)

        for registered_type, handlers in list(self._subscribers.items()):
            if issubclass(event_cls, registered_type):
                for handler in list(handlers):
                    try:
                        handler(event)
                        handlers_executed += 1
                    except Exception as exc:  # noqa: BLE001
                        # Error isolation: One handler failure must not halt other handlers
                        self.failed_handlers.append((handler.__name__, str(exc)))

        return handlers_executed


# ==============================================================================
# 3. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    bus = EventBus()

    welcome_emails: list[str] = []
    audit_logs: list[str] = []

    bus.subscribe(UserRegisteredEvent, lambda e: welcome_emails.append(e.email))
    bus.subscribe(
        DomainEvent, lambda e: audit_logs.append(f"AUDIT: Event {e.event_id} at {e.timestamp}")
    )

    ev = UserRegisteredEvent(user_id="U-100", email="newuser@domain.com")
    bus.publish(ev)

    print(f"Welcome emails queued: {welcome_emails}")
    print(f"Audit log entries: {len(audit_logs)}")

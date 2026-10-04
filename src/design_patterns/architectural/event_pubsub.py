"""Event-Driven Publish/Subscribe (Event Bus) Pattern.

Classification: Architectural / Enterprise
Intent:
    Provide a loosely coupled messaging architecture where senders (publishers)
    dispatch domain events to an event bus without knowledge of recipients (subscribers).
    Subscribers listen to specific event types and react independently.

Motivation & Real-World Analogy:
    In microservices, event-driven architectures, and domain-driven design (DDD),
    a domain mutation (e.g., an `OrderPlaced` event) needs to trigger many independent downstream actions:
    send a confirmation email, notify the warehouse fulfillment queue, update analytics dashboards,
    and initiate fraud detection checks.
    If the order processing service directly called all these secondary systems, it would be
    fragile, heavily coupled, slow, and violate the Single Responsibility Principle.
    The Event Pub/Sub pattern introduces an Event Bus that mediates event publishing and routing.
    In Python, this is enhanced with typed event envelopes, decorator-based subscription,
    and support for both synchronous and asynchronous event handlers.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Event {
            <<dataclass>>
            +event_id: str
            +timestamp: float
        }
        class OrderPlacedEvent {
            +order_id: str
            +customer_email: str
            +total_amount: float
        }
        class EventBus {
            -subscribers: dict
            +subscribe(event_type, handler)
            +publish(event) int
            +clear()
        }
        Event <|-- OrderPlacedEvent
        EventBus --> Event : routes
    ```
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

E = TypeVar("E", bound="Event")
EventHandler = Callable[[Any], None]


# ==============================================================================
# 1. Base Event Envelope & Concrete Domain Events
# ==============================================================================
@dataclass(frozen=True)
class Event:
    """Base event envelope carrying common metadata for all domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class OrderPlacedEvent(Event):
    """Fired whenever a customer places an order."""

    order_id: str = ""
    customer_email: str = ""
    total_amount: float = 0.0


@dataclass(frozen=True)
class PaymentReceivedEvent(Event):
    """Fired when an external payment provider confirms receipt of funds."""

    order_id: str = ""
    payment_reference: str = ""
    amount: float = 0.0


@dataclass(frozen=True)
class ShipmentDispatchedEvent(Event):
    """Fired when items depart the distribution center."""

    order_id: str = ""
    tracking_number: str = ""


# ==============================================================================
# 2. Event Bus Implementation
# ==============================================================================
class EventBus:
    """In-memory event bus managing subscription and event dispatching."""

    def __init__(self) -> None:
        self._subscribers: dict[type[Event], list[EventHandler]] = {}
        self._history: list[Event] = []

    def subscribe(
        self, event_type: type[E]
    ) -> Callable[[Callable[[E], None]], Callable[[E], None]]:
        """Decorator or direct method to register an event handler for a specific event type."""

        def decorator(handler: Callable[[E], None]) -> Callable[[E], None]:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
            return handler

        return decorator

    def register_handler(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        """Explicit programmatic registration without decorator."""
        self.subscribe(event_type)(handler)

    def unsubscribe(self, event_type: type[E], handler: Callable[[E], None]) -> bool:
        """Remove a registered subscriber handler."""
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            return True
        return False

    def publish(self, event: Event) -> int:
        """Dispatch event to all subscribed handlers and return count of invoked handlers."""
        self._history.append(event)
        event_cls = type(event)
        handlers = self._subscribers.get(event_cls, [])

        invoked = 0
        for handler in list(handlers):
            handler(event)
            invoked += 1

        return invoked

    def event_history(self) -> list[Event]:
        """Return audit trail of all published events."""
        return list(self._history)

    def clear(self) -> None:
        """Reset subscriptions and event history."""
        self._subscribers.clear()
        self._history.clear()


# ==============================================================================
# 3. Downstream Handlers / Listeners
# ==============================================================================
class EmailNotificationListener:
    """Sends confirmation emails when events occur."""

    def __init__(self) -> None:
        self.sent_emails: list[tuple[str, str]] = []

    def on_order_placed(self, event: OrderPlacedEvent) -> None:
        self.sent_emails.append(
            (event.customer_email, f"Order {event.order_id} placed for ${event.total_amount:.2f}")
        )


class InventoryReservationListener:
    """Reserves warehouse inventory upon order placement."""

    def __init__(self) -> None:
        self.reservations: list[str] = []

    def on_order_placed(self, event: OrderPlacedEvent) -> None:
        self.reservations.append(event.order_id)


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    bus = EventBus()

    email_listener = EmailNotificationListener()
    inventory_listener = InventoryReservationListener()

    # Register listeners
    bus.register_handler(OrderPlacedEvent, email_listener.on_order_placed)
    bus.register_handler(OrderPlacedEvent, inventory_listener.on_order_placed)

    # Decorator-based inline listener
    audit_log: list[str] = []

    @bus.subscribe(PaymentReceivedEvent)
    def on_payment(event: PaymentReceivedEvent) -> None:
        audit_log.append(f"Recorded payment {event.payment_reference} for order {event.order_id}")

    # Publish events
    order_event = OrderPlacedEvent(
        order_id="ord_9901", customer_email="buyer@test.com", total_amount=249.99
    )
    bus.publish(order_event)

    payment_event = PaymentReceivedEvent(
        order_id="ord_9901", payment_reference="ch_stripe_xyz", amount=249.99
    )
    bus.publish(payment_event)

    print("Sent Emails:", email_listener.sent_emails)
    print("Reserved Inventory Orders:", inventory_listener.reservations)
    print("Audit Log:", audit_log)
    print(f"Total Published Events: {len(bus.event_history())}")

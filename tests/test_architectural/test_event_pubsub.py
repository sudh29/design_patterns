"""Tests for Event-Driven Pub/Sub pattern implementation."""

import time

from design_patterns.architectural.event_pubsub import (
    EmailNotificationListener,
    Event,
    EventBus,
    InventoryReservationListener,
    OrderPlacedEvent,
    PaymentReceivedEvent,
    ShipmentDispatchedEvent,
)


class TestEventBusPubSub:
    def test_single_event_multiple_subscribers(self) -> None:
        bus = EventBus()
        email_listener = EmailNotificationListener()
        inventory_listener = InventoryReservationListener()

        bus.register_handler(OrderPlacedEvent, email_listener.on_order_placed)
        bus.register_handler(OrderPlacedEvent, inventory_listener.on_order_placed)

        evt = OrderPlacedEvent(order_id="101", customer_email="user@test.com", total_amount=150.0)
        invoked = bus.publish(evt)

        assert invoked == 2
        assert len(email_listener.sent_emails) == 1
        assert email_listener.sent_emails[0][0] == "user@test.com"
        assert inventory_listener.reservations == ["101"]

    def test_decorator_subscription(self) -> None:
        bus = EventBus()
        captured: list[PaymentReceivedEvent] = []

        @bus.subscribe(PaymentReceivedEvent)
        def handle_payment(e: PaymentReceivedEvent) -> None:
            captured.append(e)

        evt = PaymentReceivedEvent(order_id="101", payment_reference="ref_1", amount=150.0)
        bus.publish(evt)

        assert len(captured) == 1
        assert captured[0].payment_reference == "ref_1"

    def test_unsubscribe_handler(self) -> None:
        bus = EventBus()
        messages: list[str] = []

        def handler(e: OrderPlacedEvent) -> None:
            messages.append(e.order_id)

        bus.register_handler(OrderPlacedEvent, handler)
        evt = OrderPlacedEvent(order_id="1", customer_email="a@b.com", total_amount=10.0)
        bus.publish(evt)
        assert len(messages) == 1

        # Unsubscribe
        assert bus.unsubscribe(OrderPlacedEvent, handler) is True
        # False on repeated unsubscribe
        assert bus.unsubscribe(OrderPlacedEvent, handler) is False

        bus.publish(evt)
        assert len(messages) == 1  # Not invoked again

    def test_publish_without_subscribers(self) -> None:
        bus = EventBus()
        evt = ShipmentDispatchedEvent(order_id="999", tracking_number="TRACK123")
        invoked = bus.publish(evt)

        assert invoked == 0
        assert len(bus.event_history()) == 1

    def test_event_envelope_metadata(self) -> None:
        before = time.time()
        evt = Event()
        after = time.time()

        assert len(evt.event_id) > 10
        assert before <= evt.timestamp <= after

    def test_clear_bus(self) -> None:
        bus = EventBus()
        bus.register_handler(OrderPlacedEvent, lambda _: None)
        bus.publish(OrderPlacedEvent(order_id="1", customer_email="a", total_amount=1))

        assert len(bus.event_history()) == 1
        bus.clear()
        assert len(bus.event_history()) == 0
        assert bus.publish(OrderPlacedEvent(order_id="2", customer_email="b", total_amount=2)) == 0

"""Tests for Event-Driven Pub-Sub pattern implementation."""

from design_patterns.architectural.event_pubsub import (
    DomainEvent,
    EventBus,
    PaymentCompletedEvent,
    UserRegisteredEvent,
)


class TestEventBus:
    def test_publish_to_single_subscriber(self) -> None:
        bus = EventBus()
        received = []

        def on_user_registered(event: UserRegisteredEvent) -> None:
            received.append(event.email)

        bus.subscribe(UserRegisteredEvent, on_user_registered)
        bus.publish(UserRegisteredEvent(user_id="U1", email="test@test.com"))

        assert received == ["test@test.com"]

    def test_polymorphic_hierarchy_dispatch(self) -> None:
        bus = EventBus()
        all_events = []

        # Subscribing to base DomainEvent captures all events
        bus.subscribe(DomainEvent, lambda e: all_events.append(e.event_id))

        bus.publish(UserRegisteredEvent(user_id="U1", email="a@b.com"))
        bus.publish(PaymentCompletedEvent(transaction_id="TX1", amount=99.0))

        assert len(all_events) == 2

    def test_unsubscribe(self) -> None:
        bus = EventBus()
        counter = [0]

        def handler(event: UserRegisteredEvent) -> None:
            counter[0] += 1

        bus.subscribe(UserRegisteredEvent, handler)
        bus.publish(UserRegisteredEvent(user_id="U1"))
        assert counter[0] == 1

        bus.unsubscribe(UserRegisteredEvent, handler)
        bus.publish(UserRegisteredEvent(user_id="U2"))
        assert counter[0] == 1  # Unsubscribed, so not invoked

    def test_error_isolation_across_handlers(self) -> None:
        bus = EventBus()
        successful = []

        def failing_handler(event: DomainEvent) -> None:
            raise RuntimeError("Database connection crashed")

        def working_handler(event: DomainEvent) -> None:
            successful.append(event.event_id)

        bus.subscribe(DomainEvent, failing_handler)
        bus.subscribe(DomainEvent, working_handler)

        count = bus.publish(DomainEvent())

        # One succeeded, one failed
        assert count == 1
        assert len(successful) == 1
        assert len(bus.failed_handlers) == 1
        assert "Database connection crashed" in bus.failed_handlers[0][1]

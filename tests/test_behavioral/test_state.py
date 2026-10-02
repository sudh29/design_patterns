"""Tests for the State pattern implementation."""

import pytest

from design_patterns.behavioral.state import Order


class TestStatePattern:
    def test_happy_path_lifecycle(self) -> None:
        order = Order()
        assert order.state_name == "DRAFT"

        order.add_item("Laptop")
        order.pay(1200.0)
        assert order.state_name == "PAID"
        assert order.paid_amount == 1200.0

        order.ship("DHL-12345")
        assert order.state_name == "SHIPPED"
        assert order.tracking_number == "DHL-12345"

    def test_cannot_pay_empty_draft(self) -> None:
        order = Order()
        with pytest.raises(ValueError, match="Cannot pay for an empty order"):
            order.pay(100.0)

    def test_cannot_ship_draft(self) -> None:
        order = Order()
        order.add_item("Book")
        with pytest.raises(ValueError, match="Cannot ship an unpaid draft order"):
            order.ship("TRACK123")

    def test_cannot_modify_items_after_paid(self) -> None:
        order = Order()
        order.add_item("Headphones")
        order.pay(50.0)

        with pytest.raises(ValueError, match="Cannot add items to an already paid order"):
            order.add_item("Mouse")

    def test_cancel_paid_order_triggers_refund(self) -> None:
        order = Order()
        order.add_item("Monitor")
        order.pay(300.0)
        assert order.paid_amount == 300.0

        order.cancel()
        assert order.state_name == "CANCELLED"
        assert order.paid_amount == 0.0

    def test_cannot_cancel_shipped_order(self) -> None:
        order = Order()
        order.add_item("Phone")
        order.pay(800.0)
        order.ship("UPS-99")

        with pytest.raises(ValueError, match="Cannot cancel an order that is already in transit"):
            order.cancel()

    def test_cancelled_order_rejects_all_operations(self) -> None:
        order = Order()
        order.cancel()
        assert order.state_name == "CANCELLED"

        with pytest.raises(ValueError, match="Order is cancelled"):
            order.add_item("Item")

        with pytest.raises(ValueError, match="Order is cancelled"):
            order.pay(10.0)

        with pytest.raises(ValueError, match="Order is cancelled"):
            order.ship("TRACK")

        with pytest.raises(ValueError, match="Order is already cancelled"):
            order.cancel()

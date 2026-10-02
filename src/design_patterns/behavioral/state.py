"""State Design Pattern.

Classification: Behavioral
Intent:
    Allow an object to alter its behavior when its internal state changes.
    The object will appear to change its class.

Motivation & Real-World Analogy:
    In an e-commerce fulfillment platform, an Order progresses through distinct
    lifecycle stages: `Draft` -> `Placed` -> `Paid` -> `Shipped` -> `Delivered` (or `Cancelled`).
    In a naive implementation, every single method (`add_item`, `pay`, `ship`, `cancel`)
    is dominated by massive `if self.state == ...` branches, leading to spaghetti logic
    and invalid state transitions.
    The State pattern encapsulates each lifecycle state into its own class, where
    each state knows which operations are valid and how to transition to the next state.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class OrderState {
            <<protocol>>
            +add_item(order: Order, item: str)
            +pay(order: Order, amount: float)
            +ship(order: Order, tracking: str)
            +cancel(order: Order)
        }
        class Order {
            -state: OrderState
            -items: list[str]
            -paid_amount: float
            -tracking_number: str | None
            +transition_to(state: OrderState)
            +add_item(item: str)
            +pay(amount: float)
            +ship(tracking: str)
            +cancel()
        }
        class DraftState {
            +add_item()
            +pay()
        }
        class PaidState {
            +ship()
            +cancel()
        }
        class ShippedState {
            +deliver()
        }
        OrderState <|.. DraftState
        OrderState <|.. PaidState
        OrderState <|.. ShippedState
        Order o--> OrderState : delegates behavior
    ```
"""

from __future__ import annotations

from typing import Protocol


# ==============================================================================
# 1. State Protocol
# ==============================================================================
class OrderState(Protocol):
    """State Interface: Defines behaviors and allowable transitions."""

    @property
    def name(self) -> str: ...
    def add_item(self, order: Order, item: str) -> None: ...
    def pay(self, order: Order, amount: float) -> None: ...
    def ship(self, order: Order, tracking: str) -> None: ...
    def cancel(self, order: Order) -> None: ...


# ==============================================================================
# 2. Context: Order
# ==============================================================================
class Order:
    """Context: Maintains current state and delegates lifecycle operations to it."""

    def __init__(self) -> None:
        self.items: list[str] = []
        self.paid_amount: float = 0.0
        self.tracking_number: str | None = None
        self._state: OrderState = DraftState()

    @property
    def state_name(self) -> str:
        return self._state.name

    def transition_to(self, state: OrderState) -> None:
        self._state = state

    def add_item(self, item: str) -> None:
        self._state.add_item(self, item)

    def pay(self, amount: float) -> None:
        self._state.pay(self, amount)

    def ship(self, tracking: str) -> None:
        self._state.ship(self, tracking)

    def cancel(self) -> None:
        self._state.cancel(self)


# ==============================================================================
# 3. Concrete State Implementations
# ==============================================================================
class DraftState:
    """Initial State: Items can be added; payment moves order to Paid."""

    @property
    def name(self) -> str:
        return "DRAFT"

    def add_item(self, order: Order, item: str) -> None:
        order.items.append(item)

    def pay(self, order: Order, amount: float) -> None:
        if not order.items:
            raise ValueError("Cannot pay for an empty order")
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        order.paid_amount = amount
        order.transition_to(PaidState())

    def ship(self, order: Order, tracking: str) -> None:
        raise ValueError("Cannot ship an unpaid draft order")

    def cancel(self, order: Order) -> None:
        order.transition_to(CancelledState())


class PaidState:
    """Paid State: Items cannot be changed; order can be shipped or cancelled with refund."""

    @property
    def name(self) -> str:
        return "PAID"

    def add_item(self, order: Order, item: str) -> None:
        raise ValueError("Cannot add items to an already paid order")

    def pay(self, order: Order, amount: float) -> None:
        raise ValueError("Order is already paid")

    def ship(self, order: Order, tracking: str) -> None:
        order.tracking_number = tracking
        order.transition_to(ShippedState())

    def cancel(self, order: Order) -> None:
        # Trigger refund
        order.paid_amount = 0.0
        order.transition_to(CancelledState())


class ShippedState:
    """Shipped State: Package is in transit; cannot be cancelled without return flow."""

    @property
    def name(self) -> str:
        return "SHIPPED"

    def add_item(self, order: Order, item: str) -> None:
        raise ValueError("Cannot add items to shipped order")

    def pay(self, order: Order, amount: float) -> None:
        raise ValueError("Cannot pay for already shipped order")

    def ship(self, order: Order, tracking: str) -> None:
        raise ValueError("Order has already been shipped")

    def cancel(self, order: Order) -> None:
        raise ValueError("Cannot cancel an order that is already in transit")


class CancelledState:
    """Terminal State: No further operations permitted."""

    @property
    def name(self) -> str:
        return "CANCELLED"

    def add_item(self, order: Order, item: str) -> None:
        raise ValueError("Order is cancelled")

    def pay(self, order: Order, amount: float) -> None:
        raise ValueError("Order is cancelled")

    def ship(self, order: Order, tracking: str) -> None:
        raise ValueError("Order is cancelled")

    def cancel(self, order: Order) -> None:
        raise ValueError("Order is already cancelled")


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    order = Order()
    print(f"Initial State: {order.state_name}")

    order.add_item("Mechanical Keyboard")
    order.add_item("USB-C Cable")
    print(f"Items added: {order.items}")

    order.pay(150.0)
    print(f"State after payment: {order.state_name}")

    order.ship("FEDEX-8839210")
    print(f"State after shipping: {order.state_name} (Tracking: {order.tracking_number})")

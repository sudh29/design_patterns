"""Strategy Design Pattern.

Classification: Behavioral
Intent:
    Define a family of algorithms, encapsulate each one, and make them interchangeable.
    Strategy lets the algorithm vary independently of clients that use it.

Motivation & Real-World Analogy:
    In an e-commerce checkout system, discount calculation logic changes frequently:
    standard retail pricing, Black Friday 20% off, VIP tier discounts, or buy-one-get-one deals.
    Embedding all these calculations inside the `Order` or `CheckoutService` with
    convoluted `if-elif-else` branches creates fragility and violates the Open/Closed Principle.
    The Strategy pattern abstracts the pricing calculation behind a pluggable interface.
    In Python, because functions are first-class citizens, a strategy can be either
    a class hierarchy or simply a callable function (`Callable[[float], float]`).

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class DiscountStrategy {
            <<protocol>>
            +apply_discount(total: float) float
        }
        class PercentageDiscount {
            -percentage: float
            +apply_discount(total: float) float
        }
        class FlatDiscount {
            -discount_amount: float
            +apply_discount(total: float) float
        }
        class TieredVolumeDiscount {
            +apply_discount(total: float) float
        }
        class CheckoutCart {
            -strategy: DiscountStrategy
            +total() float
            +calculate_final_price() float
        }
        DiscountStrategy <|.. PercentageDiscount
        DiscountStrategy <|.. FlatDiscount
        DiscountStrategy <|.. TieredVolumeDiscount
        CheckoutCart o--> DiscountStrategy : delegates calculation
    ```
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


# ==============================================================================
# 1. Strategy Protocol & Concrete Class Strategies
# ==============================================================================
class DiscountStrategy(Protocol):
    """Strategy Protocol: Encapsulates algorithm for calculating discounts."""

    def apply_discount(self, total: float) -> float: ...


class PercentageDiscount:
    """Applies a percentage discount (e.g., 0.15 for 15% off)."""

    def __init__(self, percentage: float) -> None:
        if not (0.0 <= percentage <= 1.0):
            raise ValueError("Percentage must be between 0.0 and 1.0")
        self._percentage = percentage

    def apply_discount(self, total: float) -> float:
        return total * (1.0 - self._percentage)


class FlatDiscount:
    """Applies a flat dollar discount (capped at total price so total cannot be negative)."""

    def __init__(self, discount_amount: float) -> None:
        if discount_amount < 0:
            raise ValueError("Discount amount cannot be negative")
        self._discount_amount = discount_amount

    def apply_discount(self, total: float) -> float:
        return max(0.0, total - self._discount_amount)


class TieredVolumeDiscount:
    """Applies higher discounts for larger totals."""

    def apply_discount(self, total: float) -> float:
        if total > 500.0:
            return total * 0.80  # 20% off over $500
        elif total > 100.0:
            return total * 0.90  # 10% off over $100
        return total


# ==============================================================================
# 2. Context: Checkout Cart
# ==============================================================================
class CheckoutCart:
    """Context that utilizes a DiscountStrategy to compute checkout totals."""

    def __init__(self, strategy: DiscountStrategy | None = None) -> None:
        self._items: list[float] = []
        self._strategy: DiscountStrategy = strategy or (lambda total: total)  # type: ignore[assignment]

    def add_item(self, price: float) -> None:
        if price <= 0:
            raise ValueError("Item price must be positive")
        self._items.append(price)

    def set_strategy(self, strategy: DiscountStrategy) -> None:
        self._strategy = strategy

    def raw_total(self) -> float:
        return sum(self._items)

    def final_price(self) -> float:
        return self._strategy.apply_discount(self.raw_total())


# ==============================================================================
# 3. Pythonic Twist: First-Class Functions as Strategies
# ==============================================================================
PricingFunction = Callable[[float], float]


def apply_vip_club_discount(total: float) -> float:
    """In Python, functions can be used directly as strategies without classes."""
    return total * 0.75  # 25% VIP discount


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    cart = CheckoutCart(strategy=PercentageDiscount(0.10))
    cart.add_item(100.0)
    cart.add_item(200.0)

    print(f"Raw Total:    ${cart.raw_total():.2f}")
    print(f"10% Strategy: ${cart.final_price():.2f}")

    # Switch strategy at runtime to Tiered Volume
    cart.set_strategy(TieredVolumeDiscount())
    cart.add_item(300.0)  # Total now $600 -> qualifies for 20% tier
    print(f"Tiered Strategy: ${cart.final_price():.2f}")

    # Switch to Pythonic Function strategy
    class FuncStrategyAdapter:
        def __init__(self, fn: PricingFunction) -> None:
            self.fn = fn

        def apply_discount(self, total: float) -> float:
            return self.fn(total)

    cart.set_strategy(FuncStrategyAdapter(apply_vip_club_discount))
    print(f"VIP Function Strategy: ${cart.final_price():.2f}")

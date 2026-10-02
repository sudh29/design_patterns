"""Tests for the Strategy pattern implementation."""

import pytest

from design_patterns.behavioral.strategy import (
    CheckoutCart,
    FlatDiscount,
    PercentageDiscount,
    TieredVolumeDiscount,
    apply_vip_club_discount,
)


class TestStrategyPattern:
    def test_percentage_discount(self) -> None:
        cart = CheckoutCart(strategy=PercentageDiscount(0.20))
        cart.add_item(100.0)
        assert cart.final_price() == 80.0

    def test_invalid_percentage(self) -> None:
        with pytest.raises(ValueError, match="Percentage must be between 0.0 and 1.0"):
            PercentageDiscount(1.5)

    def test_flat_discount(self) -> None:
        cart = CheckoutCart(strategy=FlatDiscount(15.0))
        cart.add_item(50.0)
        assert cart.final_price() == 35.0

    def test_flat_discount_capped_at_zero(self) -> None:
        cart = CheckoutCart(strategy=FlatDiscount(100.0))
        cart.add_item(40.0)
        assert cart.final_price() == 0.0

    def test_invalid_flat_discount(self) -> None:
        with pytest.raises(ValueError, match="Discount amount cannot be negative"):
            FlatDiscount(-5.0)

    def test_tiered_volume_discount(self) -> None:
        cart = CheckoutCart(strategy=TieredVolumeDiscount())
        cart.add_item(50.0)
        assert cart.final_price() == 50.0  # < 100: no discount

        cart.add_item(100.0)  # Total 150 -> 10% off
        assert cart.final_price() == 135.0

        cart.add_item(400.0)  # Total 550 -> 20% off
        assert cart.final_price() == 440.0

    def test_runtime_strategy_swapping(self) -> None:
        cart = CheckoutCart(strategy=PercentageDiscount(0.10))
        cart.add_item(100.0)
        assert cart.final_price() == 90.0

        cart.set_strategy(FlatDiscount(20.0))
        assert cart.final_price() == 80.0

    def test_invalid_item_price(self) -> None:
        cart = CheckoutCart()
        with pytest.raises(ValueError, match="Item price must be positive"):
            cart.add_item(-10.0)

    def test_vip_function_strategy(self) -> None:
        from collections.abc import Callable

        class CallableAdapter:
            def __init__(self, fn: Callable[[float], float]) -> None:
                self.fn = fn

            def apply_discount(self, total: float) -> float:
                return self.fn(total)

        cart = CheckoutCart(strategy=CallableAdapter(apply_vip_club_discount))
        cart.add_item(200.0)
        assert cart.final_price() == 150.0

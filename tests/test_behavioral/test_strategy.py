"""Tests for the Strategy pattern implementation."""

import pytest

from design_patterns.behavioral.strategy import (
    CheckoutCart,
    FlatDiscount,
    FuncStrategyAdapter,
    NoDiscount,
    PercentageDiscount,
    TieredVolumeDiscount,
    apply_vip_club_discount,
)


class TestPercentageDiscount:
    def test_standard_discount(self) -> None:
        strategy = PercentageDiscount(0.10)
        assert strategy.apply_discount(100.0) == pytest.approx(90.0)

    def test_zero_discount(self) -> None:
        strategy = PercentageDiscount(0.0)
        assert strategy.apply_discount(200.0) == pytest.approx(200.0)

    def test_full_discount(self) -> None:
        strategy = PercentageDiscount(1.0)
        assert strategy.apply_discount(150.0) == pytest.approx(0.0)

    def test_invalid_percentage_raises(self) -> None:
        with pytest.raises(ValueError, match="Percentage must be between"):
            PercentageDiscount(1.5)

    def test_negative_percentage_raises(self) -> None:
        with pytest.raises(ValueError, match="Percentage must be between"):
            PercentageDiscount(-0.1)


class TestFlatDiscount:
    def test_standard_flat_discount(self) -> None:
        strategy = FlatDiscount(25.0)
        assert strategy.apply_discount(100.0) == pytest.approx(75.0)

    def test_discount_exceeds_total_capped_at_zero(self) -> None:
        strategy = FlatDiscount(200.0)
        assert strategy.apply_discount(100.0) == pytest.approx(0.0)

    def test_zero_flat_discount(self) -> None:
        strategy = FlatDiscount(0.0)
        assert strategy.apply_discount(50.0) == pytest.approx(50.0)

    def test_negative_discount_raises(self) -> None:
        with pytest.raises(ValueError, match="Discount amount cannot be negative"):
            FlatDiscount(-10.0)


class TestTieredVolumeDiscount:
    def test_high_tier_over_500(self) -> None:
        strategy = TieredVolumeDiscount()
        assert strategy.apply_discount(600.0) == pytest.approx(480.0)  # 20% off

    def test_mid_tier_over_100(self) -> None:
        strategy = TieredVolumeDiscount()
        assert strategy.apply_discount(200.0) == pytest.approx(180.0)  # 10% off

    def test_no_discount_under_100(self) -> None:
        strategy = TieredVolumeDiscount()
        assert strategy.apply_discount(50.0) == pytest.approx(50.0)

    def test_boundary_exactly_500(self) -> None:
        strategy = TieredVolumeDiscount()
        assert strategy.apply_discount(500.0) == pytest.approx(450.0)  # 10% tier

    def test_boundary_exactly_100(self) -> None:
        strategy = TieredVolumeDiscount()
        assert strategy.apply_discount(100.0) == pytest.approx(100.0)  # no discount


class TestCheckoutCart:
    def test_default_no_strategy_no_discount(self) -> None:
        cart = CheckoutCart()
        cart.add_item(100.0)
        assert cart.final_price() == pytest.approx(100.0)

    def test_with_percentage_strategy(self) -> None:
        cart = CheckoutCart(strategy=PercentageDiscount(0.15))
        cart.add_item(100.0)
        cart.add_item(100.0)
        assert cart.raw_total() == pytest.approx(200.0)
        assert cart.final_price() == pytest.approx(170.0)

    def test_switch_strategy_at_runtime(self) -> None:
        cart = CheckoutCart(strategy=PercentageDiscount(0.10))
        cart.add_item(200.0)
        assert cart.final_price() == pytest.approx(180.0)

        cart.set_strategy(FlatDiscount(50.0))
        assert cart.final_price() == pytest.approx(150.0)

    def test_negative_item_price_raises(self) -> None:
        cart = CheckoutCart()
        with pytest.raises(ValueError, match="Item price must be positive"):
            cart.add_item(-5.0)

    def test_zero_item_price_raises(self) -> None:
        cart = CheckoutCart()
        with pytest.raises(ValueError, match="Item price must be positive"):
            cart.add_item(0.0)

    def test_empty_cart_total_zero(self) -> None:
        cart = CheckoutCart(strategy=PercentageDiscount(0.10))
        assert cart.raw_total() == pytest.approx(0.0)
        assert cart.final_price() == pytest.approx(0.0)

    def test_func_strategy_adapter(self) -> None:
        cart = CheckoutCart(strategy=FuncStrategyAdapter(apply_vip_club_discount))
        cart.add_item(100.0)
        assert cart.final_price() == pytest.approx(75.0)

    def test_no_discount_explicit(self) -> None:
        strategy = NoDiscount()
        assert strategy.apply_discount(150.0) == pytest.approx(150.0)

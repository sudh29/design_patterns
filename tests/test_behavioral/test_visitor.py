"""Tests for the Visitor pattern implementation."""

import pytest

from design_patterns.behavioral.visitor import (
    CapitalGainsTaxVisitor,
    CryptoHolding,
    LiquidityAssessmentVisitor,
    RealEstateHolding,
    StockHolding,
    estimate_asset_insurance,
)


class TestVisitorPattern:
    def test_capital_gains_tax_visitor(self) -> None:
        stock = StockHolding("MSFT", 10, 200.0, 300.0)  # Profit: 1000 -> 15% = 150
        estate = RealEstateHolding("123 Main St", 200_000.0, False)  # 1.5% = 3000
        crypto = CryptoHolding("ETH", 2.0, 1000.0, 2000.0)  # Profit: 2000 -> 28% = 560

        visitor = CapitalGainsTaxVisitor()
        assert stock.accept(visitor) == 150.0
        assert estate.accept(visitor) == 3000.0
        assert crypto.accept(visitor) == 560.0

    def test_loss_yields_zero_capital_gains(self) -> None:
        loss_stock = StockHolding("BAD", 50, 100.0, 80.0)
        visitor = CapitalGainsTaxVisitor()
        assert loss_stock.accept(visitor) == 0.0

    def test_liquidity_visitor(self) -> None:
        stock = StockHolding("GOOG", 1, 100, 150)
        estate = RealEstateHolding("Apt 4B", 100_000, True)
        crypto = CryptoHolding("SOL", 10, 20, 150)

        visitor = LiquidityAssessmentVisitor()
        assert stock.accept(visitor) == 2.0
        assert estate.accept(visitor) == 90.0
        assert crypto.accept(visitor) == 0.1

    def test_pythonic_singledispatch(self) -> None:
        estate = RealEstateHolding("Villa", 1_000_000, False)
        assert estimate_asset_insurance(estate) == 5000.0

        stock = StockHolding("NVDA", 10, 100, 120)
        assert estimate_asset_insurance(stock) == 0.0

        with pytest.raises(NotImplementedError, match="No insurance estimator registered"):
            estimate_asset_insurance("invalid_string_object")

"""Tests for the Visitor pattern implementation."""

import pytest

from design_patterns.behavioral.visitor import (
    BondAsset,
    CapitalGainsTaxVisitor,
    CryptoAsset,
    MarketValueVisitor,
    PortfolioElement,
    PortfolioVisitor,
    SingleDispatchPortfolioEvaluator,
    StockAsset,
)


class TestMarketValueVisitor:
    def test_stock_valuation(self) -> None:
        stock = StockAsset("NVDA", shares=10.0, current_price=120.0, cost_basis=100.0)
        visitor = MarketValueVisitor()
        assert stock.accept(visitor) == pytest.approx(1200.0)

    def test_bond_valuation(self) -> None:
        bond = BondAsset("CorpBond", par_value=1000.0, coupon_rate=0.06)
        visitor = MarketValueVisitor()
        # 1000 * 1.06 = 1060
        assert bond.accept(visitor) == pytest.approx(1060.0)

    def test_crypto_valuation(self) -> None:
        crypto = CryptoAsset("ETH", amount=2.5, current_price=3000.0, cost_basis=2500.0)
        visitor = MarketValueVisitor()
        assert crypto.accept(visitor) == pytest.approx(7500.0)


class TestCapitalGainsTaxVisitor:
    def test_stock_positive_capital_gain(self) -> None:
        stock = StockAsset("MSFT", shares=10.0, current_price=400.0, cost_basis=300.0)
        visitor = CapitalGainsTaxVisitor(stock_rate=0.15)
        # Gain = (400 - 300) * 10 = 1000; Tax = 1000 * 0.15 = 150
        assert stock.accept(visitor) == pytest.approx(150.0)

    def test_stock_capital_loss_yields_zero_tax(self) -> None:
        stock = StockAsset("LOSS", shares=10.0, current_price=50.0, cost_basis=100.0)
        visitor = CapitalGainsTaxVisitor()
        assert stock.accept(visitor) == pytest.approx(0.0)

    def test_bond_income_tax(self) -> None:
        bond = BondAsset("GovBond", par_value=5000.0, coupon_rate=0.04)
        visitor = CapitalGainsTaxVisitor(bond_income_rate=0.30)
        # Coupon interest = 5000 * 0.04 = 200; Tax = 200 * 0.30 = 60
        assert bond.accept(visitor) == pytest.approx(60.0)

    def test_crypto_capital_gain(self) -> None:
        crypto = CryptoAsset("SOL", amount=10.0, current_price=150.0, cost_basis=100.0)
        visitor = CapitalGainsTaxVisitor(crypto_rate=0.28)
        # Gain = (150 - 100) * 10 = 500; Tax = 500 * 0.28 = 140
        assert crypto.accept(visitor) == pytest.approx(140.0)


class TestExtensibilityWithNewVisitor:
    def test_adding_new_visitor_without_modifying_elements(self) -> None:
        class RiskWeightVisitor:
            def visit_stock(self, element: StockAsset) -> float:
                return 1.2

            def visit_bond(self, element: BondAsset) -> float:
                return 0.4

            def visit_crypto(self, element: CryptoAsset) -> float:
                return 2.5

        visitor: PortfolioVisitor = RiskWeightVisitor()
        stock = StockAsset("XYZ", shares=1, current_price=10, cost_basis=10)
        bond = BondAsset("XYZ", par_value=100, coupon_rate=0.01)
        crypto = CryptoAsset("XYZ", amount=1, current_price=10, cost_basis=10)

        assert stock.accept(visitor) == pytest.approx(1.2)
        assert bond.accept(visitor) == pytest.approx(0.4)
        assert crypto.accept(visitor) == pytest.approx(2.5)


class TestSingleDispatchAlternative:
    def test_single_dispatch_evaluates_all_assets(self) -> None:
        evaluator = SingleDispatchPortfolioEvaluator()
        portfolio: list[PortfolioElement] = [
            StockAsset("AAPL", shares=10.0, current_price=150.0, cost_basis=100.0),
            BondAsset("Treasury", par_value=1000.0, coupon_rate=0.05),
            CryptoAsset("BTC", amount=0.1, current_price=50000.0, cost_basis=30000.0),
        ]
        results = [evaluator.evaluate(item) for item in portfolio]
        assert results[0] == pytest.approx(1500.0)
        assert results[1] == pytest.approx(1050.0)
        assert results[2] == pytest.approx(5000.0)

    def test_single_dispatch_unsupported_type_raises(self) -> None:
        evaluator = SingleDispatchPortfolioEvaluator()
        with pytest.raises(NotImplementedError, match="Unsupported asset type: int"):
            evaluator.evaluate(42)

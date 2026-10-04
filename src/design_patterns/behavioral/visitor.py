"""Visitor Design Pattern.

Classification: Behavioral
Intent:
    Represent an operation to be performed on the elements of an object structure.
    Visitor lets you define a new operation without changing the classes of the elements
    on which it operates.

Motivation & Real-World Analogy:
    In a financial investment portfolio, an investor holds diverse asset types:
    equities (stocks), fixed-income instruments (bonds), and digital currencies (crypto).
    Each asset has unique financial mechanics, calculation rules, and regulatory constraints.
    Frequently, financial applications need to execute complex operations across the portfolio:
    - Calculating capital gains and tax liabilities (equities taxed at long-term capital rate,
      bonds taxed as ordinary income, crypto under specialized digital asset rules).
    - Computing total market valuation and portfolio weights.
    - Generating audited risk disclosure statements.
    Polluting asset entities with tax calculations or reporting formats violates the Single
    Responsibility Principle and requires modifying core domain models whenever tax rules change.
    The Visitor pattern uses double dispatch to decouple algorithms from the asset data structures.
    In Python, this is supplemented by `functools.singledispatchmethod` for elegant,
    idiomatic multi-method dispatch.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class PortfolioVisitor {
            <<protocol>>
            +visit_stock(stock: StockAsset) float
            +visit_bond(bond: BondAsset) float
            +visit_crypto(crypto: CryptoAsset) float
        }
        class PortfolioElement {
            <<protocol>>
            +accept(visitor: PortfolioVisitor) float
        }
        class StockAsset {
            +symbol: str
            +shares: float
            +current_price: float
            +cost_basis: float
            +accept(visitor: PortfolioVisitor) float
        }
        class BondAsset {
            +issuer: str
            +par_value: float
            +coupon_rate: float
            +accept(visitor: PortfolioVisitor) float
        }
        class CryptoAsset {
            +token: str
            +amount: float
            +current_price: float
            +cost_basis: float
            +accept(visitor: PortfolioVisitor) float
        }
        class CapitalGainsTaxVisitor {
            +visit_stock(stock: StockAsset) float
            +visit_bond(bond: BondAsset) float
            +visit_crypto(crypto: CryptoAsset) float
        }
        class MarketValueVisitor {
            +visit_stock(stock: StockAsset) float
            +visit_bond(bond: BondAsset) float
            +visit_crypto(crypto: CryptoAsset) float
        }
        PortfolioElement <|.. StockAsset
        PortfolioElement <|.. BondAsset
        PortfolioElement <|.. CryptoAsset
        PortfolioVisitor <|.. CapitalGainsTaxVisitor
        PortfolioVisitor <|.. MarketValueVisitor
        PortfolioElement --> PortfolioVisitor : accepts
    ```
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import singledispatchmethod
from typing import Any, Protocol


# ==============================================================================
# 1. Visitor and Element Protocols
# ==============================================================================
class PortfolioVisitor(Protocol):
    """Visitor Protocol: Declares visit operations for each concrete asset type."""

    def visit_stock(self, element: StockAsset) -> float: ...

    def visit_bond(self, element: BondAsset) -> float: ...

    def visit_crypto(self, element: CryptoAsset) -> float: ...


class PortfolioElement(Protocol):
    """Element Protocol: Declares the double-dispatch accept method."""

    def accept(self, visitor: PortfolioVisitor) -> float: ...


# ==============================================================================
# 2. Concrete Elements (Asset Classes)
# ==============================================================================
@dataclass(frozen=True)
class StockAsset:
    """Stock holding with shares, market price, and purchase cost."""

    symbol: str
    shares: float
    current_price: float
    cost_basis: float

    def accept(self, visitor: PortfolioVisitor) -> float:
        return visitor.visit_stock(self)


@dataclass(frozen=True)
class BondAsset:
    """Fixed-income bond with face value and annual coupon yield."""

    issuer: str
    par_value: float
    coupon_rate: float  # e.g., 0.05 for 5%

    def accept(self, visitor: PortfolioVisitor) -> float:
        return visitor.visit_bond(self)


@dataclass(frozen=True)
class CryptoAsset:
    """Cryptocurrency asset with high volatility and distinct taxation."""

    token: str
    amount: float
    current_price: float
    cost_basis: float

    def accept(self, visitor: PortfolioVisitor) -> float:
        return visitor.visit_crypto(self)


# ==============================================================================
# 3. Concrete Visitors
# ==============================================================================
class MarketValueVisitor:
    """Visitor that computes the fair market value of each portfolio asset."""

    def visit_stock(self, element: StockAsset) -> float:
        return element.shares * element.current_price

    def visit_bond(self, element: BondAsset) -> float:
        # Valuation includes principal par value plus one year's accrued coupon
        return element.par_value * (1.0 + element.coupon_rate)

    def visit_crypto(self, element: CryptoAsset) -> float:
        return element.amount * element.current_price


class CapitalGainsTaxVisitor:
    """Visitor computing taxable obligations per regulatory asset categories."""

    def __init__(
        self, stock_rate: float = 0.15, bond_income_rate: float = 0.30, crypto_rate: float = 0.28
    ) -> None:
        self.stock_rate = stock_rate
        self.bond_income_rate = bond_income_rate
        self.crypto_rate = crypto_rate

    def visit_stock(self, element: StockAsset) -> float:
        gain = (element.current_price - element.cost_basis) * element.shares
        return max(0.0, gain * self.stock_rate)

    def visit_bond(self, element: BondAsset) -> float:
        # Coupon interest income is taxed as ordinary income
        annual_coupon_interest = element.par_value * element.coupon_rate
        return annual_coupon_interest * self.bond_income_rate

    def visit_crypto(self, element: CryptoAsset) -> float:
        gain = (element.current_price - element.cost_basis) * element.amount
        return max(0.0, gain * self.crypto_rate)


# ==============================================================================
# 4. Pythonic Twist: Single-Dispatch Alternative
# ==============================================================================
class SingleDispatchPortfolioEvaluator:
    """Pythonic alternative using functools.singledispatchmethod.

    Eliminates the need for explicit accept() methods on elements by routing
    polymorphically on the runtime type of the target asset.
    """

    @singledispatchmethod
    def evaluate(self, asset: Any) -> float:
        raise NotImplementedError(f"Unsupported asset type: {type(asset).__name__}")

    @evaluate.register
    def _(self, asset: StockAsset) -> float:
        return asset.shares * asset.current_price

    @evaluate.register
    def _(self, asset: BondAsset) -> float:
        return asset.par_value * (1.0 + asset.coupon_rate)

    @evaluate.register
    def _(self, asset: CryptoAsset) -> float:
        return asset.amount * asset.current_price


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    portfolio: list[PortfolioElement] = [
        StockAsset("AAPL", shares=50, current_price=180.0, cost_basis=140.0),
        BondAsset("US-Treasury-10Y", par_value=10000.0, coupon_rate=0.045),
        CryptoAsset("BTC", amount=0.5, current_price=64000.0, cost_basis=42000.0),
    ]

    val_visitor = MarketValueVisitor()
    tax_visitor = CapitalGainsTaxVisitor()

    total_market_value = sum(item.accept(val_visitor) for item in portfolio)
    total_tax_due = sum(item.accept(tax_visitor) for item in portfolio)

    print(f"Total Portfolio Value: ${total_market_value:,.2f}")
    print(f"Estimated Tax Liability: ${total_tax_due:,.2f}")

    # Using Pythonic Single-Dispatch
    sd_evaluator = SingleDispatchPortfolioEvaluator()
    sd_total = sum(sd_evaluator.evaluate(item) for item in portfolio)
    print(f"Single-Dispatch Valuation: ${sd_total:,.2f}")

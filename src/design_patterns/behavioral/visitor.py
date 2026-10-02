"""Visitor Design Pattern.

Classification: Behavioral
Intent:
    Represent an operation to be performed on the elements of an object structure.
    Visitor lets you define a new operation without changing the classes of the
    elements on which it operates.

Motivation & Real-World Analogy:
    In financial wealth management, a client portfolio contains heterogeneous assets:
    `StockHolding`, `RealEstateHolding`, and `CryptoHolding`.
    We need to perform diverse calculations across the portfolio:
    1. Calculating Capital Gains Tax according to jurisdiction
    2. Calculating Liquidity Risk Scores
    3. Generating an Export XML/JSON Report
    Polluting asset domain models with tax computation rules violates SRP and OCP.
    The Visitor pattern externalizes these algorithms into dedicated visitor classes.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class AssetVisitor {
            <<protocol>>
            +visit_stock(stock: StockHolding) float
            +visit_real_estate(property: RealEstateHolding) float
            +visit_crypto(crypto: CryptoHolding) float
        }
        class TaxCalculatorVisitor {
            +visit_stock() float
            +visit_real_estate() float
            +visit_crypto() float
        }
        class AssetElement {
            <<protocol>>
            +accept(visitor: AssetVisitor) float
        }
        class StockHolding {
            +ticker: str
            +shares: int
            +purchase_price: float
            +current_price: float
            +accept(visitor: AssetVisitor) float
        }
        class RealEstateHolding {
            +address: str
            +appraised_value: float
            +accept(visitor: AssetVisitor) float
        }
        class CryptoHolding {
            +token: str
            +quantity: float
            +cost_basis: float
            +current_price: float
            +accept(visitor: AssetVisitor) float
        }
        AssetElement <|.. StockHolding
        AssetElement <|.. RealEstateHolding
        AssetElement <|.. CryptoHolding
        AssetVisitor <|.. TaxCalculatorVisitor
    ```
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Protocol


# ==============================================================================
# 1. Visitor Protocol
# ==============================================================================
class AssetVisitor(Protocol):
    """Visitor Interface: Declares visiting methods for each concrete element type."""

    def visit_stock(self, element: StockHolding) -> float: ...
    def visit_real_estate(self, element: RealEstateHolding) -> float: ...
    def visit_crypto(self, element: CryptoHolding) -> float: ...


# ==============================================================================
# 2. Element Protocol & Concrete Elements
# ==============================================================================
class AssetElement(Protocol):
    """Element Interface: Must define accept method for double dispatch."""

    def accept(self, visitor: AssetVisitor) -> float: ...


@dataclass(frozen=True)
class StockHolding:
    ticker: str
    shares: int
    purchase_price: float
    current_price: float

    def accept(self, visitor: AssetVisitor) -> float:
        return visitor.visit_stock(self)


@dataclass(frozen=True)
class RealEstateHolding:
    address: str
    appraised_value: float
    is_commercial: bool

    def accept(self, visitor: AssetVisitor) -> float:
        return visitor.visit_real_estate(self)


@dataclass(frozen=True)
class CryptoHolding:
    token: str
    quantity: float
    cost_basis: float
    current_price: float

    def accept(self, visitor: AssetVisitor) -> float:
        return visitor.visit_crypto(self)


# ==============================================================================
# 3. Concrete Visitors
# ==============================================================================
class CapitalGainsTaxVisitor:
    """Calculates taxable gain liabilities across asset classes."""

    def visit_stock(self, element: StockHolding) -> float:
        profit = (element.current_price - element.purchase_price) * element.shares
        # 15% capital gains on stock profits (if profitable)
        return max(0.0, profit * 0.15)

    def visit_real_estate(self, element: RealEstateHolding) -> float:
        # Annual property tax rate: 1.5% residential, 2.5% commercial
        rate = 0.025 if element.is_commercial else 0.015
        return element.appraised_value * rate

    def visit_crypto(self, element: CryptoHolding) -> float:
        gain = (element.current_price - element.cost_basis) * element.quantity
        # 28% crypto short-term rate
        return max(0.0, gain * 0.28)


class LiquidityAssessmentVisitor:
    """Calculates estimated liquidation timeframe in business days."""

    def visit_stock(self, element: StockHolding) -> float:
        return 2.0  # T+2 settlement

    def visit_real_estate(self, element: RealEstateHolding) -> float:
        return 90.0  # ~3 months to sell real estate

    def visit_crypto(self, element: CryptoHolding) -> float:
        return 0.1  # Instant on-chain liquidity (~2 hours)


# ==============================================================================
# 4. Pythonic Alternative: functools.singledispatch
# ==============================================================================
@functools.singledispatch
def estimate_asset_insurance(asset: object) -> float:
    """Pythonic alternative: Single dispatch handles polymorphic routing without accept()."""
    raise NotImplementedError(f"No insurance estimator registered for {type(asset)}")


@estimate_asset_insurance.register
def _(asset: RealEstateHolding) -> float:
    return asset.appraised_value * 0.005  # 0.5% homeowners policy


@estimate_asset_insurance.register
def _(asset: StockHolding) -> float:
    return 0.0  # SIPC protected up to statutory limit, zero private insurance needed


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    portfolio: list[AssetElement] = [
        StockHolding(ticker="AAPL", shares=100, purchase_price=120.0, current_price=180.0),
        RealEstateHolding(
            address="742 Evergreen Terrace", appraised_value=500_000.0, is_commercial=False
        ),
        CryptoHolding(token="BTC", quantity=0.5, cost_basis=40_000.0, current_price=65_000.0),
    ]

    tax_calc = CapitalGainsTaxVisitor()
    liquidity_calc = LiquidityAssessmentVisitor()

    total_tax = sum(item.accept(tax_calc) for item in portfolio)
    avg_liquidity = sum(item.accept(liquidity_calc) for item in portfolio) / len(portfolio)

    print(f"Total Portfolio Tax Liability: ${total_tax:,.2f}")
    print(f"Average Liquidation Delay:    {avg_liquidity:.1f} days")

"""Specification Design Pattern.

Classification: Architectural / Domain-Driven Design (DDD)
Intent:
    Recombine business rules that can be chained together using boolean logic (AND, OR, NOT).

Motivation & Real-World Analogy:
    In e-commerce search engines, loan approval engines, or fraud screening pipelines,
    filtering entities based on dozens of dynamic rules is standard:
    - Item must be in stock
    - Item price between $50 and $200
    - Item ships to customer's country
    Hardcoding these conditions in huge SQL WHERE clauses or procedural loops results
    in code duplication and makes testing individual rules impossible.
    The Specification pattern models each business rule as an isolated, testable
    object that can be combined fluently using Python operator overloading (`&`, `|`, `~`).

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Specification~T~ {
            <<abstract>>
            +is_satisfied_by(candidate: T) bool*
            +and_(other: Specification) Specification
            +or_(other: Specification) Specification
            +not_() Specification
            +__and__() Specification
            +__or__() Specification
            +__invert__() Specification
        }
        class InStockSpec {
            +is_satisfied_by(candidate) bool
        }
        class PriceRangeSpec {
            -min_price: float
            -max_price: float
            +is_satisfied_by(candidate) bool
        }
        class CategorySpec {
            -category: str
            +is_satisfied_by(candidate) bool
        }
        Specification <|-- InStockSpec
        Specification <|-- PriceRangeSpec
        Specification <|-- CategorySpec
    ```
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


# ==============================================================================
# 1. Base Specification with Boolean Combinators & Operator Overloading
# ==============================================================================
class Specification(ABC, Generic[T]):
    """Abstract Base Specification supporting composable boolean algebra."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Evaluates whether the candidate entity fulfills this specification."""
        ...

    def and_(self, other: Specification[T]) -> Specification[T]:
        return AndSpecification(self, other)

    def or_(self, other: Specification[T]) -> Specification[T]:
        return OrSpecification(self, other)

    def not_(self) -> Specification[T]:
        return NotSpecification(self)

    # Pythonic dunder operator overloads: &, |, ~
    def __and__(self, other: Specification[T]) -> Specification[T]:
        return self.and_(other)

    def __or__(self, other: Specification[T]) -> Specification[T]:
        return self.or_(other)

    def __invert__(self) -> Specification[T]:
        return self.not_()


class AndSpecification(Specification[T]):
    def __init__(self, one: Specification[T], other: Specification[T]) -> None:
        self.one = one
        self.other = other

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.one.is_satisfied_by(candidate) and self.other.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    def __init__(self, one: Specification[T], other: Specification[T]) -> None:
        self.one = one
        self.other = other

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.one.is_satisfied_by(candidate) or self.other.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    def __init__(self, wrapped: Specification[T]) -> None:
        self.wrapped = wrapped

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.wrapped.is_satisfied_by(candidate)


# ==============================================================================
# 2. Domain Model & Concrete Specifications
# ==============================================================================
@dataclass(frozen=True)
class CatalogItem:
    title: str
    price: float
    category: str
    in_stock: bool


class InStockSpecification(Specification[CatalogItem]):
    def is_satisfied_by(self, candidate: CatalogItem) -> bool:
        return candidate.in_stock


class PriceRangeSpecification(Specification[CatalogItem]):
    def __init__(self, min_price: float, max_price: float) -> None:
        if min_price > max_price:
            raise ValueError(f"Min price {min_price} cannot exceed max price {max_price}")
        self.min_price = min_price
        self.max_price = max_price

    def is_satisfied_by(self, candidate: CatalogItem) -> bool:
        return self.min_price <= candidate.price <= self.max_price


class CategorySpecification(Specification[CatalogItem]):
    def __init__(self, category: str) -> None:
        self.category = category.lower()

    def is_satisfied_by(self, candidate: CatalogItem) -> bool:
        return candidate.category.lower() == self.category


# ==============================================================================
# 3. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    items = [
        CatalogItem("Gaming Laptop", 1299.99, "Electronics", in_stock=True),
        CatalogItem("Wireless Mouse", 49.99, "Electronics", in_stock=True),
        CatalogItem("Coffee Mug", 15.00, "Kitchen", in_stock=False),
        CatalogItem("Desk Lamp", 35.00, "Office", in_stock=True),
    ]

    # Express complex business queries with natural Python operators:
    # "In stock AND (Electronics under $100 OR Office items)"
    query = InStockSpecification() & (
        (CategorySpecification("Electronics") & PriceRangeSpecification(0, 100))
        | CategorySpecification("Office")
    )

    matching = [item for item in items if query.is_satisfied_by(item)]
    print(f"Matching Items ({len(matching)}): {[item.title for item in matching]}")

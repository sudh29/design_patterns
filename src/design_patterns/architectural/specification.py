"""Specification Design Pattern.

Classification: Architectural / Enterprise
Intent:
    Encapsulate a business rule or predicate condition into a reusable object.
    Specifications can be recombined using boolean logic (AND, OR, NOT) without
    duplicating domain filtering logic.

Motivation & Real-World Analogy:
    In e-commerce search, inventory, or billing systems, criteria for querying products
    (e.g., "products under $100", "in-stock items", "electronics on discount",
    "customer eligible for free shipping") are frequently scattered across SQL queries,
    controllers, and domain entities.
    Changing a rule (such as what defines "premium member") requires tracking down
    every occurrence of that boolean logic across the application.
    The Specification pattern isolates business criteria in cohesive objects.
    By implementing Python operator overloading (`&`, `|`, `~`), specifications compose
    fluently and declaratively:
    `spec = (InStockSpec() & PriceUnderSpec(100.0)) | ClearanceSpec()`.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Specification~T~ {
            <<abstract>>
            +is_satisfied_by(candidate: T)* bool
            +__and__(other: Specification~T~) Specification~T~
            +__or__(other: Specification~T~) Specification~T~
            +__invert__() Specification~T~
        }
        class AndSpecification~T~ {
            -left: Specification~T~
            -right: Specification~T~
            +is_satisfied_by(candidate: T) bool
        }
        class OrSpecification~T~ {
            -left: Specification~T~
            -right: Specification~T~
            +is_satisfied_by(candidate: T) bool
        }
        class NotSpecification~T~ {
            -spec: Specification~T~
            +is_satisfied_by(candidate: T) bool
        }
        class Product {
            +name: str
            +category: str
            +price: float
            +rating: float
            +in_stock: bool
        }
        Specification <|-- AndSpecification
        Specification <|-- OrSpecification
        Specification <|-- NotSpecification
    ```
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


# ==============================================================================
# 1. Base Specification with Composable Operators
# ==============================================================================
class Specification(ABC, Generic[T]):
    """Abstract composable specification with boolean operator overloading."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Predicate checking whether the candidate satisfies the specification."""
        ...

    def __and__(self, other: Specification[T]) -> Specification[T]:
        return AndSpecification(self, other)

    def __or__(self, other: Specification[T]) -> Specification[T]:
        return OrSpecification(self, other)

    def __invert__(self) -> Specification[T]:
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """Composite specification representing logical conjunction (AND)."""

    def __init__(self, left: Specification[T], right: Specification[T]) -> None:
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    """Composite specification representing logical disjunction (OR)."""

    def __init__(self, left: Specification[T], right: Specification[T]) -> None:
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    """Composite specification representing logical negation (NOT)."""

    def __init__(self, spec: Specification[T]) -> None:
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)


# ==============================================================================
# 2. Domain Model: E-Commerce Product
# ==============================================================================
@dataclass(frozen=True)
class Product:
    """Catalog product candidate for filtering rules."""

    id: str
    name: str
    category: str
    price: float
    rating: float
    in_stock: bool


# ==============================================================================
# 3. Concrete Domain Specifications
# ==============================================================================
class CategorySpecification(Specification[Product]):
    """Matches products belonging to a specific category."""

    def __init__(self, category: str) -> None:
        self.category = category.lower().strip()

    def is_satisfied_by(self, candidate: Product) -> bool:
        return candidate.category.lower().strip() == self.category


class PriceBetweenSpecification(Specification[Product]):
    """Matches products within an inclusive price bracket."""

    def __init__(self, min_price: float = 0.0, max_price: float = float("inf")) -> None:
        if min_price > max_price:
            raise ValueError(f"min_price ({min_price}) cannot exceed max_price ({max_price})")
        self.min_price = min_price
        self.max_price = max_price

    def is_satisfied_by(self, candidate: Product) -> bool:
        return self.min_price <= candidate.price <= self.max_price


class InStockSpecification(Specification[Product]):
    """Matches items currently in stock."""

    def is_satisfied_by(self, candidate: Product) -> bool:
        return candidate.in_stock


class MinimumRatingSpecification(Specification[Product]):
    """Matches products that meet or exceed a minimum customer review rating."""

    def __init__(self, min_rating: float) -> None:
        if not (0.0 <= min_rating <= 5.0):
            raise ValueError("Rating must be between 0.0 and 5.0")
        self.min_rating = min_rating

    def is_satisfied_by(self, candidate: Product) -> bool:
        return candidate.rating >= self.min_rating


# ==============================================================================
# 4. Specification Filter Utility
# ==============================================================================
def filter_by_specification(items: list[Product], spec: Specification[Product]) -> list[Product]:
    """Helper to evaluate and filter a collection using a composite specification."""
    return [item for item in items if spec.is_satisfied_by(item)]


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    catalog = [
        Product("1", "Mechanical Keyboard", "electronics", 120.0, 4.8, True),
        Product("2", "Wireless Mouse", "electronics", 45.0, 4.6, True),
        Product("3", "Vintage Desk Lamp", "home", 35.0, 4.2, False),
        Product("4", "Ergonomic Chair", "office", 350.0, 4.9, True),
        Product("5", "Budget USB Cable", "electronics", 9.99, 3.8, True),
    ]

    # Composed specification: In Stock & Electronics & Price <= 100 & Rating >= 4.0
    budget_tech_deal = (
        InStockSpecification()
        & CategorySpecification("electronics")
        & PriceBetweenSpecification(max_price=100.0)
        & MinimumRatingSpecification(min_rating=4.0)
    )

    matching_products = filter_by_specification(catalog, budget_tech_deal)
    print("Matching Products for Budget Tech Deal:")
    for p in matching_products:
        print(f" - {p.name}: ${p.price:.2f} (Rating: {p.rating})")

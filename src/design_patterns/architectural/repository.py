"""Repository Design Pattern.

Classification: Architectural / Domain-Driven Design (DDD)
Intent:
    Mediates between the domain and data mapping layers using a collection-like
    interface for accessing domain objects.

Motivation & Real-World Analogy:
    In Clean Architecture and Domain-Driven Design (DDD), domain entities
    (such as `Product` or `Customer`) should remain completely agnostic to the
    underlying persistence mechanism (PostgreSQL, MongoDB, Redis, or In-Memory).
    If domain services write raw SQL queries or ORM calls directly, swapping the
    database or writing unit tests becomes prohibitively difficult.
    The Repository pattern provides a typed, collection-like interface:
    `add(entity)`, `get(id)`, `list()`, `delete(id)`.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Repository~T, ID~ {
            <<protocol>>
            +add(entity: T)
            +get_by_id(id: ID) T | None
            +list_all() list[T]
            +delete(id: ID) bool
        }
        class Product {
            +id: str
            +name: str
            +price: float
            +inventory_count: int
        }
        class InMemoryProductRepository {
            -_storage: dict[str, Product]
            +add(entity: Product)
            +get_by_id(id: str) Product | None
            +list_all() list[Product]
            +delete(id: str) bool
        }
        Repository <|.. InMemoryProductRepository
        InMemoryProductRepository o--> Product : stores
    ```
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")
ID = TypeVar("ID", contravariant=True)


# ==============================================================================
# 1. Domain Entity
# ==============================================================================
@dataclass
class Product:
    """Domain Entity representing an item in an e-commerce catalog."""

    sku: str
    name: str
    price: float
    stock: int

    def decrease_stock(self, count: int) -> None:
        if count <= 0:
            raise ValueError("Count must be positive")
        if count > self.stock:
            raise ValueError(f"Insufficient stock for {self.name}")
        self.stock -= count


# ==============================================================================
# 2. Generic Repository Protocol
# ==============================================================================
class Repository(Protocol, Generic[T, ID]):
    """Generic Repository interface providing collection-like abstractions."""

    def add(self, entity: T) -> None: ...
    def get_by_id(self, entity_id: ID) -> T | None: ...
    def list_all(self) -> list[T]: ...
    def delete(self, entity_id: ID) -> bool: ...


# ==============================================================================
# 3. Concrete In-Memory Implementation
# ==============================================================================
class InMemoryProductRepository(Repository[Product, str]):
    """Thread-safe in-memory collection simulating a persistent datastore."""

    def __init__(self) -> None:
        self._records: dict[str, Product] = {}

    def add(self, entity: Product) -> None:
        if entity.sku in self._records:
            raise KeyError(f"Product with SKU '{entity.sku}' already exists")
        self._records[entity.sku] = entity

    def get_by_id(self, entity_id: str) -> Product | None:
        return self._records.get(entity_id)

    def list_all(self) -> list[Product]:
        return list(self._records.values())

    def delete(self, entity_id: str) -> bool:
        if entity_id in self._records:
            del self._records[entity_id]
            return True
        return False


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    repo = InMemoryProductRepository()

    p1 = Product(sku="SKU-100", name="Ergonomic Mouse", price=69.99, stock=15)
    p2 = Product(sku="SKU-200", name="Mechanical Keyboard", price=129.99, stock=8)

    repo.add(p1)
    repo.add(p2)

    found = repo.get_by_id("SKU-100")
    print(f"Retrieved: {found}")
    print(f"Total Catalog Products: {len(repo.list_all())}")

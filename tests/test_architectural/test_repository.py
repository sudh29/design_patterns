"""Tests for the Repository pattern implementation."""

import pytest

from design_patterns.architectural.repository import (
    InMemoryProductRepository,
    Product,
)


class TestRepositoryPattern:
    def test_product_stock_operations(self) -> None:
        p = Product("SKU-1", "Desk", 199.99, 5)
        p.decrease_stock(2)
        assert p.stock == 3

        with pytest.raises(ValueError, match="Count must be positive"):
            p.decrease_stock(-1)

        with pytest.raises(ValueError, match="Insufficient stock"):
            p.decrease_stock(10)

    def test_add_and_get_by_id(self) -> None:
        repo = InMemoryProductRepository()
        p = Product("P-1", "Monitor", 300.0, 10)
        repo.add(p)

        retrieved = repo.get_by_id("P-1")
        assert retrieved is not None
        assert retrieved.name == "Monitor"

    def test_duplicate_add_raises(self) -> None:
        repo = InMemoryProductRepository()
        p = Product("P-1", "Monitor", 300.0, 10)
        repo.add(p)
        with pytest.raises(KeyError, match="already exists"):
            repo.add(p)

    def test_list_all_and_delete(self) -> None:
        repo = InMemoryProductRepository()
        repo.add(Product("P-1", "M1", 10.0, 1))
        repo.add(Product("P-2", "M2", 20.0, 2))

        assert len(repo.list_all()) == 2
        assert repo.delete("P-1") is True
        assert repo.get_by_id("P-1") is None
        assert repo.delete("P-NONEXISTENT") is False

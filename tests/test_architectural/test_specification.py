"""Tests for the Specification pattern implementation."""

import pytest

from design_patterns.architectural.specification import (
    CatalogItem,
    CategorySpecification,
    InStockSpecification,
    PriceRangeSpecification,
)


class TestSpecificationPattern:
    def setup_method(self) -> None:
        self.item_a = CatalogItem("Laptop", 1000.0, "Tech", in_stock=True)
        self.item_b = CatalogItem("Mouse", 25.0, "Tech", in_stock=False)
        self.item_c = CatalogItem("Pen", 5.0, "Stationery", in_stock=True)

    def test_single_specifications(self) -> None:
        in_stock = InStockSpecification()
        assert in_stock.is_satisfied_by(self.item_a) is True
        assert in_stock.is_satisfied_by(self.item_b) is False

        price_spec = PriceRangeSpecification(10.0, 50.0)
        assert price_spec.is_satisfied_by(self.item_b) is True
        assert price_spec.is_satisfied_by(self.item_a) is False

    def test_invalid_price_range(self) -> None:
        with pytest.raises(ValueError, match="cannot exceed max price"):
            PriceRangeSpecification(100.0, 50.0)

    def test_and_composition(self) -> None:
        spec = InStockSpecification() & CategorySpecification("Tech")
        assert spec.is_satisfied_by(self.item_a) is True
        assert spec.is_satisfied_by(self.item_b) is False  # out of stock

    def test_or_composition(self) -> None:
        spec = CategorySpecification("Stationery") | PriceRangeSpecification(0, 30)
        assert spec.is_satisfied_by(self.item_b) is True  # price <= 30
        assert spec.is_satisfied_by(self.item_c) is True  # Stationery
        assert spec.is_satisfied_by(self.item_a) is False

    def test_not_composition(self) -> None:
        out_of_stock = ~InStockSpecification()
        assert out_of_stock.is_satisfied_by(self.item_b) is True
        assert out_of_stock.is_satisfied_by(self.item_a) is False

    def test_complex_composite_expression(self) -> None:
        # In stock AND (Price < $50 OR NOT Stationery)
        expr = InStockSpecification() & (
            PriceRangeSpecification(0, 50) | (~CategorySpecification("Stationery"))
        )
        assert expr.is_satisfied_by(self.item_a) is True  # In stock & not stationery
        assert expr.is_satisfied_by(self.item_c) is True  # In stock & price <= 50
        assert expr.is_satisfied_by(self.item_b) is False  # Out of stock

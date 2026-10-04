"""Tests for Specification pattern implementation."""

import pytest

from design_patterns.architectural.specification import (
    CategorySpecification,
    InStockSpecification,
    MinimumRatingSpecification,
    PriceBetweenSpecification,
    Product,
    filter_by_specification,
)


@pytest.fixture
def sample_products() -> list[Product]:
    return [
        Product("1", "Pro Laptop", "electronics", 1200.0, 4.9, True),
        Product("2", "Cheap Mouse", "electronics", 20.0, 3.5, True),
        Product("3", "Out-of-Stock Tablet", "electronics", 300.0, 4.2, False),
        Product("4", "Coffee Mug", "kitchen", 15.0, 4.8, True),
        Product("5", "Blender", "kitchen", 80.0, 4.1, False),
    ]


class TestAtomicSpecifications:
    def test_category_specification(self, sample_products: list[Product]) -> None:
        spec = CategorySpecification("Electronics")
        matched = filter_by_specification(sample_products, spec)
        assert len(matched) == 3
        assert {p.id for p in matched} == {"1", "2", "3"}

    def test_price_between_specification(self, sample_products: list[Product]) -> None:
        spec = PriceBetweenSpecification(min_price=10.0, max_price=100.0)
        matched = filter_by_specification(sample_products, spec)
        assert len(matched) == 3
        assert {p.id for p in matched} == {"2", "4", "5"}

    def test_price_between_invalid_bounds(self) -> None:
        with pytest.raises(ValueError, match="cannot exceed max_price"):
            PriceBetweenSpecification(min_price=200.0, max_price=100.0)

    def test_in_stock_specification(self, sample_products: list[Product]) -> None:
        spec = InStockSpecification()
        matched = filter_by_specification(sample_products, spec)
        assert len(matched) == 3
        assert {p.id for p in matched} == {"1", "2", "4"}

    def test_minimum_rating_specification(self, sample_products: list[Product]) -> None:
        spec = MinimumRatingSpecification(4.5)
        matched = filter_by_specification(sample_products, spec)
        assert len(matched) == 2
        assert {p.id for p in matched} == {"1", "4"}

    def test_minimum_rating_invalid_range(self) -> None:
        with pytest.raises(ValueError, match="Rating must be between"):
            MinimumRatingSpecification(-0.5)
        with pytest.raises(ValueError, match="Rating must be between"):
            MinimumRatingSpecification(5.5)


class TestCompositeOperators:
    def test_and_operator(self, sample_products: list[Product]) -> None:
        # Electronics AND in stock
        spec = CategorySpecification("electronics") & InStockSpecification()
        matched = filter_by_specification(sample_products, spec)
        assert len(matched) == 2
        assert {p.id for p in matched} == {"1", "2"}

    def test_or_operator(self, sample_products: list[Product]) -> None:
        # Category kitchen OR price > 1000
        spec = CategorySpecification("kitchen") | PriceBetweenSpecification(min_price=1000.0)
        matched = filter_by_specification(sample_products, spec)
        assert len(matched) == 3
        assert {p.id for p in matched} == {"1", "4", "5"}

    def test_invert_operator(self, sample_products: list[Product]) -> None:
        # NOT in stock
        spec = ~InStockSpecification()
        matched = filter_by_specification(sample_products, spec)
        assert len(matched) == 2
        assert {p.id for p in matched} == {"3", "5"}

    def test_complex_composite_expression(self, sample_products: list[Product]) -> None:
        # (In stock AND Rating >= 4.0) AND NOT kitchen
        spec = (InStockSpecification() & MinimumRatingSpecification(4.0)) & ~(
            CategorySpecification("kitchen")
        )
        matched = filter_by_specification(sample_products, spec)
        assert len(matched) == 1
        assert matched[0].id == "1"

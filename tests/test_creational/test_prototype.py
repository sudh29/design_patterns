"""Tests for the Prototype pattern implementation."""

import copy

import pytest

from design_patterns.creational.prototype import (
    CustomCacheConfig,
    DocumentSection,
    InvoiceTemplate,
    NaiveDocument,
    PrototypeRegistry,
)


class TestNaiveDocument:
    def test_naive_shallow_copy_corruption(self) -> None:
        original = NaiveDocument("Invoice", ["Item 1"], {"status": "draft"})
        clone = original.shallow_clone()

        clone.sections.append("Item 2")
        clone.metadata["status"] = "paid"

        # Demonstrates the shallow-copy anti-pattern flaw:
        assert original.sections == ["Item 1", "Item 2"]
        assert original.metadata["status"] == "paid"


class TestGoFPrototype:
    def test_invoice_clone_isolation(self) -> None:
        original = InvoiceTemplate(
            template_name="US Sales",
            currency="USD",
            sections=[DocumentSection("Billing", "Standard terms")],
            tax_rules={"CA": 0.075},
        )
        clone = original.clone()

        # Modify clone
        clone.add_section("Shipping", "Overnight delivery")
        clone.set_tax_rate("NY", 0.088)

        # Original remains untouched
        assert len(original.sections) == 1
        assert "NY" not in original.tax_rules
        assert len(clone.sections) == 2
        assert "NY" in clone.tax_rules

    def test_invalid_tax_rate(self) -> None:
        template = InvoiceTemplate("Test", "USD")
        with pytest.raises(ValueError, match="Tax rate cannot be negative"):
            template.set_tax_rate("INVALID", -0.05)


class TestPrototypeRegistry:
    def test_register_and_clone(self) -> None:
        registry = PrototypeRegistry()
        template = InvoiceTemplate("Base", "EUR")
        registry.register("base", template)

        clone = registry.get_clone("base")
        assert isinstance(clone, InvoiceTemplate)
        assert clone.currency == "EUR"
        assert clone is not template

    def test_duplicate_registration_raises(self) -> None:
        registry = PrototypeRegistry()
        template = InvoiceTemplate("Base", "EUR")
        registry.register("base", template)
        with pytest.raises(KeyError, match="already registered"):
            registry.register("base", template)

    def test_unregister(self) -> None:
        registry = PrototypeRegistry()
        template = InvoiceTemplate("Base", "EUR")
        registry.register("base", template)
        registry.unregister("base")
        with pytest.raises(KeyError, match="not registered"):
            registry.get_clone("base")

    def test_unregister_nonexistent_raises(self) -> None:
        registry = PrototypeRegistry()
        with pytest.raises(KeyError, match="not found"):
            registry.unregister("nonexistent")


class TestCustomDeepcopyHook:
    def test_custom_deepcopy(self) -> None:
        config = CustomCacheConfig("Redis", 3600, ["db", "cache"])
        cloned = copy.deepcopy(config)
        cloned.tags.append("session")

        assert config.tags == ["db", "cache"]
        assert cloned.tags == ["db", "cache", "session"]

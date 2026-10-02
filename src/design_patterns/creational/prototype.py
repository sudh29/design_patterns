"""Prototype Design Pattern.

Classification: Creational
Intent:
    Specify the kinds of objects to create using a prototypical instance,
    and create new objects by copying this prototype.

Motivation & Real-World Analogy:
    In document management, game engines, or cloud configuration management,
    instantiating a complex entity from scratch (involving DB queries, heavy calculations,
    or numerous nested sub-components) is expensive. Instead of configuring from
    scratch, a pre-configured prototype is cloned and tailored. Naive cloning (shallow copy)
    leads to catastrophic state-sharing bugs when nested mutable objects (e.g., line items,
    tags, or metadata) are modified.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Prototype {
            <<protocol>>
            +clone() Self
        }
        class DocumentTemplate {
            +title: str
            +sections: list[str]
            +metadata: dict[str, str]
            +clone() DocumentTemplate
        }
        class PrototypeRegistry {
            -prototypes: dict[str, Prototype]
            +register(name: str, proto: Prototype)
            +clone(name: str) Prototype
        }
        Prototype <|.. DocumentTemplate
        PrototypeRegistry o--> Prototype
    ```
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Protocol, Self


# ==============================================================================
# 1. Anti-Pattern / Naive Approach (Shallow Copy Pitfall)
# ==============================================================================
class NaiveDocument:
    """Anti-pattern: Naive copy constructor that performs shallow copying.

    Modifying nested structures in the clone silently corrupts the original instance!
    """

    def __init__(
        self, title: str, sections: list[str], metadata: dict[str, Any] | None = None
    ) -> None:
        self.title = title
        self.sections = sections
        self.metadata = metadata if metadata is not None else {}

    def shallow_clone(self) -> NaiveDocument:
        # BUG: sections list and metadata dict references are shared!
        return NaiveDocument(self.title, self.sections, self.metadata)


# ==============================================================================
# 2. Clean Pattern Implementation (GoF Prototype with Deep Copy)
# ==============================================================================
class Prototype(Protocol):
    """Prototype Protocol: Guarantees a clean, isolated cloning contract."""

    def clone(self) -> Self: ...


@dataclass
class DocumentSection:
    heading: str
    body: str


@dataclass
class InvoiceTemplate:
    """Concrete Prototype: Represents a structured enterprise invoice."""

    template_name: str
    currency: str
    sections: list[DocumentSection] = field(default_factory=list)
    tax_rules: dict[str, float] = field(default_factory=dict)

    def clone(self) -> InvoiceTemplate:
        """Creates a truly isolated deep copy of this prototype."""
        return copy.deepcopy(self)

    def add_section(self, heading: str, body: str) -> None:
        self.sections.append(DocumentSection(heading=heading, body=body))

    def set_tax_rate(self, jurisdiction: str, rate: float) -> None:
        if rate < 0:
            raise ValueError("Tax rate cannot be negative")
        self.tax_rules[jurisdiction] = rate


class PrototypeRegistry:
    """Registry / Prototype Manager: Stores and dispenses cloned templates by key."""

    def __init__(self) -> None:
        self._prototypes: dict[str, Prototype] = {}

    def register(self, name: str, prototype: Prototype) -> None:
        if name in self._prototypes:
            raise KeyError(f"Prototype '{name}' already registered")
        self._prototypes[name] = prototype

    def unregister(self, name: str) -> None:
        if name not in self._prototypes:
            raise KeyError(f"Prototype '{name}' not found")
        del self._prototypes[name]

    def get_clone(self, name: str) -> Any:
        if name not in self._prototypes:
            raise KeyError(f"Prototype '{name}' is not registered")
        return self._prototypes[name].clone()


# ==============================================================================
# 3. Pythonic Twist: __copy__ and __deepcopy__ Protocol Integration
# ==============================================================================
class CustomCacheConfig:
    """Demonstrates custom __deepcopy__ hook to bypass cloning non-serializable resources."""

    def __init__(self, name: str, ttl: int, tags: list[str]) -> None:
        self.name = name
        self.ttl = ttl
        self.tags = tags

    def __deepcopy__(self, memo: dict[int, Any]) -> CustomCacheConfig:
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        result.name = self.name
        result.ttl = self.ttl
        result.tags = copy.deepcopy(self.tags, memo)
        return result


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    registry = PrototypeRegistry()

    # Create base standard EU Invoice template
    eu_invoice = InvoiceTemplate(
        template_name="Standard EU B2B",
        currency="EUR",
        sections=[DocumentSection("Terms", "Net 30 payment")],
        tax_rules={"VAT": 0.20},
    )
    registry.register("eu_standard", eu_invoice)

    # Client clones the prototype for Germany specifically
    de_invoice: InvoiceTemplate = registry.get_clone("eu_standard")
    de_invoice.set_tax_rate("MwSt", 0.19)
    de_invoice.add_section("Notice", "Lieferung steuerfrei gem. § 4 Nr. 1b UStG")

    print(f"Original EU rules: {eu_invoice.tax_rules}")
    print(f"DE Clone rules:   {de_invoice.tax_rules}")
    assert "MwSt" not in eu_invoice.tax_rules, "Original corrupted by clone!"
    print("Isolation confirmed: Prototype deep clone succeeded.")

"""Interactive and Non-Interactive CLI Runner for Design Patterns.

Allows users to explore, inspect, and execute demonstrations of all 28 design patterns.
"""

from __future__ import annotations

import argparse
import runpy
import sys
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class PatternMeta:
    """Metadata describing an implemented design pattern."""

    category: str
    name: str
    module: str
    description: str


PATTERNS: list[PatternMeta] = [
    # --- Creational Patterns (5) ---
    PatternMeta(
        category="Creational",
        name="Factory Method",
        module="design_patterns.creational.factory_method",
        description="Encapsulates object instantiation, allowing subclasses to decide which class to instantiate.",
    ),
    PatternMeta(
        category="Creational",
        name="Abstract Factory",
        module="design_patterns.creational.abstract_factory",
        description="Creates families of related or dependent objects without specifying concrete classes.",
    ),
    PatternMeta(
        category="Creational",
        name="Builder",
        module="design_patterns.creational.builder",
        description="Separates complex object construction from representation for step-by-step assembly.",
    ),
    PatternMeta(
        category="Creational",
        name="Prototype",
        module="design_patterns.creational.prototype",
        description="Specifies object types to create using a prototypical instance cloned via deepcopy.",
    ),
    PatternMeta(
        category="Creational",
        name="Singleton",
        module="design_patterns.creational.singleton",
        description="Ensures a class has only one instance and provides a global point of access to it.",
    ),
    # --- Structural Patterns (7) ---
    PatternMeta(
        category="Structural",
        name="Adapter",
        module="design_patterns.structural.adapter",
        description="Converts the interface of a class into another interface clients expect.",
    ),
    PatternMeta(
        category="Structural",
        name="Bridge",
        module="design_patterns.structural.bridge",
        description="Decouples an abstraction from its implementation so both can vary independently.",
    ),
    PatternMeta(
        category="Structural",
        name="Composite",
        module="design_patterns.structural.composite",
        description="Composes objects into tree structures to represent part-whole hierarchies uniformly.",
    ),
    PatternMeta(
        category="Structural",
        name="Decorator",
        module="design_patterns.structural.decorator",
        description="Attaches additional responsibilities dynamically without subclassing.",
    ),
    PatternMeta(
        category="Structural",
        name="Facade",
        module="design_patterns.structural.facade",
        description="Provides a unified higher-level interface to a complex subsystem.",
    ),
    PatternMeta(
        category="Structural",
        name="Flyweight",
        module="design_patterns.structural.flyweight",
        description="Shares common state across multiple objects to minimize memory footprint.",
    ),
    PatternMeta(
        category="Structural",
        name="Proxy",
        module="design_patterns.structural.proxy",
        description="Provides a surrogate or placeholder to control access to another object.",
    ),
    # --- Behavioral Patterns (10) ---
    PatternMeta(
        category="Behavioral",
        name="Chain of Responsibility",
        module="design_patterns.behavioral.chain_of_responsibility",
        description="Passes requests along a dynamic chain of processing middleware handlers.",
    ),
    PatternMeta(
        category="Behavioral",
        name="Command",
        module="design_patterns.behavioral.command",
        description="Encapsulates requests as objects, supporting undo/redo operations and queueing.",
    ),
    PatternMeta(
        category="Behavioral",
        name="Iterator",
        module="design_patterns.behavioral.iterator",
        description="Accesses elements of an aggregate object sequentially without exposing internal representation.",
    ),
    PatternMeta(
        category="Behavioral",
        name="Mediator",
        module="design_patterns.behavioral.mediator",
        description="Reduces chaotic dependencies between objects through a central communication hub.",
    ),
    PatternMeta(
        category="Behavioral",
        name="Memento",
        module="design_patterns.behavioral.memento",
        description="Captures and externalizes object internal state for restoration without violating encapsulation.",
    ),
    PatternMeta(
        category="Behavioral",
        name="Observer",
        module="design_patterns.behavioral.observer",
        description="Defines a one-to-many subscription notification mechanism between objects.",
    ),
    PatternMeta(
        category="Behavioral",
        name="State",
        module="design_patterns.behavioral.state",
        description="Allows an object to alter its behavior when its internal state changes.",
    ),
    PatternMeta(
        category="Behavioral",
        name="Strategy",
        module="design_patterns.behavioral.strategy",
        description="Defines a family of interchangeable algorithms selected at runtime.",
    ),
    PatternMeta(
        category="Behavioral",
        name="Template Method",
        module="design_patterns.behavioral.template_method",
        description="Defines algorithm skeleton in a base class, deferring specific steps to subclasses.",
    ),
    PatternMeta(
        category="Behavioral",
        name="Visitor",
        module="design_patterns.behavioral.visitor",
        description="Separates algorithms from object structures using double-dispatch or singledispatch.",
    ),
    # --- Architectural & Enterprise Patterns (6) ---
    PatternMeta(
        category="Architectural",
        name="Dependency Injection",
        module="design_patterns.architectural.dependency_injection",
        description="Inversion of Control (IoC) service container with singleton and transient scopes.",
    ),
    PatternMeta(
        category="Architectural",
        name="Repository",
        module="design_patterns.architectural.repository",
        description="Collection-like abstraction mediating domain entities and data persistence layers.",
    ),
    PatternMeta(
        category="Architectural",
        name="Unit of Work",
        module="design_patterns.architectural.unit_of_work",
        description="Coordinates atomic transactions across repositories with rollback semantics.",
    ),
    PatternMeta(
        category="Architectural",
        name="Specification",
        module="design_patterns.architectural.specification",
        description="Composable business predicate logic using boolean operators (&, |, ~).",
    ),
    PatternMeta(
        category="Architectural",
        name="Event Pub/Sub",
        module="design_patterns.architectural.event_pubsub",
        description="Loosely coupled event bus for asynchronous and decoupled domain events.",
    ),
    PatternMeta(
        category="Architectural",
        name="Registry",
        module="design_patterns.architectural.registry",
        description="Dynamic plugin discovery and registration catalog for extensible systems.",
    ),
]


def list_patterns(category_filter: str | None = None) -> list[PatternMeta]:
    """Return matching patterns filtered by category, or all patterns if none specified."""
    if not category_filter:
        return list(PATTERNS)
    norm = category_filter.lower().strip()
    return [p for p in PATTERNS if p.category.lower() == norm]


def find_pattern(query: str) -> PatternMeta | None:
    """Find a pattern by exact/partial name or module suffix."""
    norm = query.lower().strip().replace("-", "_")
    for p in PATTERNS:
        short_mod = p.module.split(".")[-1]
        full_mod = p.module.replace("design_patterns.", "")
        if norm in (p.name.lower(), short_mod, full_mod, p.module.lower()):
            return p
    return None


def run_pattern(meta: PatternMeta) -> None:
    """Execute the demonstration block of the specified pattern module."""
    print(f"\n{'=' * 70}")
    print(f"▶ Running {meta.category}: {meta.name}")
    print(f"  Module: {meta.module}")
    print(f"  Intent: {meta.description}")
    print(f"{'=' * 70}\n")
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", category=RuntimeWarning, message=".*found in sys.modules.*"
        )
        runpy.run_module(meta.module, run_name="__main__")
    print(f"\n[Completed demonstration: {meta.name}]\n")


def build_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="design-patterns",
        description="Modern Python Design Patterns - Interactive & Headless CLI Runner",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all 28 implemented design patterns",
    )
    parser.add_argument(
        "--category",
        choices=["creational", "structural", "behavioral", "architectural"],
        help="Filter patterns by category",
    )
    parser.add_argument(
        "--run",
        metavar="PATTERN",
        help="Run demonstration for a specific pattern (e.g. 'factory_method' or 'creational.builder')",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point handling both programmatic arguments and interactive invocation."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        patterns = list_patterns(args.category)
        print(f"\nFound {len(patterns)} pattern(s):\n")
        current_cat = ""
        for i, p in enumerate(patterns, 1):
            if p.category != current_cat:
                current_cat = p.category
                print(f"\n--- {current_cat} Patterns ---")
            print(f" {i:2d}. {p.name:<25} ({p.module})")
            print(f"     {p.description}")
        print()
        return 0

    if args.run:
        meta = find_pattern(args.run)
        if not meta:
            print(f"Error: Pattern '{args.run}' not recognized.", file=sys.stderr)
            print("Run with --list to see available patterns.", file=sys.stderr)
            return 1
        run_pattern(meta)
        return 0

    # Default if no arguments: print summary and usage
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

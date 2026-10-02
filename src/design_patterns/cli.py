"""Interactive Command-Line Interface (CLI) for Design Patterns in Python.

Allows users to explore, inspect, and execute demonstrations of any design pattern.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from typing import Any

PATTERN_REGISTRY: dict[str, dict[str, str]] = {
    "creational": {
        "factory_method": "Multi-channel Notification Dispatcher (Email, SMS, Slack)",
        "abstract_factory": "Cross-Platform Cloud Infrastructure Provisioner (AWS, GCP)",
        "builder": "Fluent HTTP Request Builder with Invariant Validation",
        "prototype": "Document & Invoice Template Deep-Cloning with Registry",
        "singleton": "Thread-safe Metaclass Connection Pool and Borg Monostate",
    },
    "structural": {
        "adapter": "Legacy XML/SOAP to Modern JSON/REST Payment Gateway Adapter",
        "bridge": "Notification Messaging Abstraction & Delivery Channels (SMS, Webhook)",
        "composite": "Hierarchical File System & Recursive Directory Sizing",
        "decorator": "API Service Middleware for In-Memory Caching & Audit Logging",
        "facade": "Unified Video Transcoding Pipeline Subsystem Facade",
        "flyweight": "Forest Ecosystem Simulation with Shared Intrinsic Mesh Geometry",
        "proxy": "Virtual Lazy Document Loader and Role-Based Protection Proxy",
    },
    "behavioral": {
        "chain_of_responsibility": "HTTP Middleware Request Pipeline (Auth, RateLimit, Schema)",
        "command": "Document Text Editor with Full Undo/Redo Stacks",
        "iterator": "Binary Search Tree In-Order Traversal with Custom Iterators & Generators",
        "mediator": "Air Traffic Control (ATC) Runway Clearance Coordinator",
        "memento": "Financial Ledger Transaction Snapshot & Safe Rollback",
        "observer": "Real-time Stock Price Ticker with Automated Subscriber Bots",
        "state": "E-commerce Order Finite State Machine Lifecycle",
        "strategy": "Dynamic E-commerce Checkout Pricing & Discount Algorithms",
        "template_method": "Data Engineering ETL Pipeline (Extract, Clean, Transform, Load)",
        "visitor": "Financial Wealth Asset Tax & Liquidity Evaluation Engine",
    },
    "architectural": {
        "dependency_injection": "Lightweight IoC Container with Singleton & Transient Lifecycles",
        "repository": "Domain Persistence Decoupling with Generic Product Repository",
        "unit_of_work": "Atomic Multi-Repository Transaction Coordinator with Rollback",
        "specification": "Composable Business Rules with Boolean Operator Overloading (&, |, ~)",
        "event_pubsub": "Domain Event Bus with Isolated Handler Error Handling",
        "registry": "Extensible Dynamic Plugin System with Decorator Registration",
    },
}


def list_patterns() -> None:
    """Prints all cataloged design patterns grouped by category."""
    print("\n" + "=" * 80)
    print(" 🎨 DESIGN PATTERNS IN PYTHON (3.12+) - CATALOG")
    print("=" * 80)
    for category, patterns in PATTERN_REGISTRY.items():
        print(f"\n📂 [{category.upper()} PATTERNS]")
        for name, desc in sorted(patterns.items()):
            print(f"  • {name:<26} : {desc}")
    print("\nRun any pattern using: python -m design_patterns.cli run <category> <pattern_name>")
    print("=" * 80 + "\n")


def run_pattern(category: str, pattern: str) -> bool:
    """Dynamically imports and executes a pattern module demo."""
    cat_key = category.lower()
    pat_key = pattern.lower()

    if cat_key not in PATTERN_REGISTRY:
        print(f"Error: Unknown category '{category}'. Available: {list(PATTERN_REGISTRY.keys())}")
        return False

    if pat_key not in PATTERN_REGISTRY[cat_key]:
        available = list(PATTERN_REGISTRY[cat_key].keys())
        print(f"Error: Unknown pattern '{pattern}' in '{category}'. Available: {available}")
        return False

    module_name = f"design_patterns.{cat_key}.{pat_key}"
    print(f"\n>>> Loading and Executing {module_name} ...")
    print("-" * 80)

    try:
        mod = importlib.import_module(module_name)
        # Execute the module's demonstration driver if callable or present
        # In our pattern modules, running the module executes __main__,
        # or we can inspect and run the driver block.
        if hasattr(mod, "__file__") and mod.__file__:
            with open(mod.__file__, encoding="utf-8") as f:
                code = f.read()
            # Execute in clean namespace
            exec_globals: dict[str, Any] = {"__name__": "__main__"}
            exec(compile(code, mod.__file__, "exec"), exec_globals)
        print("-" * 80)
        print(f"✓ Execution of '{pat_key}' completed successfully.\n")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Error during execution: {exc}")
        return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI tool to explore and run software design patterns in Python."
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Command to execute")

    # List command
    subparsers.add_parser("list", help="List all available design patterns")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a specific design pattern demonstration")
    run_parser.add_argument(
        "category", help="Category (creational, structural, behavioral, architectural)"
    )
    run_parser.add_argument(
        "pattern", help="Name of pattern (e.g. factory_method, adapter, strategy)"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.subcommand == "list" or not args.subcommand:
        list_patterns()
    elif args.subcommand == "run":
        success = run_pattern(args.category, args.pattern)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()

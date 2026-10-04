# Design Patterns in Python 🐍

[![CI](https://github.com/sudh29/design_patterns/actions/workflows/ci.yml/badge.svg)](https://github.com/sudh29/design_patterns/actions)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: mypy](https://img.shields.io/badge/type--checked-mypy%20(strict)-brightgreen.svg)](https://mypy-lang.org/)
[![Coverage](https://img.shields.io/badge/coverage-98.5%25-brightgreen.svg)](https://pytest-cov.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, production-grade guide to **28 software design patterns** implemented in Python 3.12+.

This repository showcases the classic 22 Gang of Four (GoF) patterns plus 6 essential Modern Architectural & Enterprise patterns, pairing traditional object-oriented architectures with modern Python idioms (structural subtyping with `Protocol`, context managers, decorators, `__init_subclass__`, `functools.singledispatch`, and operator overloading).

---

## 🌟 Key Highlights

- **28 Fully Implemented Patterns:** 5 Creational, 7 Structural, 10 Behavioral, and 6 Architectural patterns.
- **Strict 5-Section Architecture:** Every module features comprehensive docstrings, Mermaid architecture diagrams, real-world enterprise scenarios, Pythonic alternatives, and runnable driver demos.
- **100% Type-Safe:** Verified under `mypy --strict` with zero type errors.
- **High Test Coverage:** ≥ 98% line coverage verified via `pytest-cov` across 222 unit tests.
- **Interactive CLI Runner:** Explore, filter, and run pattern demonstrations directly from the command line.

---

## 🚀 Quick Start

### Installation

Clone the repository and set up a virtual environment using `uv` (recommended) or standard `venv`:

```bash
# Clone repository
git clone git@github.com:sudh29/design_patterns.git
cd design_patterns

# Install with development dependencies using uv
uv sync
# OR using pip:
# python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
```

### Exploring & Running Patterns via CLI

The project includes a built-in CLI tool `design-patterns`:

```bash
# List all 28 available patterns grouped by category
uv run design-patterns --list

# Filter patterns by category
uv run design-patterns --list --category architectural

# Execute a pattern demonstration
uv run design-patterns --run factory_method
uv run design-patterns --run unit_of_work
uv run design-patterns --run visitor
```

### Running Modules Directly

You can also run any pattern module directly:

```bash
python -m design_patterns.creational.factory_method
python -m design_patterns.structural.decorator
python -m design_patterns.behavioral.strategy
python -m design_patterns.architectural.dependency_injection
```

---

## 📚 Pattern Index

### 1. Creational Patterns (5)

| Pattern | Module | Real-World Scenario | Pythonic Idioms |
|---------|--------|---------------------|-----------------|
| **Factory Method** | [`creational.factory_method`](src/design_patterns/creational/factory_method.py) | Multi-channel notification delivery (Email, SMS, Slack) | Callable registry dictionary |
| **Abstract Factory** | [`creational.abstract_factory`](src/design_patterns/creational/abstract_factory.py) | Cross-platform cloud infrastructure provisioning (AWS, Azure, GCP) | Protocol-based abstract factories |
| **Builder** | [`creational.builder`](src/design_patterns/creational/builder.py) | HTTP request payload constructor with immutable options | Fluent chaining with validation |
| **Prototype** | [`creational.prototype`](src/design_patterns/creational/prototype.py) | Microservice configuration cloning and variance | `copy.deepcopy` & `__copy__` overrides |
| **Singleton** | [`creational.singleton`](src/design_patterns/creational/singleton.py) | Database connection pool manager | Thread-safe `__new__` locking & module-level singletons |

### 2. Structural Patterns (7)

| Pattern | Module | Real-World Scenario | Pythonic Idioms |
|---------|--------|---------------------|-----------------|
| **Adapter** | [`structural.adapter`](src/design_patterns/structural/adapter.py) | Legacy XML analytics billing bridge to modern JSON APIs | Class adapter & object adapter |
| **Bridge** | [`structural.bridge`](src/design_patterns/structural/bridge.py) | Database query abstraction decoupled from SQL engines | Structural subtyping with `Protocol` |
| **Composite** | [`structural.composite`](src/design_patterns/structural/composite.py) | File system directory tree structure with size calculation | Recursive iteration & generator traversal |
| **Decorator** | [`structural.decorator`](src/design_patterns/structural/decorator.py) | API request caching, authentication, and execution rate limiting | First-class function decorators (`@functools.wraps`) |
| **Facade** | [`structural.facade`](src/design_patterns/structural/facade.py) | Unified high-level e-commerce checkout coordinating inventory, billing, shipping | Simplified unified client interface |
| **Flyweight** | [`structural.flyweight`](src/design_patterns/structural/flyweight.py) | High-volume gaming particle effects rendering engine | `__slots__` memory optimization & intrinsic state caching |
| **Proxy** | [`structural.proxy`](src/design_patterns/structural/proxy.py) | Lazy-loaded heavy S3 file storage with access authorization and caching | Virtual proxy with transparent attribute delegation |

### 3. Behavioral Patterns (10)

| Pattern | Module | Real-World Scenario | Pythonic Idioms |
|---------|--------|---------------------|-----------------|
| **Chain of Responsibility** | [`behavioral.chain_of_responsibility`](src/design_patterns/behavioral/chain_of_responsibility.py) | HTTP middleware security pipeline (Auth -> RateLimit -> Schema) | Fluent pipeline builder & generators |
| **Command** | [`behavioral.command`](src/design_patterns/behavioral/command.py) | Text editor transactional command history with Undo/Redo | Reversible command objects & callable invokers |
| **Iterator** | [`behavioral.iterator`](src/design_patterns/behavioral/iterator.py) | In-order traversal across Binary Search Tree data structures | Python iterator protocol (`__iter__` / `__next__`) & generator functions |
| **Mediator** | [`behavioral.mediator`](src/design_patterns/behavioral/mediator.py) | Air traffic control tower coordinating commercial flight landings | Central message hub decoupling colleagues |
| **Memento** | [`behavioral.memento`](src/design_patterns/behavioral/memento.py) | Financial account balance ledger snapshot rollback | Immutable mementos with state capture |
| **Observer** | [`behavioral.observer`](src/design_patterns/behavioral/observer.py) | Real-time stock ticker price updates streaming to trading bots and audit loggers | One-to-many event subscription |
| **State** | [`behavioral.state`](src/design_patterns/behavioral/state.py) | E-commerce order lifecycle transitions (Draft -> Paid -> Shipped -> Cancelled) | Finite state machine encapsulation |
| **Strategy** | [`behavioral.strategy`](src/design_patterns/behavioral/strategy.py) | Dynamic checkout pricing discounts (Percentage, Flat, Tiered Volume) | First-class functions as pluggable strategies |
| **Template Method** | [`behavioral.template_method`](src/design_patterns/behavioral/template_method.py) | Invariant ETL data mining pipeline (Extract -> Parse -> Clean -> Transform -> Load) | Subclass registration via `__init_subclass__` |
| **Visitor** | [`behavioral.visitor`](src/design_patterns/behavioral/visitor.py) | Multi-asset portfolio tax liability calculator (Stocks, Bonds, Crypto) | Double dispatch & `functools.singledispatchmethod` |

### 4. Architectural & Enterprise Patterns (6)

| Pattern | Module | Real-World Scenario | Pythonic Idioms |
|---------|--------|---------------------|-----------------|
| **Dependency Injection** | [`architectural.dependency_injection`](src/design_patterns/architectural/dependency_injection.py) | Inversion of Control (IoC) service container with `SINGLETON` and `TRANSIENT` scopes | Constructor injection & provider resolution |
| **Repository** | [`architectural.repository`](src/design_patterns/architectural/repository.py) | Decoupling domain models from persistence mechanisms | Collection-like generic repository abstraction |
| **Unit of Work** | [`architectural.unit_of_work`](src/design_patterns/architectural/unit_of_work.py) | Coordinating atomic business transactions across multiple repositories | Python context manager (`with UnitOfWork():`) with rollback semantics |
| **Specification** | [`architectural.specification`](src/design_patterns/architectural/specification.py) | E-commerce catalog product filtering predicates | Composable boolean logic via operator overloading (`&`, `\|`, `~`) |
| **Event Pub/Sub** | [`architectural.event_pubsub`](src/design_patterns/architectural/event_pubsub.py) | Domain event dispatcher for asynchronous microservice workflows | Typed event envelopes & `@bus.subscribe(EventClass)` decorators |
| **Registry** | [`architectural.registry`](src/design_patterns/architectural/registry.py) | Dynamic document exporter plugin system (Markdown, HTML, JSON) | Decorator-based registration (`@registry.register`) & dynamic lookup |

---

## 📂 Project Structure

```
design_patterns/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI matrix (Python 3.10-3.13)
├── src/
│   └── design_patterns/
│       ├── __init__.py
│       ├── cli.py               # Interactive & Headless CLI runner
│       ├── creational/          # 5 Creational patterns + __init__.py
│       ├── structural/          # 7 Structural patterns + __init__.py
│       ├── behavioral/          # 10 Behavioral patterns + __init__.py
│       └── architectural/       # 6 Architectural patterns + __init__.py
├── tests/
│   ├── test_cli.py              # CLI test suite
│   ├── test_creational/         # Creational test suite
│   ├── test_structural/         # Structural test suite
│   ├── test_behavioral/         # Behavioral test suite
│   └── test_architectural/      # Architectural test suite
├── .pre-commit-config.yaml      # Git pre-commit hooks (Ruff format + lint)
├── CHANGELOG.md                 # Version history & release notes
├── CONTRIBUTING.md              # Contribution guide & pattern template
├── Makefile                     # Common development workflow commands
├── pyproject.toml               # Project metadata, dependencies & tool configs
└── README.md                    # Project overview & documentation
```

---

## 🛠️ Development & Quality Gates

This project enforces strict quality standards via a comprehensive `Makefile`:

```bash
# Run Ruff linting
make lint

# Automatically format code with Ruff
make format

# Run strict static type checking with mypy
make typecheck

# Run test suite
make test

# Run tests with coverage reporting (enforces ≥95% threshold)
make test-cov

# Clean build caches
make clean
```

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code conventions, the standard 5-section anatomy, and quality requirements.

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
Copyright © 2026 Sudhanshu Chaudhary.
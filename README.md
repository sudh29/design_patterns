# Design Patterns in Python (3.12+)

A modern, production-grade guide to **Software Design Patterns implemented in Python 3.12+**.

This repository is designed from the ground up for software engineers, architects, and technical interview candidates looking for **clean, idiomatic, fully type-annotated, and thoroughly tested** implementations of software design patterns.

---

## 🌟 Key Features

- **Modern Python 3.12+ Idioms**: Built with `typing.Protocol`, `abc.ABC`, `dataclasses`, structural pattern matching `match/case`, and `typing.Self`.
- **Anti-Pattern vs. Clean Pattern**: Contrasts naive/tightly-coupled code with refactored, SOLID-compliant architectures.
- **Pythonic Twists**: Explains where Python's built-in features supersede traditional GoF boilerplate (e.g., first-class functions for Strategy, decorators for Decorator, generators for Iterator, metaclasses/modules for Singleton).
- **Practical Domain Scenarios**: Concrete real-world problems (multi-cloud orchestration, payment gateways, e-commerce checkout, financial ledgers, video transcoding, and IoC containers).
- **100% Type-Safe & Linted**: Checked with `mypy --strict` and `ruff`.
- **Extensive Test Suite**: 160+ unit tests with **>97% test coverage** via `pytest`.
- **Interactive CLI Runner**: Explore, inspect, and execute any pattern interactively.

---

## 📂 Project Architecture

```
design_patterns/
├── src/design_patterns/
│   ├── creational/           # Object creation mechanisms
│   │   ├── factory_method.py
│   │   ├── abstract_factory.py
│   │   ├── builder.py
│   │   ├── prototype.py
│   │   └── singleton.py
│   ├── structural/           # Object composition & structure
│   │   ├── adapter.py
│   │   ├── bridge.py
│   │   ├── composite.py
│   │   ├── decorator.py
│   │   ├── facade.py
│   │   ├── flyweight.py
│   │   └── proxy.py
│   ├── behavioral/           # Algorithms & responsibility assignment
│   │   ├── chain_of_responsibility.py
│   │   ├── command.py
│   │   ├── iterator.py
│   │   ├── mediator.py
│   │   ├── memento.py
│   │   ├── observer.py
│   │   ├── state.py
│   │   ├── strategy.py
│   │   ├── template_method.py
│   │   └── visitor.py
│   ├── architectural/        # Modern enterprise & domain patterns
│   │   ├── dependency_injection.py
│   │   ├── repository.py
│   │   ├── unit_of_work.py
│   │   ├── specification.py
│   │   ├── event_pubsub.py
│   │   └── registry.py
│   └── cli.py                # Interactive CLI tool
└── tests/                    # 160+ unit tests mirroring src/
```

---

## 📚 Pattern Index & Real-World Catalog

### 1. Creational Patterns
| Pattern | Module | Real-World Scenario | Pythonic Nuance |
| :--- | :--- | :--- | :--- |
| **Factory Method** | [`factory_method.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/creational/factory_method.py) | Multi-channel Notification Dispatcher (Email, SMS, Slack) | Dynamic registry-based factory decorator |
| **Abstract Factory** | [`abstract_factory.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/creational/abstract_factory.py) | Multi-Cloud Resource Provisioner (AWS vs GCP) | Protocol duck-typing & tuple-based factory maps |
| **Builder** | [`builder.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/creational/builder.py) | Fluent HTTP Request Builder with Invariant Validation | Method chaining returning `Self`, frozen dataclasses |
| **Prototype** | [`prototype.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/creational/prototype.py) | Document & Invoice Template Deep-Cloning | `copy.deepcopy` & `__deepcopy__` customization |
| **Singleton** | [`singleton.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/creational/singleton.py) | Database Connection Pool & Application Settings | Thread-safe Metaclass & Borg (Monostate) pattern |

### 2. Structural Patterns
| Pattern | Module | Real-World Scenario | Pythonic Nuance |
| :--- | :--- | :--- | :--- |
| **Adapter** | [`adapter.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/structural/adapter.py) | Legacy XML/SOAP Payment Gateway to Modern JSON/REST | Object Adapter composition vs Functional wrappers |
| **Bridge** | [`bridge.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/structural/bridge.py) | Notification Messaging vs Delivery Transport Channels | Decouples orthogonal dimensions without class explosion |
| **Composite** | [`composite.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/structural/composite.py) | Hierarchical File System & Recursive Directory Sizing | Recursive `yield from` generator iteration (`__iter__`) |
| **Decorator** | [`decorator.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/structural/decorator.py) | Service Caching, Audit Logging & Rate Limiting | GoF class decorators vs `functools.wraps` functions |
| **Facade** | [`facade.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/structural/facade.py) | Complex Multimedia Transcoding Subsystem Pipeline | High-level unified orchestrator over granular codecs |
| **Flyweight** | [`flyweight.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/structural/flyweight.py) | Forest Ecosystem Simulation with Shared Meshes | `__slots__` memory optimization & flyweight cache |
| **Proxy** | [`proxy.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/structural/proxy.py) | Virtual Lazy Document Loader & RBAC Protection Proxy | Dynamic delegation and lazy property evaluation |

### 3. Behavioral Patterns
| Pattern | Module | Real-World Scenario | Pythonic Nuance |
| :--- | :--- | :--- | :--- |
| **Chain of Responsibility** | [`chain_of_responsibility.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/chain_of_responsibility.py) | HTTP Middleware Pipeline (Auth -> RateLimit -> Schema) | Short-circuiting handler chain with context bag |
| **Command** | [`command.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/command.py) | Text Document Editor with Undo/Redo Stacks | Encapsulated command actions with snapshot state |
| **Iterator** | [`iterator.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/iterator.py) | Binary Search Tree Traversal | Custom Iterator class vs recursive `yield from` generators |
| **Mediator** | [`mediator.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/mediator.py) | Air Traffic Control (ATC) Runway Clearance Coordinator | Decouples O(N^2) colleague dependencies |
| **Memento** | [`memento.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/memento.py) | Financial Ledger Checkpoint Snapshot & Rollback | Encapsulated, immutable frozen dataclass snapshots |
| **Observer** | [`observer.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/observer.py) | Real-time Stock Price Ticker with Automated Bot Traders | Pub/Sub notifications with decoupled observers |
| **State** | [`state.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/state.py) | E-commerce Order Finite State Machine Lifecycle | Eliminates conditionals by delegating to State objects |
| **Strategy** | [`strategy.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/strategy.py) | E-commerce Dynamic Checkout Discount Engine | Class-based strategies vs First-Class callables |
| **Template Method** | [`template_method.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/template_method.py) | Data Engineering ETL Pipeline (CSV & REST API) | Invariant execution skeleton with abstract steps & hooks |
| **Visitor** | [`visitor.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/behavioral/visitor.py) | Financial Asset Tax & Liquidity Evaluation Engine | Double dispatch vs `functools.singledispatch` |

### 4. Architectural & Modern Patterns
| Pattern | Module | Real-World Scenario | Key Concepts |
| :--- | :--- | :--- | :--- |
| **Dependency Injection** | [`dependency_injection.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/architectural/dependency_injection.py) | Lightweight IoC Container | Constructor injection, Singleton vs Transient scopes |
| **Repository** | [`repository.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/architectural/repository.py) | Domain Persistence Decoupling | Generic repository protocol `Repository[T, ID]` |
| **Unit of Work** | [`unit_of_work.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/architectural/unit_of_work.py) | Atomic Multi-Repository Transactions | Context manager (`with UnitOfWork():`) rollback semantics |
| **Specification** | [`specification.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/architectural/specification.py) | Composable Catalog Search Rules | Operator overloading (`&`, `\|`, `~`) for boolean algebra |
| **Event Pub/Sub** | [`event_pubsub.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/architectural/event_pubsub.py) | Domain Event Bus | Event envelopes, typed subscriber dispatch, error isolation |
| **Registry** | [`registry.py`](file:///home/liber_primus/code/design_patterns/src/design_patterns/architectural/registry.py) | Extensible Plugin System | Dynamic decorator-based registration (`@reg.register`) |

---

## 🚀 Quickstart & Development

### 1. Environment Setup

Using [`uv`](https://github.com/astral-sh/uv) (recommended) or standard `venv`:

```bash
# Clone the repository
git clone https://github.com/liber_primus/design_patterns.git
cd design_patterns

# Create virtual environment and install dev dependencies
uv venv .venv
uv pip install -e ".[dev]"
```

### 2. Running the Interactive CLI Runner

List all patterns:
```bash
.venv/bin/python -m design_patterns.cli list
```

Run any pattern live:
```bash
# Run Factory Method
.venv/bin/python -m design_patterns.cli run creational factory_method

# Run Strategy Pattern
.venv/bin/python -m design_patterns.cli run behavioral strategy

# Run Unit of Work Pattern
.venv/bin/python -m design_patterns.cli run architectural unit_of_work
```

You can also run any module directly:
```bash
.venv/bin/python -m design_patterns.structural.adapter
```

### 3. Running Tests & Quality Verification

Run the complete test suite with coverage:
```bash
.venv/bin/pytest --cov=design_patterns --cov-report=term-missing tests/
```

Check linting and formatting:
```bash
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
```

Run static type checking in strict mode:
```bash
.venv/bin/mypy src tests
```

---

## 📄 License

MIT License. See [LICENSE](file:///home/liber_primus/code/design_patterns/LICENSE) for details.
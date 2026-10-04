# Contributing to Design Patterns in Python 🐍

Thank you for your interest in contributing to this project! We welcome contributions, bug fixes, documentation improvements, and additional pattern demonstrations.

To ensure consistency, readability, and production-grade software quality across all modules, please adhere to the following guidelines.

---

## 🏗️ Development Setup

We recommend using [uv](https://docs.astral.sh/uv/) for lightning-fast, reproducible dependency management:

```bash
# Clone the repository
git clone git@github.com:sudh29/design_patterns.git
cd design_patterns

# Install editable package with dev dependencies
uv sync

# Or with traditional virtualenv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optionally install git pre-commit hooks:

```bash
uv run pre-commit install
```

---

## 📐 Anatomy of a Design Pattern Module

Every pattern module must strictly follow our standard **5-section anatomy**:

### 1. Module Docstring & Metadata
- **Classification:** Category (`Creational`, `Structural`, `Behavioral`, or `Architectural`).
- **Intent:** Concise GoF or architectural definition.
- **Motivation & Real-World Analogy:** A realistic enterprise problem statement (avoid toy `Dog/Cat` examples).
- **Mermaid Architecture Diagram:** A clear `classDiagram` showing contracts, concrete classes, and relationships.

### 2. Protocol / Interface Contracts
- Declare interfaces using `typing.Protocol` (for structural typing) or `abc.ABC` (when default implementations/template methods are necessary).
- Provide clear type annotations on all methods.

### 3. Concrete Implementations
- Provide production-grade concrete implementations addressing the real-world scenario.
- Handle edge cases, validations, and custom exceptions.

### 4. Pythonic Twist
- Highlight how modern Python simplifies or improves the pattern:
  - First-class functions / callables
  - Decorators (`@wraps`, `@register`)
  - Context managers (`with ... :`)
  - `__init_subclass__` auto-registration
  - `functools.singledispatch` / `functools.singledispatchmethod`
  - Operator overloading (`&`, `|`, `~`)

### 5. Driver / Demonstration Block
- An executable `if __name__ == "__main__":` block demonstrating the pattern in action.
- Print clear, readable output tracing the pattern execution.

---

## 🧪 Testing Guidelines

Every pattern must have a corresponding test module in `tests/test_<category>/test_<pattern>.py`:

1. **Isolation:** Unit tests must be fast, deterministic, and self-contained (no external database or network calls).
2. **Coverage:** All code branches, error conditions, and Pythonic variations must be tested.
3. **Threshold:** The repository enforces a minimum test coverage of **≥ 95%** (`make test-cov`).

---

## 🚦 Quality Gates

Before submitting a Pull Request, all of the following commands must succeed with zero errors or warnings:

```bash
# 1. Formatting
make format

# 2. Linting (Ruff rules: E, W, F, I, B, UP, SIM)
make lint

# 3. Static Type Checking (mypy in strict mode)
make typecheck

# 4. Tests and Coverage
make test-cov
```

---

## 📝 Commit Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` A new pattern or capability (e.g. `feat: implement Template Method pattern`)
- `fix:` A bug fix or formatting correction (e.g. `fix: handle edge case in checkout cart`)
- `test:` Adding or updating tests (e.g. `test: add tests for Visitor pattern`)
- `docs:` Documentation changes (e.g. `docs: update README with pattern index`)
- `chore:` Maintenance, Makefile, dependencies, or tooling updates (e.g. `chore: configure pre-commit`)

Each commit should be **atomic and focused** on a single logical change.

---

## 🚀 Submitting a Pull Request

1. Fork the repository and create a feature branch (`git checkout -b feat/my-new-feature`).
2. Implement your changes following the 5-section anatomy.
3. Add comprehensive tests in `tests/`.
4. Run `make lint && make format && make typecheck && make test-cov` to verify all quality gates pass.
5. Commit your changes with conventional commit messages.
6. Push to your branch and open a Pull Request with a clear summary of your changes.

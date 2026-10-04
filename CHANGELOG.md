# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] - 2026-10-04

### Added
- **28 Design Patterns Implemented:**
  - **Creational (5):** Factory Method, Abstract Factory, Builder, Prototype, Singleton.
  - **Structural (7):** Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy.
  - **Behavioral (10):** Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor.
  - **Architectural & Enterprise (6):** Dependency Injection, Repository, Unit of Work, Specification, Event Pub/Sub, Registry.
- **Interactive & Headless CLI Runner (`design-patterns`):**
  - List and inspect all 28 patterns (`--list`, `--category`).
  - Run executable demonstrations directly from the command line (`--run <pattern>`).
- **Comprehensive Test Suite & Quality Gates:**
  - 222 unit tests with **≥ 98% line coverage**.
  - Strict type checking with `mypy --strict`.
  - Modern formatting and linting with `ruff`.
  - Development `Makefile` automating `lint`, `format`, `typecheck`, `test`, `test-cov`.
- **Pre-commit Automation:**
  - `.pre-commit-config.yaml` with Ruff lint and format hooks.
- **Documentation:**
  - Comprehensive `README.md` with badges, quickstart guide, full pattern index table, and architectural overview.
  - Detailed `CONTRIBUTING.md` guidelines outlining the 5-section pattern anatomy and PR review criteria.
  - `IMPROVEMENT_PLAN.md` roadmap and gap analysis.

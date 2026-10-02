"""Dependency Injection & Inversion of Control (IoC) Pattern.

Classification: Architectural / Modern Enterprise
Intent:
    Invert the control of dependency resolution: instead of objects creating
    their dependencies directly, dependencies are provided (injected) from an
    external container or composition root.

Motivation & Real-World Analogy:
    In large backend microservices, a `UserService` depends on a `DatabaseRepository`,
    an `EmailClient`, and a `MetricsCollector`. If `UserService` directly calls
    `self.repo = PostgresRepository()`, unit testing becomes nearly impossible without
    spinning up a live database, and swapping implementations violates the Dependency
    Inversion Principle (DIP).
    With Dependency Injection:
    1. Dependencies are injected via constructor arguments (`Protocol` based).
    2. An IoC Container automatically resolves and manages lifecycles:
       - **Transient**: A fresh instance is created on every resolution.
       - **Singleton**: The same instance is shared across the application.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class UserRepository {
            <<protocol>>
            +get_by_id(user_id: str) dict | None
        }
        class NotificationService {
            <<protocol>>
            +send_welcome(email: str) bool
        }
        class UserService {
            -repo: UserRepository
            -notifier: NotificationService
            +register(user_id: str, email: str) bool
        }
        class Container {
            -_bindings: dict
            -_singletons: dict
            +register_transient(interface, factory)
            +register_singleton(interface, factory)
            +resolve(interface) Any
        }
        UserService o--> UserRepository : injected
        UserService o--> NotificationService : injected
        Container ..> UserService : resolves
    ```
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum, auto
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


# ==============================================================================
# 1. Domain Interfaces (Protocols)
# ==============================================================================
class UserRepository(Protocol):
    def find_user(self, user_id: str) -> dict[str, str] | None: ...
    def save_user(self, user_id: str, email: str) -> None: ...


class NotificationService(Protocol):
    def send_welcome(self, email: str) -> bool: ...


# ==============================================================================
# 2. Concrete Implementations
# ==============================================================================
class InMemoryUserRepository:
    """In-memory user persistence for local/testing execution."""

    def __init__(self) -> None:
        self.storage: dict[str, dict[str, str]] = {}

    def find_user(self, user_id: str) -> dict[str, str] | None:
        return self.storage.get(user_id)

    def save_user(self, user_id: str, email: str) -> None:
        self.storage[user_id] = {"id": user_id, "email": email}


class ConsoleNotificationService:
    """Delivers notifications to console output."""

    def __init__(self) -> None:
        self.sent_emails: list[str] = []

    def send_welcome(self, email: str) -> bool:
        self.sent_emails.append(email)
        return True


class UserService:
    """High-level domain service with constructor dependency injection."""

    def __init__(self, repo: UserRepository, notifier: NotificationService) -> None:
        self._repo = repo
        self._notifier = notifier

    def register_user(self, user_id: str, email: str) -> bool:
        if self._repo.find_user(user_id) is not None:
            raise ValueError(f"User {user_id} already exists")

        self._repo.save_user(user_id, email)
        self._notifier.send_welcome(email)
        return True


# ==============================================================================
# 3. Lightweight IoC Container
# ==============================================================================
class Scope(Enum):
    TRANSIENT = auto()
    SINGLETON = auto()


class Container:
    """Lightweight Inversion of Control Container supporting Singleton and Transient scopes."""

    def __init__(self) -> None:
        self._factories: dict[Any, Callable[[Container], Any]] = {}
        self._scopes: dict[Any, Scope] = {}
        self._instances: dict[Any, Any] = {}

    def register(
        self,
        interface: Any,
        factory: Callable[[Container], Any],
        scope: Scope = Scope.TRANSIENT,
    ) -> None:
        self._factories[interface] = factory
        self._scopes[interface] = scope

    def resolve(self, interface: Any) -> Any:
        if interface not in self._factories:
            name = getattr(interface, "__name__", str(interface))
            raise KeyError(f"No binding registered for {name}")

        scope = self._scopes[interface]
        if scope == Scope.SINGLETON:
            if interface not in self._instances:
                self._instances[interface] = self._factories[interface](self)
            return self._instances[interface]

        # Transient: new instance every time
        return self._factories[interface](self)


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    container = Container()

    # Register dependencies
    container.register(UserRepository, lambda c: InMemoryUserRepository(), scope=Scope.SINGLETON)
    container.register(
        NotificationService, lambda c: ConsoleNotificationService(), scope=Scope.TRANSIENT
    )
    container.register(
        UserService,
        lambda c: UserService(
            repo=c.resolve(UserRepository),
            notifier=c.resolve(NotificationService),
        ),
        scope=Scope.TRANSIENT,
    )

    # Resolve top-level service
    user_service = container.resolve(UserService)
    user_service.register_user("usr_01", "carol@domain.com")
    print("User registered successfully via Dependency Injection Container.")

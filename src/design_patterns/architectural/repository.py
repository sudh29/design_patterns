"""Repository Design Pattern.

Classification: Architectural / Enterprise
Intent:
    Mediate between the domain and data mapping layers using a collection-like interface
    for accessing domain objects. Decouples domain entities and business logic from
    underlying persistence mechanisms (databases, ORMs, files, APIs).

Motivation & Real-World Analogy:
    In complex business software, domain entities (e.g., `Customer`, `Product`, `Order`)
    represent core business rules and state. Coupling these entities directly to SQL queries,
    MongoDB drivers, or external REST APIs leaks infrastructure concerns into the domain layer,
    makes unit testing slow and dependent on external databases, and tightly couples code
    to specific database schemas.
    The Repository pattern provides an in-memory collection-like abstraction for persisting
    and querying aggregates. Code interacting with the domain layer operates purely on domain
    models, enabling transparent substitution of storage backends (e.g., switching from
    PostgreSQL to an In-Memory hash map during test execution).

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Repository~T, ID~ {
            <<protocol>>
            +get(id: ID) T?
            +list_all() list~T~
            +add(entity: T) None
            +update(entity: T) None
            +delete(id: ID) bool
            +count() int
        }
        class User {
            +id: str
            +email: str
            +name: str
            +is_active: bool
        }
        class InMemoryUserRepository {
            -storage: dict~str, User~
            +get(id: str) User?
            +list_all() list~User~
            +add(entity: User) None
            +update(entity: User) None
            +delete(id: str) bool
            +count() int
            +find_by_email(email: str) User?
        }
        Repository <|.. InMemoryUserRepository
        InMemoryUserRepository o--> User : manages
    ```
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar

T = TypeVar("T")
ID_contra = TypeVar("ID_contra", contravariant=True)


# ==============================================================================
# 1. Domain Entities
# ==============================================================================
@dataclass
class User:
    """Core domain entity representing a registered user."""

    id: str
    email: str
    full_name: str
    is_active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def deactivate(self) -> None:
        """Domain behavior: Deactivates user account."""
        self.is_active = False

    def activate(self) -> None:
        """Domain behavior: Re-activates user account."""
        self.is_active = True


# ==============================================================================
# 2. Generic Repository Protocol
# ==============================================================================
class Repository(Protocol[T, ID_contra]):
    """Generic repository protocol for collection-like entity persistence."""

    def get(self, entity_id: ID_contra) -> T | None: ...

    def list_all(self) -> list[T]: ...

    def add(self, entity: T) -> None: ...

    def update(self, entity: T) -> None: ...

    def delete(self, entity_id: ID_contra) -> bool: ...

    def count(self) -> int: ...


# ==============================================================================
# 3. Concrete Repository Implementation (In-Memory)
# ==============================================================================
class InMemoryUserRepository:
    """Thread-safe-ready, in-memory repository implementation for User entities."""

    def __init__(self) -> None:
        self._storage: dict[str, User] = {}

    def get(self, entity_id: str) -> User | None:
        return self._storage.get(entity_id)

    def list_all(self) -> list[User]:
        return list(self._storage.values())

    def add(self, entity: User) -> None:
        if entity.id in self._storage:
            raise ValueError(f"Entity with id '{entity.id}' already exists")
        self._storage[entity.id] = entity

    def update(self, entity: User) -> None:
        if entity.id not in self._storage:
            raise KeyError(f"Entity with id '{entity.id}' does not exist")
        self._storage[entity.id] = entity

    def delete(self, entity_id: str) -> bool:
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    def count(self) -> int:
        return len(self._storage)

    # Domain-specific specialized query methods
    def find_by_email(self, email: str) -> User | None:
        """Lookup active user by unique email address."""
        norm_email = email.strip().lower()
        for user in self._storage.values():
            if user.email.strip().lower() == norm_email:
                return user
        return None

    def list_active(self) -> list[User]:
        """Return only active users."""
        return [u for u in self._storage.values() if u.is_active]


# ==============================================================================
# 4. Domain Service utilizing Repository
# ==============================================================================
class UserService:
    """Domain service orchestrating user management via repository abstraction."""

    def __init__(self, repository: Repository[User, str]) -> None:
        self._repo = repository

    def register_user(self, user_id: str, email: str, name: str) -> User:
        if (
            isinstance(self._repo, InMemoryUserRepository)
            and self._repo.find_by_email(email) is not None
        ):
            raise ValueError(f"User with email '{email}' is already registered")
        user = User(id=user_id, email=email, full_name=name)

        self._repo.add(user)
        return user

    def deactivate_user(self, user_id: str) -> bool:
        user = self._repo.get(user_id)
        if user is None:
            return False
        user.deactivate()
        self._repo.update(user)
        return True


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    repo = InMemoryUserRepository()
    service = UserService(repo)

    u1 = service.register_user("usr_001", "dev@example.com", "Dev User")
    u2 = service.register_user("usr_002", "admin@example.com", "Admin User")

    print(f"Total Users: {repo.count()}")
    print(f"Found by email: {repo.find_by_email('dev@example.com')}")

    service.deactivate_user("usr_001")
    print(f"Active Users: {[u.full_name for u in repo.list_active()]}")

"""Singleton Design Pattern.

Classification: Creational
Intent:
    Ensure a class only has one instance, and provide a global point of access to it.

Motivation & Real-World Analogy:
    In database connection pools, hardware drivers, or telemetry collectors,
    having multiple competing instances can lead to exhausted socket pools,
    conflicting write operations, or split-brain states.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class SingletonMeta {
            <<metaclass>>
            -_instances: dict
            -_lock: Lock
            +__call__()
        }
        class DatabaseConnectionPool {
            -connection_string: str
            -max_connections: int
            +get_connection()
        }
        class BorgMonostate {
            -_shared_state: dict
            +state: Any
        }
        DatabaseConnectionPool ..> SingletonMeta : metaclass
    ```

Trade-offs & Anti-Pattern Risks:
    Singletons introduce global state, hidden dependencies, and state leakage
    across unit test suites. Modern Python architectures frequently favor
    Dependency Injection over Singletons.
"""

from __future__ import annotations

import threading
from typing import Any, ClassVar


# ==============================================================================
# 1. Anti-Pattern / Naive Approach (Non-Thread-Safe Singleton)
# ==============================================================================
class NaiveSingleton:
    """Anti-pattern: Race conditions occur when multiple threads check instance simultaneously."""

    _instance: ClassVar[NaiveSingleton | None] = None

    def __init__(self, value: str) -> None:
        self.value = value

    @classmethod
    def get_instance(cls, value: str) -> NaiveSingleton:
        if cls._instance is None:
            # Race condition: Two threads can enter here simultaneously!
            cls._instance = cls(value)
        return cls._instance


# ==============================================================================
# 2. Clean Pattern Implementation: Thread-Safe Singleton via Metaclass
# ==============================================================================
class SingletonMeta(type):
    """Thread-safe implementation of Singleton using a Metaclass and double-checked locking."""

    _instances: ClassVar[dict[type, Any]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        # First check (unlocked for performance)
        if cls not in cls._instances:
            with cls._lock:
                # Second check (locked for thread safety)
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class DatabaseConnectionPool(metaclass=SingletonMeta):
    """Concrete Singleton representing a centralized database connection pool."""

    def __init__(self, dsn: str = "postgresql://localhost:5432/production") -> None:
        self.dsn = dsn
        self.active_connections: int = 0
        self.is_connected: bool = True

    def acquire(self) -> str:
        self.active_connections += 1
        return f"Conn-{self.active_connections} from {self.dsn}"

    def release(self) -> None:
        if self.active_connections > 0:
            self.active_connections -= 1


# ==============================================================================
# 3. Pythonic Alternative: Borg Pattern (Monostate)
# ==============================================================================
class BorgMonostate:
    """Pythonic alternative: All instances share the same __dict__ (state),

    even though they are distinct object instances.
    """

    _shared_state: ClassVar[dict[str, Any]] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state

    @property
    def config(self) -> dict[str, Any]:
        return self._shared_state


class AppSettings(BorgMonostate):
    """Application settings sharing state across instances."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self._shared_state.update(kwargs)


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    print("=== Thread-Safe Singleton Verification ===")
    pool1 = DatabaseConnectionPool()
    pool2 = DatabaseConnectionPool("different-dsn-will-be-ignored")

    print(f"Pool 1 DSN: {pool1.dsn}")
    print(f"Pool 2 DSN: {pool2.dsn}")
    print(f"Same instance: {pool1 is pool2}")
    assert pool1 is pool2

    print("\n=== Pythonic Borg (Monostate) Verification ===")
    cfg1 = AppSettings(theme="dark", timeout=60)
    cfg2 = AppSettings()

    print(f"Config 1 theme: {cfg1.theme}")  # type: ignore[attr-defined]
    print(f"Config 2 theme: {cfg2.theme}")  # type: ignore[attr-defined]
    print(f"Distinct instances: {cfg1 is not cfg2}")
    print(f"Shared state dict:  {cfg1.__dict__ is cfg2.__dict__}")

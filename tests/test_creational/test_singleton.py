"""Tests for the Singleton and Borg patterns implementation."""

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from design_patterns.creational.singleton import (
    AppSettings,
    BorgMonostate,
    DatabaseConnectionPool,
    NaiveSingleton,
    SingletonMeta,
)


class TestNaiveSingleton:
    def test_naive_singleton_basic(self) -> None:
        NaiveSingleton._instance = None
        s1 = NaiveSingleton.get_instance("first")
        s2 = NaiveSingleton.get_instance("second")
        assert s1 is s2
        assert s1.value == "first"


class TestSingletonMeta:
    def test_singleton_identity(self) -> None:
        # Clear instances for testing isolation
        SingletonMeta._instances.clear()

        pool1 = DatabaseConnectionPool("dsn1")
        pool2 = DatabaseConnectionPool("dsn2")

        assert pool1 is pool2
        assert pool1.dsn == "dsn1"
        assert pool2.dsn == "dsn1"

    def test_singleton_thread_safety(self) -> None:
        SingletonMeta._instances.clear()

        def acquire_pool(idx: int) -> DatabaseConnectionPool:
            return DatabaseConnectionPool(f"thread-dsn-{idx}")

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(acquire_pool, range(50)))

        # All 50 threads received the exact same singleton instance
        first_instance = results[0]
        assert all(res is first_instance for res in results)

    def test_singleton_pool_operations(self) -> None:
        SingletonMeta._instances.clear()
        pool = DatabaseConnectionPool()
        assert pool.active_connections == 0
        conn_str = pool.acquire()
        assert "Conn-1" in conn_str
        assert pool.active_connections == 1
        pool.release()
        assert pool.active_connections == 0
        pool.release()  # should not go below 0
        assert pool.active_connections == 0


class TestBorgMonostate:
    def test_borg_shared_state(self) -> None:
        BorgMonostate._shared_state.clear()

        app1: Any = AppSettings(api_key="secret", debug=True)
        app2: Any = AppSettings()

        # Instances are distinct
        assert app1 is not app2
        # But share exact state dictionary
        assert app1.__dict__ is app2.__dict__
        assert app2.api_key == "secret"
        assert app2.debug is True

    def test_borg_mutation_propagation(self) -> None:
        BorgMonostate._shared_state.clear()

        app1: Any = AppSettings(retries=3)
        app2: Any = AppSettings()

        app2.retries = 5
        assert app1.retries == 5

"""Tests for the Dependency Injection Container implementation."""

import pytest

from design_patterns.architectural.dependency_injection import (
    ConsoleNotificationService,
    Container,
    InMemoryUserRepository,
    NotificationService,
    Scope,
    UserRepository,
    UserService,
)


class TestDependencyInjection:
    def test_transient_scope(self) -> None:
        container = Container()
        container.register(
            NotificationService, lambda c: ConsoleNotificationService(), scope=Scope.TRANSIENT
        )

        n1 = container.resolve(NotificationService)
        n2 = container.resolve(NotificationService)

        assert isinstance(n1, ConsoleNotificationService)
        assert isinstance(n2, ConsoleNotificationService)
        assert n1 is not n2  # Transient gives fresh instances

    def test_singleton_scope(self) -> None:
        container = Container()
        container.register(
            UserRepository, lambda c: InMemoryUserRepository(), scope=Scope.SINGLETON
        )

        repo1 = container.resolve(UserRepository)
        repo2 = container.resolve(UserRepository)

        assert repo1 is repo2  # Singleton gives exact same reference

    def test_unregistered_resolution_raises(self) -> None:
        container = Container()
        with pytest.raises(KeyError, match="No binding registered for UserService"):
            container.resolve(UserService)

    def test_full_service_resolution(self) -> None:
        container = Container()
        container.register(
            UserRepository, lambda c: InMemoryUserRepository(), scope=Scope.SINGLETON
        )
        container.register(
            NotificationService, lambda c: ConsoleNotificationService(), scope=Scope.SINGLETON
        )
        container.register(
            UserService,
            lambda c: UserService(
                repo=c.resolve(UserRepository),
                notifier=c.resolve(NotificationService),
            ),
        )

        service = container.resolve(UserService)
        assert service.register_user("u1", "user@test.com") is True

        with pytest.raises(ValueError, match="already exists"):
            service.register_user("u1", "user@test.com")

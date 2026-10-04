"""Tests for Repository pattern implementation."""

import pytest

from design_patterns.architectural.repository import (
    InMemoryUserRepository,
    User,
    UserService,
)


class TestInMemoryUserRepository:
    def test_add_and_get_user(self) -> None:
        repo = InMemoryUserRepository()
        user = User(id="u1", email="alice@test.com", full_name="Alice Smith")
        repo.add(user)

        retrieved = repo.get("u1")
        assert retrieved is not None
        assert retrieved.id == "u1"
        assert retrieved.email == "alice@test.com"

    def test_get_nonexistent_returns_none(self) -> None:
        repo = InMemoryUserRepository()
        assert repo.get("nonexistent") is None

    def test_duplicate_add_raises_value_error(self) -> None:
        repo = InMemoryUserRepository()
        u1 = User(id="u1", email="a@test.com", full_name="A")
        repo.add(u1)

        with pytest.raises(ValueError, match="already exists"):
            repo.add(u1)

    def test_update_existing_user(self) -> None:
        repo = InMemoryUserRepository()
        u1 = User(id="u1", email="a@test.com", full_name="A")
        repo.add(u1)

        u1.full_name = "A Updated"
        repo.update(u1)

        updated = repo.get("u1")
        assert updated is not None
        assert updated.full_name == "A Updated"

    def test_update_nonexistent_user_raises_key_error(self) -> None:
        repo = InMemoryUserRepository()
        u = User(id="ghost", email="ghost@test.com", full_name="Ghost")
        with pytest.raises(KeyError, match="does not exist"):
            repo.update(u)

    def test_delete_user(self) -> None:
        repo = InMemoryUserRepository()
        u1 = User(id="u1", email="a@test.com", full_name="A")
        repo.add(u1)
        assert repo.count() == 1

        assert repo.delete("u1") is True
        assert repo.count() == 0
        assert repo.get("u1") is None
        assert repo.delete("u1") is False

    def test_list_all_and_count(self) -> None:
        repo = InMemoryUserRepository()
        repo.add(User(id="1", email="1@test.com", full_name="One"))
        repo.add(User(id="2", email="2@test.com", full_name="Two"))

        assert repo.count() == 2
        all_users = repo.list_all()
        assert len(all_users) == 2
        assert {u.id for u in all_users} == {"1", "2"}

    def test_find_by_email_case_insensitive(self) -> None:
        repo = InMemoryUserRepository()
        repo.add(User(id="u1", email="Alice@Domain.COM", full_name="Alice"))

        found = repo.find_by_email("alice@domain.com")
        assert found is not None
        assert found.id == "u1"
        assert repo.find_by_email("bob@domain.com") is None

    def test_list_active_users(self) -> None:
        repo = InMemoryUserRepository()
        active = User(id="1", email="1@test.com", full_name="Active", is_active=True)
        inactive = User(id="2", email="2@test.com", full_name="Inactive", is_active=False)
        repo.add(active)
        repo.add(inactive)

        active_users = repo.list_active()
        assert len(active_users) == 1
        assert active_users[0].id == "1"


class TestUserServiceAndDomainEntities:
    def test_user_service_registration_and_duplicate_check(self) -> None:
        repo = InMemoryUserRepository()
        service = UserService(repo)

        u1 = service.register_user("u1", "unique@test.com", "Unique User")
        assert u1.id == "u1"

        with pytest.raises(ValueError, match="already registered"):
            service.register_user("u2", "unique@test.com", "Duplicate Email")

    def test_user_deactivation_flow(self) -> None:
        repo = InMemoryUserRepository()
        service = UserService(repo)
        service.register_user("u1", "u1@test.com", "User 1")

        assert service.deactivate_user("u1") is True
        user = repo.get("u1")
        assert user is not None
        assert user.is_active is False

        assert service.deactivate_user("nonexistent") is False

    def test_user_entity_activation_methods(self) -> None:
        user = User(id="u", email="e@test.com", full_name="Name")
        assert user.is_active is True
        user.deactivate()
        assert user.is_active is False
        user.activate()
        assert user.is_active is True

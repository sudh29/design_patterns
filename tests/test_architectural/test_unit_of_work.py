"""Tests for the Unit of Work pattern implementation."""

import pytest

from design_patterns.architectural.unit_of_work import (
    BankAccount,
    FakeUnitOfWork,
    transfer_funds,
)


class TestUnitOfWorkPattern:
    def test_successful_atomic_transfer(self) -> None:
        db = {
            "A1": BankAccount("A1", 500.0),
            "A2": BankAccount("A2", 100.0),
        }
        uow = FakeUnitOfWork(db)
        transfer_funds(uow, "A1", "A2", 200.0)

        assert db["A1"].balance == 300.0
        assert db["A2"].balance == 300.0
        assert uow.committed is True

    def test_failed_transfer_rolls_back(self) -> None:
        db = {
            "A1": BankAccount("A1", 100.0),
            "A2": BankAccount("A2", 50.0),
        }
        uow = FakeUnitOfWork(db)

        with pytest.raises(ValueError, match="Insufficient funds"):
            transfer_funds(uow, "A1", "A2", 250.0)

        # Balances must remain unchanged
        assert db["A1"].balance == 100.0
        assert db["A2"].balance == 50.0
        assert uow.rolled_back is True

    def test_uncommitted_with_block_rolls_back(self) -> None:
        db = {"A1": BankAccount("A1", 100.0)}
        uow = FakeUnitOfWork(db)

        with uow:
            uow.accounts.get("A1").balance = 500.0
            # Forgotten commit call!

        # Should rollback automatically on exit
        assert db["A1"].balance == 100.0
        assert uow.rolled_back is True

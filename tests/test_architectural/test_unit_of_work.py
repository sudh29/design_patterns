"""Tests for Unit of Work pattern implementation."""

import pytest

from design_patterns.architectural.unit_of_work import (
    Account,
    BankTransferService,
    InMemoryUnitOfWork,
)


class TestAccountDomainEntity:
    def test_debit_credit_success(self) -> None:
        acc = Account("1", "User", 100.0)
        acc.credit(50.0)
        assert acc.balance == pytest.approx(150.0)

        acc.debit(30.0)
        assert acc.balance == pytest.approx(120.0)

    def test_debit_insufficient_funds_raises(self) -> None:
        acc = Account("1", "User", 50.0)
        with pytest.raises(ValueError, match="Insufficient funds"):
            acc.debit(100.0)

    def test_negative_amounts_raise(self) -> None:
        acc = Account("1", "User", 50.0)
        with pytest.raises(ValueError, match="Debit amount must be positive"):
            acc.debit(-10.0)
        with pytest.raises(ValueError, match="Credit amount must be positive"):
            acc.credit(-10.0)


class TestUnitOfWorkLifecycle:
    def test_successful_transfer_commits_atomically(self) -> None:
        uow = InMemoryUnitOfWork(
            {
                "a1": Account("a1", "Alice", 500.0),
                "a2": Account("a2", "Bob", 200.0),
            }
        )
        service = BankTransferService(uow)

        service.transfer("a1", "a2", 150.0)

        assert uow.committed is True
        assert uow.rolled_back is False
        assert uow._datastore["a1"].balance == pytest.approx(350.0)
        assert uow._datastore["a2"].balance == pytest.approx(350.0)
        assert len(uow.ledger) == 1
        assert "TRANSFERRED $150.00" in uow.ledger[0]

    def test_failed_transfer_rolls_back_entirely(self) -> None:
        uow = InMemoryUnitOfWork(
            {
                "a1": Account("a1", "Alice", 100.0),
                "a2": Account("a2", "Bob", 50.0),
            }
        )
        service = BankTransferService(uow)

        with pytest.raises(ValueError, match="Insufficient funds"):
            service.transfer("a1", "a2", 500.0)

        assert uow.rolled_back is True
        # Both balances must remain at initial state
        assert uow._datastore["a1"].balance == pytest.approx(100.0)
        assert uow._datastore["a2"].balance == pytest.approx(50.0)
        # Ledger entries must be empty
        assert len(uow.ledger) == 0

    def test_missing_account_rolls_back(self) -> None:
        uow = InMemoryUnitOfWork({"a1": Account("a1", "Alice", 100.0)})
        service = BankTransferService(uow)

        with pytest.raises(KeyError, match="Account unknown not found"):
            service.transfer("a1", "unknown", 20.0)

        assert uow.rolled_back is True
        assert uow._datastore["a1"].balance == pytest.approx(100.0)

    def test_get_account_in_active_context(self) -> None:
        uow = InMemoryUnitOfWork({"a1": Account("a1", "Alice", 100.0)})
        with uow:
            acc = uow.get_account("a1")
            assert acc.balance == 100.0
            with pytest.raises(KeyError, match="not found"):
                uow.get_account("missing")

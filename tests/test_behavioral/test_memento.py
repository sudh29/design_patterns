"""Tests for the Memento pattern implementation."""

import pytest

from design_patterns.behavioral.memento import (
    AccountLedger,
    TransactionCaretaker,
)


class TestMementoPattern:
    def test_deposit_and_withdraw_validation(self) -> None:
        ledger = AccountLedger("A1", 100.0)
        with pytest.raises(ValueError, match="Deposit amount must be positive"):
            ledger.deposit(-10)

        with pytest.raises(ValueError, match="Withdrawal amount must be positive"):
            ledger.withdraw(0)

        with pytest.raises(ValueError, match="Insufficient funds"):
            ledger.withdraw(500)

    def test_save_and_restore_cycle(self) -> None:
        ledger = AccountLedger("A1", 200.0)
        caretaker = TransactionCaretaker()

        caretaker.checkpoint(ledger)
        ledger.deposit(300.0)
        assert ledger.balance == 500.0
        assert ledger.transaction_count == 1

        assert caretaker.rollback(ledger) is True
        assert ledger.balance == 200.0
        assert ledger.transaction_count == 0

    def test_empty_caretaker_rollback(self) -> None:
        ledger = AccountLedger("A1", 50.0)
        caretaker = TransactionCaretaker()
        assert caretaker.rollback(ledger) is False

    def test_multi_step_checkpoints(self) -> None:
        ledger = AccountLedger("A1", 10.0)
        caretaker = TransactionCaretaker()

        caretaker.checkpoint(ledger)  # balance 10
        ledger.deposit(10.0)

        caretaker.checkpoint(ledger)  # balance 20
        ledger.deposit(10.0)

        assert ledger.balance == 30.0
        assert caretaker.history_depth() == 2

        caretaker.rollback(ledger)
        assert ledger.balance == 20.0

        caretaker.rollback(ledger)
        assert ledger.balance == 10.0

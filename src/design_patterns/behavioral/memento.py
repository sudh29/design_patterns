"""Memento Design Pattern.

Classification: Behavioral
Intent:
    Without violating encapsulation, capture and externalize an object's internal
    state so that the object can be restored to this state later.

Motivation & Real-World Analogy:
    In financial accounting ledgers or transaction processing systems,
    complex multi-step operations (e.g. transfers, balance updates, tax deductions)
    must support rollbacks if an intermediate step fails or if an auditor requests
    a checkpoint comparison.
    The Memento pattern stores internal state in a strictly immutable token (`Memento`)
    that only the Originator can unpack, preventing external tampering by the Caretaker.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class LedgerMemento {
            <<frozen dataclass>>
            -balance: float
            -transaction_count: int
            -timestamp: float
        }
        class AccountLedger {
            <<originator>>
            -account_id: str
            -balance: float
            -tx_count: int
            +deposit(amount: float)
            +withdraw(amount: float)
            +create_memento() LedgerMemento
            +restore(memento: LedgerMemento)
        }
        class TransactionCaretaker {
            -history: list[LedgerMemento]
            +save_checkpoint(ledger: AccountLedger)
            +rollback(ledger: AccountLedger) bool
        }
        AccountLedger ..> LedgerMemento : creates & restores
        TransactionCaretaker o--> LedgerMemento : stores
    ```
"""

from __future__ import annotations

import time
from dataclasses import dataclass


# ==============================================================================
# 1. Memento: Immutable State Token
# ==============================================================================
@dataclass(frozen=True)
class LedgerMemento:
    """Memento: Frozen snapshot holding internal ledger state at a point in time."""

    balance: float
    transaction_count: int
    timestamp: float


# ==============================================================================
# 2. Originator: Owns State and Produces/Consumes Mementos
# ==============================================================================
class AccountLedger:
    """Originator: Performs business logic and manufactures snapshots of itself."""

    def __init__(self, account_id: str, initial_balance: float = 0.0) -> None:
        self.account_id = account_id
        self._balance = initial_balance
        self._tx_count = 0

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def transaction_count(self) -> int:
        return self._tx_count

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
        self._tx_count += 1

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError(f"Insufficient funds: Balance {self._balance:.2f} < {amount:.2f}")
        self._balance -= amount
        self._tx_count += 1

    def save_to_memento(self) -> LedgerMemento:
        """Creates an immutable memento preserving current internal state."""
        return LedgerMemento(
            balance=self._balance,
            transaction_count=self._tx_count,
            timestamp=time.time(),
        )

    def restore_from_memento(self, memento: LedgerMemento) -> None:
        """Restores internal state from a previously issued memento."""
        self._balance = memento.balance
        self._tx_count = memento.transaction_count


# ==============================================================================
# 3. Caretaker: Manages Memento Lifecycles without Peeking Inside
# ==============================================================================
class TransactionCaretaker:
    """Caretaker: Safely maintains checkpoint history for rollback operations."""

    def __init__(self) -> None:
        self._checkpoints: list[LedgerMemento] = []

    def checkpoint(self, ledger: AccountLedger) -> None:
        self._checkpoints.append(ledger.save_to_memento())

    def rollback(self, ledger: AccountLedger) -> bool:
        if not self._checkpoints:
            return False
        last_memento = self._checkpoints.pop()
        ledger.restore_from_memento(last_memento)
        return True

    def history_depth(self) -> int:
        return len(self._checkpoints)


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    ledger = AccountLedger("ACC-9012", initial_balance=1000.0)
    caretaker = TransactionCaretaker()

    print(f"Initial Balance: ${ledger.balance:.2f}")

    # Checkpoint 1
    caretaker.checkpoint(ledger)

    ledger.deposit(500.0)
    print(f"After Deposit:   ${ledger.balance:.2f} (Tx: {ledger.transaction_count})")

    # Checkpoint 2
    caretaker.checkpoint(ledger)

    ledger.withdraw(200.0)
    print(f"After Withdraw:  ${ledger.balance:.2f} (Tx: {ledger.transaction_count})")

    # Rollback 1
    caretaker.rollback(ledger)
    print(f"After 1st Rollback: ${ledger.balance:.2f} (Tx: {ledger.transaction_count})")

    # Rollback 2
    caretaker.rollback(ledger)
    print(f"After 2nd Rollback: ${ledger.balance:.2f} (Tx: {ledger.transaction_count})")

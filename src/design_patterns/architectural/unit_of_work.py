"""Unit of Work Design Pattern.

Classification: Architectural / Enterprise
Intent:
    Maintains a list of objects affected by a business transaction and coordinates
    the writing out of changes and the resolution of concurrency problems.

Motivation & Real-World Analogy:
    In financial funds transfers or e-commerce checkouts, multiple repositories are
    involved (e.g., `AccountRepository` and `AuditLogRepository`, or `OrderRepository` and `InventoryRepository`).
    If an operation modifies Account A, then attempts to modify Account B but fails,
    leaving Account A debited without Account B credited results in corrupt data.
    The Unit of Work pattern bundles multiple operations into an atomic transaction,
    leveraging Python's `with` context manager protocol (`__enter__` and `__exit__`)
    to guarantee commit or rollback semantics.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class AbstractUnitOfWork {
            <<protocol>>
            +__enter__() Self
            +__exit__(exc_type, exc_val, exc_tb)
            +commit()
            +rollback()
        }
        class SqlAlchemyStyleUnitOfWork {
            -committed: bool
            -rolled_back: bool
            +accounts: AccountRepository
            +audit_logs: list[str]
            +commit()
            +rollback()
        }
        AbstractUnitOfWork <|.. SqlAlchemyStyleUnitOfWork
    ```
"""

from __future__ import annotations

import copy
from typing import Any, Protocol, Self


# ==============================================================================
# 1. Domain Model & Repository
# ==============================================================================
class BankAccount:
    def __init__(self, account_id: str, balance: float) -> None:
        self.account_id = account_id
        self.balance = balance


class AccountRepository:
    def __init__(self, data: dict[str, BankAccount]) -> None:
        self._data = data

    def get(self, account_id: str) -> BankAccount:
        if account_id not in self._data:
            raise KeyError(f"Account {account_id} not found")
        return self._data[account_id]


# ==============================================================================
# 2. Unit of Work Protocol & Implementation
# ==============================================================================
class AbstractUnitOfWork(Protocol):
    """Context manager protocol orchestrating atomic business transactions."""

    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


class FakeUnitOfWork:
    """Atomic Unit of Work with rollback isolation for multi-repository operations."""

    def __init__(self, initial_accounts: dict[str, BankAccount]) -> None:
        self._live_accounts = initial_accounts
        # Working sandbox copy
        self._working_accounts: dict[str, BankAccount] = {}
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> FakeUnitOfWork:
        # Clone current state into sandbox on entering transaction
        self._working_accounts = {
            acc_id: copy.deepcopy(acc) for acc_id, acc in self._live_accounts.items()
        }
        self.accounts = AccountRepository(self._working_accounts)
        self.committed = False
        self.rolled_back = False
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_type is not None:
            # Exception occurred inside with-block -> automatic rollback
            self.rollback()
            return False  # Re-raise exception
        elif not self.committed:
            # User forgot to commit explicitly -> rollback safely
            self.rollback()
        return True

    def commit(self) -> None:
        # Atomic commit: Apply sandbox modifications to live storage
        self._live_accounts.clear()
        self._live_accounts.update(self._working_accounts)
        self.committed = True

    def rollback(self) -> None:
        # Discard sandbox changes
        self._working_accounts.clear()
        self.rolled_back = True


# ==============================================================================
# 3. Transfer Service Coordinating Transaction
# ==============================================================================
def transfer_funds(uow: FakeUnitOfWork, sender_id: str, receiver_id: str, amount: float) -> None:
    if amount <= 0:
        raise ValueError("Transfer amount must be positive")

    with uow:
        sender = uow.accounts.get(sender_id)
        receiver = uow.accounts.get(receiver_id)

        if sender.balance < amount:
            raise ValueError(f"Insufficient funds: {sender.balance} < {amount}")

        sender.balance -= amount
        receiver.balance += amount
        uow.commit()


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    live_db = {
        "ACC-1": BankAccount("ACC-1", 1000.0),
        "ACC-2": BankAccount("ACC-2", 200.0),
    }

    uow = FakeUnitOfWork(live_db)

    print("Initial Balances: ACC-1=$1000, ACC-2=$200")

    # Successful transfer
    transfer_funds(uow, "ACC-1", "ACC-2", 300.0)
    print(f"Post-Transfer: ACC-1=${live_db['ACC-1'].balance}, ACC-2=${live_db['ACC-2'].balance}")

    # Failed transfer (Overdraft)
    try:
        transfer_funds(uow, "ACC-1", "ACC-2", 5000.0)
    except ValueError as e:
        print(f"Transfer blocked: {e}")

    print(
        f"Post-Failure:  ACC-1=${live_db['ACC-1'].balance}, ACC-2=${live_db['ACC-2'].balance} (Unchanged!)"
    )

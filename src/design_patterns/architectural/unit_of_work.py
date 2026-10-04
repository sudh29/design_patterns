"""Unit of Work Design Pattern.

Classification: Architectural / Enterprise
Intent:
    Maintain a list of objects affected by a business transaction and coordinate
    the writing out of changes and the resolution of concurrency problems.
    Guarantees atomic commit or rollback across multiple repositories.

Motivation & Real-World Analogy:
    In complex business workflows—such as transferring funds between bank accounts
    or placing an e-commerce order (which reserves inventory, deducts customer credit,
    and creates a shipping order)—multiple entities across multiple tables or repositories
    are mutated.
    If each repository executes changes immediately and independently, a failure halfway through
    (e.g., deducting funds succeeds but crediting the destination fails) leaves the database
    in an inconsistent, corrupt state.
    The Unit of Work pattern tracks all newly created, modified, and deleted entities within
    a transaction boundary. In Python, it is idiomatically implemented as a context manager:
    if the code block finishes without exceptions, changes are committed atomically;
    if any exception occurs, changes are rolled back completely.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class AbstractUnitOfWork {
            <<abstract>>
            +__enter__() AbstractUnitOfWork
            +__exit__(exc_type, exc_val, exc_tb) bool
            +commit()* void
            +rollback()* void
        }
        class InMemoryUnitOfWork {
            -committed: bool
            -rolled_back: bool
            +accounts: dict
            +ledger: list
            +commit() void
            +rollback() void
        }
        class BankTransferService {
            -uow: InMemoryUnitOfWork
            +transfer(from_id, to_id, amount) void
        }
        AbstractUnitOfWork <|-- InMemoryUnitOfWork
        BankTransferService o--> InMemoryUnitOfWork : manages transaction
    ```
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from types import TracebackType


# ==============================================================================
# 1. Domain Entities
# ==============================================================================
@dataclass
class Account:
    """Bank account domain entity."""

    id: str
    owner: str
    balance: float

    def debit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Debit amount must be positive")
        if self.balance < amount:
            raise ValueError(f"Insufficient funds: available {self.balance}, requested {amount}")
        self.balance -= amount

    def credit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        self.balance += amount


# ==============================================================================
# 2. Abstract Unit of Work Context Manager
# ==============================================================================
class AbstractUnitOfWork(ABC):
    """Abstract Context Manager defining Unit of Work atomic transaction boundaries."""

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if exc_type is not None:
            self.rollback()
            return False  # Propagate exception to caller
        self.commit()
        return True

    @abstractmethod
    def commit(self) -> None:
        """Atomically persist pending changes."""
        ...

    @abstractmethod
    def rollback(self) -> None:
        """Discard uncommitted modifications and restore previous state."""
        ...


# ==============================================================================
# 3. Concrete In-Memory Unit of Work Implementation
# ==============================================================================
class InMemoryUnitOfWork(AbstractUnitOfWork):
    """In-memory Unit of Work supporting snapshot-based rollback semantics."""

    def __init__(self, initial_accounts: dict[str, Account] | None = None) -> None:
        # Canonical datastore
        self._datastore: dict[str, Account] = initial_accounts or {}
        # Working state for current transaction
        self.accounts: dict[str, Account] = {}
        # Audit log of ledger events
        self.ledger: list[str] = []
        self._ledger_snapshot: list[str] = []
        self.committed: bool = False
        self.rolled_back: bool = False

    def __enter__(self) -> InMemoryUnitOfWork:
        # Create an isolated working copy of datastore for this transaction
        self.accounts = deepcopy(self._datastore)
        self._ledger_snapshot = list(self.ledger)
        self.committed = False
        self.rolled_back = False
        return self

    def commit(self) -> None:
        """Apply working copies into canonical datastore."""
        self._datastore = deepcopy(self.accounts)
        self.committed = True

    def rollback(self) -> None:
        """Revert working copies back to last committed datastore state."""
        self.accounts = deepcopy(self._datastore)
        self.ledger = list(self._ledger_snapshot)
        self.rolled_back = True

    def get_account(self, account_id: str) -> Account:
        """Helper to get account from active transaction context."""
        if account_id not in self.accounts:
            raise KeyError(f"Account {account_id} not found")
        return self.accounts[account_id]


# ==============================================================================
# 4. Service / Application Coordinator
# ==============================================================================
class BankTransferService:
    """Coordinates account transfers inside Unit of Work transaction boundaries."""

    def __init__(self, uow: InMemoryUnitOfWork) -> None:
        self.uow = uow

    def transfer(self, from_id: str, to_id: str, amount: float) -> None:
        """Execute funds transfer atomically across accounts."""
        with self.uow:
            from_acc = self.uow.get_account(from_id)
            to_acc = self.uow.get_account(to_id)

            from_acc.debit(amount)
            to_acc.credit(amount)

            self.uow.ledger.append(f"TRANSFERRED ${amount:.2f} from {from_id} to {to_id}")


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    initial_db = {
        "acc_1": Account("acc_1", "Alice", 1000.0),
        "acc_2": Account("acc_2", "Bob", 500.0),
    }

    uow = InMemoryUnitOfWork(initial_db)
    service = BankTransferService(uow)

    # 1. Successful transfer
    service.transfer("acc_1", "acc_2", 200.0)
    print("Post Transfer Alice Balance:", uow._datastore["acc_1"].balance)  # 800
    print("Post Transfer Bob Balance:", uow._datastore["acc_2"].balance)  # 700

    # 2. Failed transfer (insufficient balance -> rollback)
    try:
        service.transfer("acc_1", "acc_2", 5000.0)
    except ValueError as err:
        print("Transfer safely failed & rolled back with error:", err)

    print("After Failed Transfer Alice Balance:", uow._datastore["acc_1"].balance)  # 800 unchanged

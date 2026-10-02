"""Architectural and modern enterprise design patterns."""

from design_patterns.architectural.dependency_injection import (
    ConsoleNotificationService,
    Container,
    InMemoryUserRepository,
    NotificationService,
    Scope,
    UserRepository,
    UserService,
)
from design_patterns.architectural.event_pubsub import (
    DomainEvent,
    EventBus,
    EventHandler,
    PaymentCompletedEvent,
    UserRegisteredEvent,
)
from design_patterns.architectural.registry import (
    DataExporter,
    PluginRegistry,
    exporter_registry,
)
from design_patterns.architectural.repository import (
    InMemoryProductRepository,
    Product,
    Repository,
)
from design_patterns.architectural.specification import (
    AndSpecification,
    CatalogItem,
    CategorySpecification,
    InStockSpecification,
    NotSpecification,
    OrSpecification,
    PriceRangeSpecification,
    Specification,
)
from design_patterns.architectural.unit_of_work import (
    AbstractUnitOfWork,
    AccountRepository,
    BankAccount,
    FakeUnitOfWork,
    transfer_funds,
)

__all__ = [
    "AbstractUnitOfWork",
    "AccountRepository",
    "AndSpecification",
    "BankAccount",
    "CatalogItem",
    "CategorySpecification",
    "ConsoleNotificationService",
    "Container",
    "DataExporter",
    "DomainEvent",
    "EventBus",
    "EventHandler",
    "FakeUnitOfWork",
    "InMemoryProductRepository",
    "InMemoryUserRepository",
    "InStockSpecification",
    "NotSpecification",
    "NotificationService",
    "OrSpecification",
    "PaymentCompletedEvent",
    "PluginRegistry",
    "PriceRangeSpecification",
    "Product",
    "Repository",
    "Scope",
    "Specification",
    "UserRegisteredEvent",
    "UserRepository",
    "UserService",
    "exporter_registry",
    "transfer_funds",
]

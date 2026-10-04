"""Dependency Injection & Service Container Pattern.

Classification: Architectural / Enterprise
Intent:
    Decouple component creation and configuration from component usage.
    An Inversion of Control (IoC) container manages the lifecycle, dependencies,
    and resolution of application services.

Motivation & Real-World Analogy:
    In complex enterprise applications, high-level business services (such as an `OrderCheckoutService`)
    depend on multiple specialized infrastructure services: a `PaymentGateway`, a `TaxCalculator`,
    and an `EmailNotificationService`.
    Hardcoding concrete instantiations inside the `OrderCheckoutService` creates tight coupling,
    prevents mocking during testing, and violates the Dependency Inversion Principle.
    A Dependency Injection (DI) Container manages object creation and dependency resolution,
    supporting distinct lifecycle scopes (such as `SINGLETON` for shared stateless services
    and `TRANSIENT` for stateful or request-scoped instances).

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Scope {
            <<enumeration>>
            SINGLETON
            TRANSIENT
        }
        class Container {
            -registry: dict
            -singletons: dict
            +register(service_type, provider, scope)
            +resolve(service_type) Any
            +register_instance(service_type, instance)
        }
        class PaymentGateway {
            <<protocol>>
            +charge(amount: float) bool
        }
        class TaxCalculator {
            <<protocol>>
            +calculate_tax(amount: float) float
        }
        class NotificationService {
            <<protocol>>
            +send(message: str) None
        }
        class OrderCheckoutService {
            -gateway: PaymentGateway
            -tax_calc: TaxCalculator
            -notifier: NotificationService
            +checkout(amount: float) bool
        }
        Container --> Scope
        OrderCheckoutService o--> PaymentGateway
        OrderCheckoutService o--> TaxCalculator
        OrderCheckoutService o--> NotificationService
        Container ..> OrderCheckoutService : resolves & injects
    ```
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum, auto
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


# ==============================================================================
# 1. Scopes & Service Protocols
# ==============================================================================
class Scope(Enum):
    """Lifecycle scopes for service instances."""

    SINGLETON = auto()
    TRANSIENT = auto()


class PaymentGateway(Protocol):
    """Payment processing protocol."""

    def charge(self, amount: float) -> bool: ...


class TaxCalculator(Protocol):
    """Tax estimation protocol."""

    def calculate_tax(self, amount: float) -> float: ...


class NotificationService(Protocol):
    """Notification messaging protocol."""

    def send(self, recipient: str, message: str) -> None: ...


# ==============================================================================
# 2. Concrete Service Implementations
# ==============================================================================
class StripePaymentGateway:
    """Production payment gateway implementation."""

    def __init__(self, api_key: str = "sk_live_default") -> None:
        self.api_key = api_key
        self.transactions: list[float] = []

    def charge(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Charge amount must be positive")
        self.transactions.append(amount)
        return True


class MockPaymentGateway:
    """Mock payment gateway for test isolation."""

    def __init__(self) -> None:
        self.charges: list[float] = []

    def charge(self, amount: float) -> bool:
        self.charges.append(amount)
        return True


class StandardTaxCalculator:
    """Flat-rate tax calculator."""

    def __init__(self, tax_rate: float = 0.08) -> None:
        self.tax_rate = tax_rate

    def calculate_tax(self, amount: float) -> float:
        return amount * self.tax_rate


class ConsoleNotificationService:
    """Log-based notification dispatcher."""

    def __init__(self) -> None:
        self.sent_messages: list[tuple[str, str]] = []

    def send(self, recipient: str, message: str) -> None:
        self.sent_messages.append((recipient, message))


# ==============================================================================
# 3. High-Level Consumer Service (Dependent)
# ==============================================================================
class OrderCheckoutService:
    """Business coordinator with constructor dependency injection."""

    def __init__(
        self,
        gateway: PaymentGateway,
        tax_calc: TaxCalculator,
        notifier: NotificationService,
    ) -> None:
        self.gateway = gateway
        self.tax_calc = tax_calc
        self.notifier = notifier

    def process_order(self, customer: str, subtotal: float) -> bool:
        tax = self.tax_calc.calculate_tax(subtotal)
        total = subtotal + tax
        success = self.gateway.charge(total)
        if success:
            self.notifier.send(customer, f"Order confirmed! Charged ${total:.2f}")
        return success


# ==============================================================================
# 4. Inversion of Control (IoC) Container
# ==============================================================================
class Container:
    """IoC Service Container managing bindings, resolution, and lifetimes."""

    def __init__(self) -> None:
        self._providers: dict[type[Any], tuple[Callable[[Container], Any], Scope]] = {}
        self._singletons: dict[type[Any], Any] = {}

    def register(
        self,
        service_type: type[T],
        provider: Callable[[Container], T],
        scope: Scope = Scope.SINGLETON,
    ) -> None:
        """Register a service factory with an associated lifecycle scope."""
        self._providers[service_type] = (provider, scope)
        # Clear existing cached singleton if re-registering
        self._singletons.pop(service_type, None)

    def register_instance(self, service_type: type[T], instance: T) -> None:
        """Register a pre-constructed instance as a singleton."""
        self._singletons[service_type] = instance
        self._providers[service_type] = (lambda _: instance, Scope.SINGLETON)

    def resolve(self, service_type: type[T]) -> T:
        """Resolve an instance for the requested service type."""
        if service_type in self._singletons:
            return self._singletons[service_type]  # type: ignore[no-any-return]

        if service_type not in self._providers:
            raise KeyError(f"Service {service_type.__name__} is not registered in container")

        provider, scope = self._providers[service_type]
        instance = provider(self)

        if scope == Scope.SINGLETON:
            self._singletons[service_type] = instance

        return instance  # type: ignore[no-any-return]

    def has(self, service_type: type[Any]) -> bool:
        """Check if a service is registered in the container."""
        return service_type in self._providers or service_type in self._singletons


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    container = Container()

    # Register infrastructure dependencies
    container.register(
        PaymentGateway,
        lambda _: StripePaymentGateway(api_key="sk_prod_xyz"),
        scope=Scope.SINGLETON,
    )
    container.register(
        TaxCalculator,
        lambda _: StandardTaxCalculator(tax_rate=0.075),
        scope=Scope.SINGLETON,
    )
    container.register(
        NotificationService,
        lambda _: ConsoleNotificationService(),
        scope=Scope.TRANSIENT,
    )

    # Register composite service
    container.register(
        OrderCheckoutService,
        lambda c: OrderCheckoutService(
            gateway=c.resolve(PaymentGateway),
            tax_calc=c.resolve(TaxCalculator),
            notifier=c.resolve(NotificationService),
        ),
        scope=Scope.TRANSIENT,
    )

    checkout_service = container.resolve(OrderCheckoutService)
    checkout_service.process_order("alice@example.com", 250.0)
    print("Order checkout completed successfully via DI container!")

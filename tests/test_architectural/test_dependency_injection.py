"""Tests for Dependency Injection and Service Container pattern."""

import pytest

from design_patterns.architectural.dependency_injection import (
    ConsoleNotificationService,
    Container,
    MockPaymentGateway,
    NotificationService,
    OrderCheckoutService,
    PaymentGateway,
    Scope,
    StandardTaxCalculator,
    StripePaymentGateway,
    TaxCalculator,
)


class TestContainerScopesAndResolution:
    def test_singleton_scope_returns_same_instance(self) -> None:
        container = Container()
        container.register(
            TaxCalculator,
            lambda _: StandardTaxCalculator(0.10),
            scope=Scope.SINGLETON,
        )

        calc1 = container.resolve(TaxCalculator)
        calc2 = container.resolve(TaxCalculator)

        assert calc1 is calc2
        assert calc1.calculate_tax(100.0) == pytest.approx(10.0)

    def test_transient_scope_returns_new_instance(self) -> None:
        container = Container()
        container.register(
            NotificationService,
            lambda _: ConsoleNotificationService(),
            scope=Scope.TRANSIENT,
        )

        notifier1 = container.resolve(NotificationService)
        notifier2 = container.resolve(NotificationService)

        assert notifier1 is not notifier2

    def test_register_instance_acts_as_singleton(self) -> None:
        container = Container()
        existing_gateway = MockPaymentGateway()
        container.register_instance(PaymentGateway, existing_gateway)

        resolved = container.resolve(PaymentGateway)
        assert resolved is existing_gateway

    def test_unregistered_service_raises_key_error(self) -> None:
        container = Container()
        with pytest.raises(KeyError, match="is not registered in container"):
            container.resolve(PaymentGateway)

    def test_has_service_check(self) -> None:
        container = Container()
        assert not container.has(PaymentGateway)

        container.register(PaymentGateway, lambda _: MockPaymentGateway())
        assert container.has(PaymentGateway)


class TestOrderCheckoutServiceIntegration:
    def test_order_checkout_flow_with_mocks(self) -> None:
        container = Container()
        mock_gateway = MockPaymentGateway()
        notifier = ConsoleNotificationService()

        container.register_instance(PaymentGateway, mock_gateway)
        container.register(TaxCalculator, lambda _: StandardTaxCalculator(0.10))
        container.register_instance(NotificationService, notifier)

        container.register(
            OrderCheckoutService,
            lambda c: OrderCheckoutService(
                gateway=c.resolve(PaymentGateway),
                tax_calc=c.resolve(TaxCalculator),
                notifier=c.resolve(NotificationService),
            ),
            scope=Scope.TRANSIENT,
        )

        service = container.resolve(OrderCheckoutService)
        success = service.process_order("customer@example.com", 200.0)

        assert success is True
        # Subtotal 200 + 10% tax (20) = 220
        assert mock_gateway.charges == [pytest.approx(220.0)]
        assert len(notifier.sent_messages) == 1
        assert "Order confirmed! Charged $220.00" in notifier.sent_messages[0][1]

    def test_stripe_gateway_validations(self) -> None:
        gateway = StripePaymentGateway(api_key="test_key")
        assert gateway.charge(50.0) is True
        assert gateway.transactions == [50.0]

        with pytest.raises(ValueError, match="Charge amount must be positive"):
            gateway.charge(-10.0)

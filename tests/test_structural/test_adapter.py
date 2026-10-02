"""Tests for the Adapter pattern implementation."""

from design_patterns.structural.adapter import (
    LegacyPayPalSoapClient,
    ModernStripeProcessor,
    PaymentProcessor,
    PaymentRequest,
    PayPalSoapAdapter,
    create_legacy_adapter,
)


class TestModernStripeProcessor:
    def test_successful_payment(self) -> None:
        processor: PaymentProcessor = ModernStripeProcessor()
        req = PaymentRequest("tx12345678", 50.0, "USD", "user@test.com")
        res = processor.process_payment(req)
        assert res.success is True
        assert res.reference_number == "strp_tx123456"

    def test_invalid_amount(self) -> None:
        processor: PaymentProcessor = ModernStripeProcessor()
        req = PaymentRequest("tx000", -10.0, "USD", "user@test.com")
        res = processor.process_payment(req)
        assert res.success is False
        assert res.error_message == "Invalid payment amount"


class TestPayPalSoapAdapter:
    def test_adapter_successful_payment(self) -> None:
        legacy_client = LegacyPayPalSoapClient()
        adapter: PaymentProcessor = PayPalSoapAdapter(legacy_client)

        req = PaymentRequest("pp_tx_888", 99.50, "EUR", "buyer@germany.de")
        res = adapter.process_payment(req)

        assert res.success is True
        assert res.transaction_id == "pp_tx_888"
        assert res.reference_number == "pp_legacy_pp_tx_888"

    def test_adapter_failed_payment(self) -> None:
        legacy_client = LegacyPayPalSoapClient()
        adapter: PaymentProcessor = PayPalSoapAdapter(legacy_client)

        req = PaymentRequest("pp_tx_000", 0.0, "EUR", "buyer@germany.de")
        res = adapter.process_payment(req)

        assert res.success is False
        assert res.error_message == "Negative or zero amount"

    def test_adapter_malformed_xml_fallback(self) -> None:
        class BrokenLegacyClient(LegacyPayPalSoapClient):
            def send_xml_payload(self, xml_payload: str) -> str:
                return "<error>Corrupted</error>"

        adapter = PayPalSoapAdapter(BrokenLegacyClient())
        req = PaymentRequest("tx_fail", 10.0, "USD", "a@b.com")
        res = adapter.process_payment(req)

        assert res.success is False
        assert res.error_message == "Payment failed"

    def test_functional_factory(self) -> None:
        legacy_client = LegacyPayPalSoapClient()
        adapter = create_legacy_adapter(legacy_client)
        req = PaymentRequest("tx_factory", 15.0, "USD", "a@b.com")
        res = adapter.process_payment(req)
        assert res.success is True

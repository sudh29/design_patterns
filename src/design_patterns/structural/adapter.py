"""Adapter Design Pattern.

Classification: Structural
Intent:
    Convert the interface of a class into another interface clients expect.
    Adapter lets classes work together that couldn't otherwise because of
    incompatible interfaces.

Motivation & Real-World Analogy:
    In e-commerce systems, legacy third-party payment gateways often expect
    XML-formatted payloads, specialized authentication keys, and snake_case or
    custom method signatures (e.g., `execute_transaction_v1(xml_data)`).
    Modern internal checkout services expect a clean `PaymentProcessor` interface
    accepting standard typed domain models (`PaymentRequest` -> `PaymentResponse`).
    The Adapter reconciles this impedance mismatch without touching the third-party SDK.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class PaymentProcessor {
            <<protocol>>
            +process_payment(request: PaymentRequest) PaymentResponse
        }
        class ModernStripeProcessor {
            +process_payment(request: PaymentRequest) PaymentResponse
        }
        class LegacyPayPalSoapClient {
            +send_xml_payload(xml_content: str) str
        }
        class PayPalSoapAdapter {
            -soap_client: LegacyPayPalSoapClient
            +process_payment(request: PaymentRequest) PaymentResponse
        }
        PaymentProcessor <|.. ModernStripeProcessor
        PaymentProcessor <|.. PayPalSoapAdapter
        PayPalSoapAdapter o--> LegacyPayPalSoapClient : wraps
    ```
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol


# ==============================================================================
# Domain Models & Target Interface
# ==============================================================================
@dataclass(frozen=True)
class PaymentRequest:
    transaction_id: str
    amount: float
    currency: str
    customer_email: str


@dataclass(frozen=True)
class PaymentResponse:
    success: bool
    transaction_id: str
    reference_number: str
    error_message: str | None = None


class PaymentProcessor(Protocol):
    """Target Interface expected by modern checkout clients."""

    def process_payment(self, request: PaymentRequest) -> PaymentResponse: ...


# ==============================================================================
# 1. Concrete Modern Implementation
# ==============================================================================
class ModernStripeProcessor:
    """Native implementation conforming directly to target interface."""

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        if request.amount <= 0:
            return PaymentResponse(
                success=False,
                transaction_id=request.transaction_id,
                reference_number="",
                error_message="Invalid payment amount",
            )
        return PaymentResponse(
            success=True,
            transaction_id=request.transaction_id,
            reference_number=f"strp_{request.transaction_id[:8]}",
        )


# ==============================================================================
# 2. Adaptee: Legacy Incompatible Third-Party System
# ==============================================================================
class LegacyPayPalSoapClient:
    """Adaptee: Incompatible interface communicating in raw XML strings."""

    def send_xml_payload(self, xml_payload: str) -> str:
        # Simulates legacy XML SOAP parsing
        match_amount = re.search(r"<amount>(.*?)</amount>", xml_payload)
        match_tx = re.search(r"<tx_id>(.*?)</tx_id>", xml_payload)

        if not match_amount or not match_tx:
            return "<soap:Fault><error>Malformed XML Request</error></soap:Fault>"

        amount = float(match_amount.group(1))
        tx_id = match_tx.group(1)

        if amount <= 0:
            return f"<response><status>FAILED</status><tx>{tx_id}</tx><reason>Negative or zero amount</reason></response>"

        return f"<response><status>SUCCESS</status><tx>{tx_id}</tx><ref>pp_legacy_{tx_id}</ref></response>"


# ==============================================================================
# 3. Clean GoF Adapter (Object Adapter Pattern using Composition)
# ==============================================================================
class PayPalSoapAdapter:
    """Object Adapter: Wraps LegacyPayPalSoapClient to satisfy PaymentProcessor."""

    def __init__(self, soap_client: LegacyPayPalSoapClient) -> None:
        self._soap_client = soap_client

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        # 1. Translate modern domain model into legacy XML schema
        xml_payload = (
            f"<soap:Envelope>"
            f"<tx_id>{request.transaction_id}</tx_id>"
            f"<amount>{request.amount:.2f}</amount>"
            f"<currency>{request.currency}</currency>"
            f"<email>{request.customer_email}</email>"
            f"</soap:Envelope>"
        )

        # 2. Delegate to the adaptee
        xml_response = self._soap_client.send_xml_payload(xml_payload)

        # 3. Translate legacy XML response back into modern domain model
        if "<status>SUCCESS</status>" in xml_response:
            ref_match = re.search(r"<ref>(.*?)</ref>", xml_response)
            ref_num = ref_match.group(1) if ref_match else ""
            return PaymentResponse(
                success=True,
                transaction_id=request.transaction_id,
                reference_number=ref_num,
            )

        err_match = re.search(r"<reason>(.*?)</reason>", xml_response)
        error_msg = err_match.group(1) if err_match else "Payment failed"
        return PaymentResponse(
            success=False,
            transaction_id=request.transaction_id,
            reference_number="",
            error_message=error_msg,
        )


# ==============================================================================
# 4. Pythonic Twist: Function Adapter / Callable Wrapper
# ==============================================================================
def create_legacy_adapter(client: LegacyPayPalSoapClient) -> PaymentProcessor:
    """In Python, adapters can be simple lightweight wrapper closures or classes."""
    return PayPalSoapAdapter(client)


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    req = PaymentRequest(
        transaction_id="txn_991823",
        amount=149.99,
        currency="USD",
        customer_email="buyer@example.com",
    )

    processors: list[tuple[str, PaymentProcessor]] = [
        ("Modern Stripe", ModernStripeProcessor()),
        ("Legacy PayPal (Adapted)", PayPalSoapAdapter(LegacyPayPalSoapClient())),
    ]

    for name, proc in processors:
        resp = proc.process_payment(req)
        print(f"[{name}] Success={resp.success}, Ref={resp.reference_number}")

"""Bridge Design Pattern.

Classification: Structural
Intent:
    Decouple an abstraction from its implementation so that the two can vary independently.

Motivation & Real-World Analogy:
    Consider an Alert Notification system where you have multiple types of alerts
    (`SystemAlert`, `UrgentAlert`, `DigestAlert`) and multiple delivery channels
    (`EmailChannel`, `SMSChannel`, `WebhookChannel`).
    Without the Bridge pattern, you face a Cartesian class explosion:
    `UrgentEmailAlert`, `UrgentSMSAlert`, `DigestEmailAlert`, `DigestSMSAlert`, etc.
    The Bridge pattern splits the problem into two orthogonal dimensions:
    1. **Abstraction**: The alert domain logic and severity formatting.
    2. **Implementor**: The concrete delivery channel.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class MessageSender {
            <<protocol>>
            +send_raw(recipient: str, payload: str) bool
        }
        class EmailSender {
            +send_raw(recipient: str, payload: str) bool
        }
        class SMSSender {
            +send_raw(recipient: str, payload: str) bool
        }
        class WebhookSender {
            +send_raw(recipient: str, payload: str) bool
        }
        class AlertNotification {
            #sender: MessageSender
            +notify(recipient: str, subject: str, message: str) bool
        }
        class UrgentAlertNotification {
            +notify(recipient: str, subject: str, message: str) bool
        }
        class DigestAlertNotification {
            -items: list
            +add_item(item: str)
            +flush(recipient: str) bool
        }
        MessageSender <|.. EmailSender
        MessageSender <|.. SMSSender
        MessageSender <|.. WebhookSender
        AlertNotification o--> MessageSender : bridge
        AlertNotification <|-- UrgentAlertNotification
        AlertNotification <|-- DigestAlertNotification
    ```
"""

from __future__ import annotations

from typing import Protocol


# ==============================================================================
# 1. Implementor Dimension: Communication Channels
# ==============================================================================
class MessageSender(Protocol):
    """Implementor Interface: Dictates raw delivery without caring about alert types."""

    def send_raw(self, recipient: str, payload: str) -> bool: ...


class EmailSender:
    """Concrete Implementor A: Delivers via SMTP/Email."""

    def send_raw(self, recipient: str, payload: str) -> bool:
        print(f"[EMAIL SENDER] To: {recipient} | Payload:\n{payload}")
        return True


class SMSSender:
    """Concrete Implementor B: Delivers via SMS Gateway."""

    def send_raw(self, recipient: str, payload: str) -> bool:
        print(f"[SMS SENDER] Phone: {recipient} | Text: {payload}")
        return True


class WebhookSender:
    """Concrete Implementor C: Delivers via HTTP Webhook POST."""

    def send_raw(self, recipient: str, payload: str) -> bool:
        print(f"[WEBHOOK SENDER] Endpoint: {recipient} | JSON: {payload}")
        return True


# ==============================================================================
# 2. Abstraction Dimension: Alert Business Logic
# ==============================================================================
class AlertNotification:
    """Base Abstraction: Holds a reference to the Implementor."""

    def __init__(self, sender: MessageSender) -> None:
        self._sender = sender

    def notify(self, recipient: str, title: str, content: str) -> bool:
        formatted = f"[{title.upper()}]\n{content}"
        return self._sender.send_raw(recipient, formatted)


class UrgentAlertNotification(AlertNotification):
    """Refined Abstraction: Escalates urgency with high-priority banners."""

    def notify(self, recipient: str, title: str, content: str) -> bool:
        critical_payload = (
            f"🚨 CRITICAL ALERT: {title} 🚨\n"
            f"TIMESTAMP: IMMEDIATELY REQUIRED ACTION\n"
            f"DETAILS: {content}"
        )
        return self._sender.send_raw(recipient, critical_payload)


class DigestAlertNotification(AlertNotification):
    """Refined Abstraction: Buffers events and dispatches batch digests."""

    def __init__(self, sender: MessageSender) -> None:
        super().__init__(sender)
        self._buffer: list[str] = []

    def add_entry(self, entry: str) -> None:
        self._buffer.append(entry)

    def dispatch_digest(self, recipient: str) -> bool:
        if not self._buffer:
            return False
        digest_content = "=== PERIODIC DIGEST SUMMARY ===\n" + "\n".join(
            f"- {item}" for item in self._buffer
        )
        success = self._sender.send_raw(recipient, digest_content)
        if success:
            self._buffer.clear()
        return success


# ==============================================================================
# 3. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    email_sender = EmailSender()
    sms_sender = SMSSender()

    # Mix and match orthogonal dimensions easily:
    standard_email = AlertNotification(email_sender)
    standard_email.notify("user@corp.com", "Maintenance", "Servers rebooting at midnight.")

    urgent_sms = UrgentAlertNotification(sms_sender)
    urgent_sms.notify("+10029384", "DB Outage", "Primary cluster unreachable.")

    digest_email = DigestAlertNotification(email_sender)
    digest_email.add_entry("User logged in from new IP")
    digest_email.add_entry("Disk utilization exceeded 85%")
    digest_email.dispatch_digest("security@corp.com")

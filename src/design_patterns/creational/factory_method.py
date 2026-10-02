"""Factory Method Design Pattern.

Classification: Creational
Intent:
    Define an interface for creating an object, but let subclasses decide
    which class to instantiate. Factory Method lets a class defer
    instantiation to subclasses.

Motivation & Real-World Analogy:
    In a multi-channel notification dispatch system (Email, SMS, Slack, Push),
    client services need to send notifications without coupling to the specific
    vendor SDKs, authentication protocols, or message formats.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Notification {
            <<protocol>>
            +send(recipient: str, message: str) bool
        }
        class EmailNotification {
            +send(recipient: str, message: str) bool
        }
        class SMSNotification {
            +send(recipient: str, message: str) bool
        }
        class SlackNotification {
            +send(recipient: str, message: str) bool
        }
        class NotificationCreator {
            <<abstract>>
            +create_notification() Notification*
            +dispatch(recipient: str, message: str) bool
        }
        class EmailCreator {
            +create_notification() Notification
        }
        class SMSCreator {
            +create_notification() Notification
        }
        class SlackCreator {
            +create_notification() Notification
        }
        Notification <|.. EmailNotification
        Notification <|.. SMSNotification
        Notification <|.. SlackNotification
        NotificationCreator <|-- EmailCreator
        NotificationCreator <|-- SMSCreator
        NotificationCreator <|-- SlackCreator
        NotificationCreator ..> Notification : creates
    ```
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar, Protocol


# ==============================================================================
# 1. Anti-Pattern / Naive Approach (Tight Coupling & OCP Violation)
# ==============================================================================
class NaiveNotificationService:
    """Anti-pattern: Monolithic dispatcher with hardcoded conditionals.

    Adding a new notification channel requires modifying this class, directly
    violating the Open/Closed Principle (OCP).
    """

    def send(self, channel: str, recipient: str, message: str) -> bool:
        if channel == "email":
            # Direct instantiation & business logic tightly coupled
            print(f"[NAIVE EMAIL] To: {recipient} | Body: {message}")
            return True
        elif channel == "sms":
            if not recipient.startswith("+"):
                raise ValueError("Invalid phone number format")
            print(f"[NAIVE SMS] To: {recipient} | Body: {message}")
            return True
        elif channel == "slack":
            if not recipient.startswith("#") and not recipient.startswith("@"):
                raise ValueError("Invalid Slack target")
            print(f"[NAIVE SLACK] Channel: {recipient} | Text: {message}")
            return True
        else:
            raise ValueError(f"Unsupported notification channel: {channel}")


# ==============================================================================
# 2. Clean Pattern Implementation (GoF Factory Method with Modern Types)
# ==============================================================================
class Notification(Protocol):
    """Product Interface: Defines the contract that all concrete notifications must fulfill."""

    def send(self, recipient: str, message: str) -> bool: ...


@dataclass(frozen=True)
class EmailNotification:
    """Concrete Product: Email channel implementation."""

    sender_email: str = "noreply@company.com"

    def send(self, recipient: str, message: str) -> bool:
        if "@" not in recipient:
            raise ValueError(f"Invalid email recipient: {recipient}")
        print(f"[EMAIL] From: {self.sender_email} -> To: {recipient} | Content: {message}")
        return True


@dataclass(frozen=True)
class SMSNotification:
    """Concrete Product: SMS channel implementation."""

    sender_id: str = "COMPNOTIF"

    def send(self, recipient: str, message: str) -> bool:
        if not recipient.startswith("+"):
            raise ValueError(f"SMS recipient must include country code: {recipient}")
        print(f"[SMS] Sender: {self.sender_id} -> To: {recipient} | Text: {message}")
        return True


@dataclass(frozen=True)
class SlackNotification:
    """Concrete Product: Slack workspace channel implementation."""

    webhook_url: str = "https://hooks.slack.com/services/T00/B00/X00"

    def send(self, recipient: str, message: str) -> bool:
        if not (recipient.startswith("#") or recipient.startswith("@")):
            raise ValueError(f"Slack recipient must start with '#' or '@': {recipient}")
        print(f"[SLACK] Target: {recipient} via {self.webhook_url} | Msg: {message}")
        return True


class NotificationCreator(ABC):
    """Creator: Declares the factory method that returns a Product object."""

    @abstractmethod
    def create_notification(self) -> Notification:
        """Factory Method: Subclasses must override to supply their concrete Product."""
        ...

    def dispatch(self, recipient: str, message: str) -> bool:
        """Core business logic that relies on the Product interface, not concrete classes."""
        notification = self.create_notification()
        # Logging / Auditing / Pre-processing hook
        print(f"[AUDIT] Dispatching notification to '{recipient}'")
        return notification.send(recipient=recipient, message=message)


class EmailCreator(NotificationCreator):
    """Concrete Creator for Email notifications."""

    def __init__(self, sender_email: str = "system@enterprise.io") -> None:
        self.sender_email = sender_email

    def create_notification(self) -> Notification:
        return EmailNotification(sender_email=self.sender_email)


class SMSCreator(NotificationCreator):
    """Concrete Creator for SMS notifications."""

    def __init__(self, sender_id: str = "ENTALERT") -> None:
        self.sender_id = sender_id

    def create_notification(self) -> Notification:
        return SMSNotification(sender_id=self.sender_id)


class SlackCreator(NotificationCreator):
    """Concrete Creator for Slack notifications."""

    def __init__(self, webhook_url: str = "https://hooks.slack.com/default") -> None:
        self.webhook_url = webhook_url

    def create_notification(self) -> Notification:
        return SlackNotification(webhook_url=self.webhook_url)


# ==============================================================================
# 3. Pythonic Twist: Registry-Based Parameterized Factory
# ==============================================================================
class NotificationRegistry:
    """Pythonic alternative: Dynamic registry using first-class class references or callables.

    Eliminates subclass proliferation by allowing registration of factory functions/classes.
    """

    _registry: ClassVar[dict[str, Callable[[], Notification]]] = {}

    @classmethod
    def register(
        cls, channel: str
    ) -> Callable[[Callable[[], Notification]], Callable[[], Notification]]:
        """Decorator to register a factory function for a channel."""

        def decorator(factory: Callable[[], Notification]) -> Callable[[], Notification]:
            cls._registry[channel.lower()] = factory
            return factory

        return decorator

    @classmethod
    def create(cls, channel: str) -> Notification:
        """Creates a Notification instance based on the registered channel name."""
        factory = cls._registry.get(channel.lower())
        if not factory:
            supported = ", ".join(cls._registry.keys()) or "none"
            raise ValueError(f"Unknown channel '{channel}'. Supported channels: {supported}")
        return factory()


# Register default channels with registry
NotificationRegistry.register("email")(lambda: EmailNotification())
NotificationRegistry.register("sms")(lambda: SMSNotification())
NotificationRegistry.register("slack")(lambda: SlackNotification())


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    print("=== Traditional GoF Factory Method ===")
    creators: list[NotificationCreator] = [
        EmailCreator("support@acme.corp"),
        SMSCreator("ACME_AUTH"),
        SlackCreator("https://hooks.slack.com/acme-alerts"),
    ]

    destinations = [
        ("alice@acme.corp", "Your report is ready."),
        ("+1234567890", "Your OTP is 948201."),
        ("#devops-alerts", "Deployment to production successful."),
    ]

    for creator, (target, msg) in zip(creators, destinations, strict=True):
        creator.dispatch(recipient=target, message=msg)

    print("\n=== Pythonic Registry-Based Factory ===")
    email_notifier = NotificationRegistry.create("email")
    email_notifier.send("bob@example.com", "Welcome onboard!")

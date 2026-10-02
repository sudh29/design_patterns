"""Tests for the Bridge pattern implementation."""

from design_patterns.structural.bridge import (
    AlertNotification,
    DigestAlertNotification,
    EmailSender,
    SMSSender,
    UrgentAlertNotification,
    WebhookSender,
)


class MockSender:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def send_raw(self, recipient: str, payload: str) -> bool:
        self.messages.append((recipient, payload))
        return True


class TestBridgePattern:
    def test_standard_alert_with_email_and_sms(self) -> None:
        mock = MockSender()
        alert = AlertNotification(mock)
        assert alert.notify("ops@team.com", "Backup", "All snapshots saved") is True
        assert len(mock.messages) == 1
        recip, payload = mock.messages[0]
        assert recip == "ops@team.com"
        assert "[BACKUP]" in payload

    def test_urgent_alert_formatting(self) -> None:
        mock = MockSender()
        urgent = UrgentAlertNotification(mock)
        urgent.notify("+1888291", "Security Breach", "Unauthorized access")

        assert len(mock.messages) == 1
        _, payload = mock.messages[0]
        assert "🚨 CRITICAL ALERT: Security Breach 🚨" in payload
        assert "DETAILS: Unauthorized access" in payload

    def test_digest_alert_empty_and_flush(self) -> None:
        mock = MockSender()
        digest = DigestAlertNotification(mock)

        # Empty dispatch returns False
        assert digest.dispatch_digest("team@corp.com") is False
        assert len(mock.messages) == 0

        # After adding entries
        digest.add_entry("Task 1 completed")
        digest.add_entry("Task 2 failed")
        assert digest.dispatch_digest("team@corp.com") is True
        assert len(mock.messages) == 1
        _, payload = mock.messages[0]
        assert "=== PERIODIC DIGEST SUMMARY ===" in payload
        assert "- Task 1 completed" in payload
        assert "- Task 2 failed" in payload

        # Buffer should now be cleared
        assert digest.dispatch_digest("team@corp.com") is False

    def test_concrete_senders(self) -> None:
        email = EmailSender()
        sms = SMSSender()
        webhook = WebhookSender()

        assert email.send_raw("a@b.com", "test") is True
        assert sms.send_raw("+111", "test") is True
        assert webhook.send_raw("https://hook.url", "{}") is True

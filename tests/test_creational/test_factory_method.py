"""Tests for the Factory Method pattern implementation."""

import pytest

from design_patterns.creational.factory_method import (
    EmailCreator,
    EmailNotification,
    NaiveNotificationService,
    NotificationCreator,
    NotificationRegistry,
    SlackCreator,
    SlackNotification,
    SMSCreator,
    SMSNotification,
)


class TestNaiveNotificationService:
    def test_naive_email_success(self) -> None:
        service = NaiveNotificationService()
        assert service.send("email", "user@test.com", "Hello") is True

    def test_naive_sms_invalid(self) -> None:
        service = NaiveNotificationService()
        with pytest.raises(ValueError, match="Invalid phone number format"):
            service.send("sms", "12345", "Invalid number")

    def test_naive_slack_invalid(self) -> None:
        service = NaiveNotificationService()
        with pytest.raises(ValueError, match="Invalid Slack target"):
            service.send("slack", "general", "Invalid channel prefix")

    def test_naive_unsupported_channel(self) -> None:
        service = NaiveNotificationService()
        with pytest.raises(ValueError, match="Unsupported notification channel"):
            service.send("discord", "user", "Hello")


class TestGoFFactoryMethod:
    def test_email_creator_dispatch(self) -> None:
        creator = EmailCreator(sender_email="admin@test.com")
        assert creator.dispatch("user@domain.com", "Test msg") is True

    def test_email_validation_error(self) -> None:
        creator = EmailCreator()
        with pytest.raises(ValueError, match="Invalid email recipient"):
            creator.dispatch("invalid-email", "Test msg")

    def test_sms_creator_dispatch(self) -> None:
        creator = SMSCreator(sender_id="AUTH")
        assert creator.dispatch("+1999888777", "Your code is 1234") is True

    def test_sms_validation_error(self) -> None:
        creator = SMSCreator()
        with pytest.raises(ValueError, match="SMS recipient must include country code"):
            creator.dispatch("999888777", "Test msg")

    def test_slack_creator_dispatch(self) -> None:
        creator = SlackCreator()
        assert creator.dispatch("#general", "Standup at 10AM") is True
        assert creator.dispatch("@alice", "Direct message") is True

    def test_slack_validation_error(self) -> None:
        creator = SlackCreator()
        with pytest.raises(ValueError, match="Slack recipient must start with"):
            creator.dispatch("general", "Test msg")

    def test_custom_creator_extension(self) -> None:
        """Verifies Open/Closed Principle: Can add new notifications without altering core code."""

        class DiscordNotification:
            def send(self, recipient: str, message: str) -> bool:
                return True

        class DiscordCreator(NotificationCreator):
            def create_notification(self) -> DiscordNotification:
                return DiscordNotification()

        creator = DiscordCreator()
        assert creator.dispatch("devs", "Hello Discord") is True


class TestNotificationRegistry:
    def test_registry_create_email(self) -> None:
        notification = NotificationRegistry.create("email")
        assert isinstance(notification, EmailNotification)
        assert notification.send("user@test.com", "Hi") is True

    def test_registry_create_sms(self) -> None:
        notification = NotificationRegistry.create("sms")
        assert isinstance(notification, SMSNotification)

    def test_registry_create_slack(self) -> None:
        notification = NotificationRegistry.create("slack")
        assert isinstance(notification, SlackNotification)

    def test_registry_unknown_channel(self) -> None:
        with pytest.raises(ValueError, match="Unknown channel 'pager'"):
            NotificationRegistry.create("pager")

    def test_custom_decorator_registration(self) -> None:
        class InAppNotification:
            def send(self, recipient: str, message: str) -> bool:
                return True

        @NotificationRegistry.register("in_app")
        def create_in_app() -> InAppNotification:
            return InAppNotification()

        in_app = NotificationRegistry.create("in_app")
        assert in_app.send("user1", "Hello in app") is True

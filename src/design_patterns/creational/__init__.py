"""Creational design patterns."""

from design_patterns.creational.abstract_factory import (
    AWSCloudFactory,
    CloudInfrastructureDeployer,
    CloudResourceFactory,
    GCPCloudFactory,
)
from design_patterns.creational.builder import (
    ConcreteHttpRequestBuilder,
    HttpRequest,
    HttpRequestBuilder,
    RequestDirector,
)
from design_patterns.creational.factory_method import (
    EmailCreator,
    Notification,
    NotificationCreator,
    NotificationRegistry,
    SlackCreator,
    SMSCreator,
)
from design_patterns.creational.prototype import (
    InvoiceTemplate,
    Prototype,
    PrototypeRegistry,
)
from design_patterns.creational.singleton import (
    AppSettings,
    BorgMonostate,
    DatabaseConnectionPool,
    SingletonMeta,
)

__all__ = [
    "AWSCloudFactory",
    "AppSettings",
    "BorgMonostate",
    "CloudInfrastructureDeployer",
    "CloudResourceFactory",
    "ConcreteHttpRequestBuilder",
    "DatabaseConnectionPool",
    "EmailCreator",
    "GCPCloudFactory",
    "HttpRequest",
    "HttpRequestBuilder",
    "InvoiceTemplate",
    "Notification",
    "NotificationCreator",
    "NotificationRegistry",
    "Prototype",
    "PrototypeRegistry",
    "RequestDirector",
    "SMSCreator",
    "SingletonMeta",
    "SlackCreator",
]

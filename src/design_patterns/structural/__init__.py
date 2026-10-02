"""Structural design patterns."""

from design_patterns.structural.adapter import (
    LegacyPayPalSoapClient,
    ModernStripeProcessor,
    PaymentProcessor,
    PaymentRequest,
    PaymentResponse,
    PayPalSoapAdapter,
    create_legacy_adapter,
)
from design_patterns.structural.bridge import (
    AlertNotification,
    DigestAlertNotification,
    EmailSender,
    MessageSender,
    SMSSender,
    UrgentAlertNotification,
    WebhookSender,
)
from design_patterns.structural.composite import (
    Directory,
    File,
    FileSystemItem,
)
from design_patterns.structural.decorator import (
    CachingDecorator,
    DataService,
    LoggingDecorator,
    RemoteDatabaseService,
    rate_limit,
)
from design_patterns.structural.facade import (
    AudioMixer,
    BitrateCompressor,
    ContainerMuxer,
    VideoConverterFacade,
    VideoDecoder,
)
from design_patterns.structural.flyweight import (
    Forest,
    Tree,
    TreeFactory,
    TreeType,
)
from design_patterns.structural.proxy import (
    Document,
    HeavyDocument,
    LazyDocumentProxy,
    ProtectedDocumentProxy,
)

__all__ = [
    "AlertNotification",
    "AudioMixer",
    "BitrateCompressor",
    "CachingDecorator",
    "ContainerMuxer",
    "DataService",
    "DigestAlertNotification",
    "Directory",
    "Document",
    "EmailSender",
    "File",
    "FileSystemItem",
    "Forest",
    "HeavyDocument",
    "LazyDocumentProxy",
    "LegacyPayPalSoapClient",
    "LoggingDecorator",
    "MessageSender",
    "ModernStripeProcessor",
    "PayPalSoapAdapter",
    "PaymentProcessor",
    "PaymentRequest",
    "PaymentResponse",
    "ProtectedDocumentProxy",
    "RemoteDatabaseService",
    "SMSSender",
    "Tree",
    "TreeFactory",
    "TreeType",
    "UrgentAlertNotification",
    "VideoConverterFacade",
    "VideoDecoder",
    "WebhookSender",
    "create_legacy_adapter",
    "rate_limit",
]

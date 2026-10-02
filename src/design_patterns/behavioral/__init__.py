"""Behavioral design patterns."""

from design_patterns.behavioral.chain_of_responsibility import (
    AuthenticationMiddleware,
    BaseMiddleware,
    HttpRequestContext,
    MiddlewarePipeline,
    RateLimitMiddleware,
    SchemaValidationMiddleware,
)
from design_patterns.behavioral.command import (
    Command,
    DeleteTextCommand,
    EditorInvoker,
    InsertTextCommand,
    TextDocument,
)
from design_patterns.behavioral.iterator import (
    BinarySearchTree,
    BSTInOrderIterator,
    CustomIterator,
    TreeNode,
)
from design_patterns.behavioral.mediator import (
    Airplane,
    AirTrafficControl,
    CommercialAirliner,
    ControlTower,
)
from design_patterns.behavioral.memento import (
    AccountLedger,
    LedgerMemento,
    TransactionCaretaker,
)
from design_patterns.behavioral.observer import (
    AlgorithmicTradingBot,
    AuditLogger,
    StockSubscriber,
    StockTicker,
)
from design_patterns.behavioral.state import (
    CancelledState,
    DraftState,
    Order,
    OrderState,
    PaidState,
    ShippedState,
)
from design_patterns.behavioral.strategy import (
    CheckoutCart,
    DiscountStrategy,
    FlatDiscount,
    PercentageDiscount,
    PricingFunction,
    TieredVolumeDiscount,
    apply_vip_club_discount,
)
from design_patterns.behavioral.template_method import (
    APIDataPipeline,
    CSVDataPipeline,
    DataPipelineETL,
)
from design_patterns.behavioral.visitor import (
    AssetElement,
    AssetVisitor,
    CapitalGainsTaxVisitor,
    CryptoHolding,
    LiquidityAssessmentVisitor,
    RealEstateHolding,
    StockHolding,
    estimate_asset_insurance,
)

__all__ = [
    "APIDataPipeline",
    "AccountLedger",
    "Airplane",
    "AirTrafficControl",
    "AlgorithmicTradingBot",
    "AssetElement",
    "AssetVisitor",
    "AuditLogger",
    "AuthenticationMiddleware",
    "BSTInOrderIterator",
    "BaseMiddleware",
    "BinarySearchTree",
    "CSVDataPipeline",
    "CancelledState",
    "CapitalGainsTaxVisitor",
    "CheckoutCart",
    "Command",
    "CommercialAirliner",
    "ControlTower",
    "CryptoHolding",
    "CustomIterator",
    "DataPipelineETL",
    "DeleteTextCommand",
    "DiscountStrategy",
    "DraftState",
    "EditorInvoker",
    "FlatDiscount",
    "HttpRequestContext",
    "InsertTextCommand",
    "LedgerMemento",
    "LiquidityAssessmentVisitor",
    "MiddlewarePipeline",
    "Order",
    "OrderState",
    "PaidState",
    "PercentageDiscount",
    "PricingFunction",
    "RateLimitMiddleware",
    "RealEstateHolding",
    "SchemaValidationMiddleware",
    "ShippedState",
    "StockHolding",
    "StockSubscriber",
    "StockTicker",
    "TieredVolumeDiscount",
    "TextDocument",
    "TransactionCaretaker",
    "TreeNode",
    "apply_vip_club_discount",
    "estimate_asset_insurance",
]

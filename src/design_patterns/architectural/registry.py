"""Registry Design Pattern.

Classification: Architectural / Extensible Plugin Architecture
Intent:
    Provide a well-known central registry where components, plugins, or strategies
    can register themselves dynamically without modifying core application code.

Motivation & Real-World Analogy:
    In CLI frameworks, serialization engines (e.g. JSON, YAML, Protocol Buffers),
    or payment processor integrations, third-party developers need to add new
    functionality without modifying core codebase files.
    The Registry pattern offers a decorator-based dynamic registration mechanism
    (`@PluginRegistry.register("name")`), allowing the system to discover and
    instantiate plugins at runtime based on string identifiers or configuration files.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Plugin {
            <<protocol>>
            +execute(data: str) str
        }
        class PluginRegistry {
            -_registry: dict[str, type]
            +register(name: str) Callable
            +get(name: str) type
            +create(name: str, *args, **kwargs) Plugin
            +list_available() list[str]
        }
        class JsonExporter {
            +execute(data: str) str
        }
        class YamlExporter {
            +execute(data: str) str
        }
        Plugin <|.. JsonExporter
        Plugin <|.. YamlExporter
        PluginRegistry o--> Plugin : registers & creates
    ```
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


# ==============================================================================
# 1. Plugin Contract (Protocol)
# ==============================================================================
class DataExporter(Protocol):
    """Protocol that all registered export plugins must satisfy."""

    def export(self, data: dict[str, Any]) -> str: ...


# ==============================================================================
# 2. Registry Implementation
# ==============================================================================
class PluginRegistry:
    """Centralized typed registry for discovering and instantiating plugins."""

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self._registry: dict[str, type[Any]] = {}

    def register(self, identifier: str) -> Callable[[type[T]], type[T]]:
        """Decorator to register a plugin class under an identifier."""

        def decorator(cls: type[T]) -> type[T]:
            key = identifier.lower()
            if key in self._registry:
                raise KeyError(f"Plugin '{identifier}' is already registered in '{self.name}'.")
            self._registry[key] = cls
            return cls

        return decorator

    def get_class(self, identifier: str) -> type[Any]:
        key = identifier.lower()
        if key not in self._registry:
            available = ", ".join(self._registry.keys()) or "none"
            raise KeyError(
                f"Unknown plugin '{identifier}' in '{self.name}'. Available: {available}"
            )
        return self._registry[key]

    def create(self, identifier: str, *args: Any, **kwargs: Any) -> Any:
        cls = self.get_class(identifier)
        return cls(*args, **kwargs)

    def list_plugins(self) -> list[str]:
        return sorted(self._registry.keys())


# Global Exporters Registry
exporter_registry = PluginRegistry("exporters")


# ==============================================================================
# 3. Built-in Plugins using Registry Decorator
# ==============================================================================
@exporter_registry.register("json")
class JsonExporter:
    def export(self, data: dict[str, Any]) -> str:
        import json

        return json.dumps(data)


@exporter_registry.register("csv")
class CsvExporter:
    def export(self, data: dict[str, Any]) -> str:
        headers = ",".join(data.keys())
        values = ",".join(str(v) for v in data.values())
        return f"{headers}\n{values}"


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    print(f"Available Exporters: {exporter_registry.list_plugins()}")

    # Dynamically select exporter based on config or runtime input
    json_plugin: DataExporter = exporter_registry.create("json")
    print(json_plugin.export({"status": "active", "code": 200}))

    csv_plugin: DataExporter = exporter_registry.create("csv")
    print(csv_plugin.export({"status": "active", "code": 200}))

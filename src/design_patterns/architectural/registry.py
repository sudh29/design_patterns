"""Registry Design Pattern (Plugin Architecture).

Classification: Architectural / Enterprise
Intent:
    Provide a well-known central directory or registry where components, plugins,
    or strategies can be registered dynamically (often via decorators) and looked up
    by name or category without hardcoded dependencies.

Motivation & Real-World Analogy:
    In extensible systems (such as web frameworks, document export engines, or machine learning pipelines),
    applications must support pluggable extensions: exporting a document as `PDF`, `HTML`, `Markdown`,
    or `JSON`.
    If the document exporter uses a massive `if-elif-else` statement checking format strings, adding a new
    format requires modifying core framework code.
    The Registry pattern decouples plugin authors from the core dispatcher. Authors write a self-contained
    class or function, tag it with `@registry.register("pdf")`, and the application automatically
    discovers and dispatches to it at runtime.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class PluginRegistry~T~ {
            -registry: dict~str, T~
            +register(name: str, allow_overwrite: bool)
            +get(name: str) T
            +list_plugins() list~str~
            +has(name: str) bool
            +unregister(name: str) bool
        }
        class DocumentExporter {
            <<protocol>>
            +export(title: str, content: str) str
        }
        class MarkdownExporter {
            +export(title: str, content: str) str
        }
        class HTMLExporter {
            +export(title: str, content: str) str
        }
        class JSONExporter {
            +export(title: str, content: str) str
        }
        DocumentExporter <|.. MarkdownExporter
        DocumentExporter <|.. HTMLExporter
        DocumentExporter <|.. JSONExporter
        PluginRegistry o--> DocumentExporter : manages
    ```
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")


# ==============================================================================
# 1. Plugin Interface (Protocol)
# ==============================================================================
class DocumentExporter(Protocol):
    """Protocol for pluggable document serialization formatters."""

    def export(self, title: str, content: str) -> str: ...


# ==============================================================================
# 2. Generic Plugin Registry
# ==============================================================================
class PluginRegistry(Generic[T]):
    """Central directory managing plugin registration, retrieval, and discovery."""

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self._plugins: dict[str, T] = {}

    def register(self, key: str, allow_overwrite: bool = False) -> Callable[[T], T]:
        """Decorator to register a plugin component under a unique lookup key."""
        norm_key = key.lower().strip()

        def decorator(plugin: T) -> T:
            if not allow_overwrite and norm_key in self._plugins:
                raise ValueError(
                    f"Plugin '{norm_key}' is already registered in registry '{self.name}'"
                )
            self._plugins[norm_key] = plugin
            return plugin

        return decorator

    def register_item(self, key: str, item: T, allow_overwrite: bool = False) -> None:
        """Programmatic registration without decorator."""
        self.register(key, allow_overwrite=allow_overwrite)(item)

    def get(self, key: str) -> T:
        """Retrieve plugin by key; raises KeyError if not found."""
        norm_key = key.lower().strip()
        if norm_key not in self._plugins:
            raise KeyError(
                f"No plugin registered under '{norm_key}' in registry '{self.name}'. "
                f"Available: {self.list_plugins()}"
            )
        return self._plugins[norm_key]

    def get_or_default(self, key: str, default: T) -> T:
        """Retrieve plugin by key, or return default fallback if absent."""
        norm_key = key.lower().strip()
        return self._plugins.get(norm_key, default)

    def list_plugins(self) -> list[str]:
        """Return sorted list of all registered plugin identifiers."""
        return sorted(self._plugins.keys())

    def has(self, key: str) -> bool:
        """Check if a plugin identifier exists in the registry."""
        return key.lower().strip() in self._plugins

    def unregister(self, key: str) -> bool:
        """Remove a plugin from the registry."""
        norm_key = key.lower().strip()
        if norm_key in self._plugins:
            del self._plugins[norm_key]
            return True
        return False

    def clear(self) -> None:
        """Remove all registered plugins."""
        self._plugins.clear()


# ==============================================================================
# 3. Concrete Exporter Plugins
# ==============================================================================
exporter_registry: PluginRegistry[type[DocumentExporter]] = PluginRegistry("exporters")


@exporter_registry.register("markdown")
class MarkdownExporter:
    """Exports document content as formatted Markdown."""

    def export(self, title: str, content: str) -> str:
        return f"# {title}\n\n{content}"


@exporter_registry.register("html")
class HTMLExporter:
    """Exports document content as HTML markup."""

    def export(self, title: str, content: str) -> str:
        return f"<article><h1>{title}</h1><p>{content}</p></article>"


@exporter_registry.register("json")
class JSONExporter:
    """Exports document content as structured JSON string."""

    def export(self, title: str, content: str) -> str:
        return json.dumps({"title": title, "content": content}, indent=2)


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    print(f"Available Exporters: {exporter_registry.list_plugins()}")

    # Dispatch via registry lookup
    format_choice = "markdown"
    exporter_cls = exporter_registry.get(format_choice)
    exporter = exporter_cls()
    output = exporter.export("System Architecture", "Overview of core modules.")
    print("\nGenerated Markdown Export:")
    print(output)

    # Dynamic registration at runtime
    @exporter_registry.register("text")
    class PlainTextExporter:
        def export(self, title: str, content: str) -> str:
            return f"TITLE: {title.upper()}\nCONTENT: {content}"

    print(f"\nUpdated Exporters: {exporter_registry.list_plugins()}")
    txt_out = exporter_registry.get("text")().export("Notes", "Plain info")
    print(txt_out)

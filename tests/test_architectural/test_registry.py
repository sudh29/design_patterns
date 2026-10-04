"""Tests for Registry pattern implementation."""

import json

import pytest

from design_patterns.architectural.registry import (
    DocumentExporter,
    HTMLExporter,
    JSONExporter,
    MarkdownExporter,
    PluginRegistry,
    exporter_registry,
)


class TestPluginRegistryLifecycle:
    def test_register_and_get_plugin(self) -> None:
        reg: PluginRegistry[str] = PluginRegistry("test")
        reg.register_item("alpha", "Value A")

        assert reg.get("alpha") == "Value A"
        assert reg.get("ALPHA") == "Value A"  # Case-insensitive
        assert reg.has("alpha") is True
        assert reg.has("beta") is False

    def test_duplicate_registration_raises_value_error(self) -> None:
        reg: PluginRegistry[int] = PluginRegistry("numbers")
        reg.register_item("one", 1)

        with pytest.raises(ValueError, match="already registered"):
            reg.register_item("one", 100, allow_overwrite=False)

    def test_duplicate_registration_with_overwrite(self) -> None:
        reg: PluginRegistry[int] = PluginRegistry("numbers")
        reg.register_item("one", 1)
        reg.register_item("one", 100, allow_overwrite=True)

        assert reg.get("one") == 100

    def test_get_nonexistent_raises_key_error(self) -> None:
        reg: PluginRegistry[str] = PluginRegistry("demo")
        with pytest.raises(KeyError, match="No plugin registered under 'missing'"):
            reg.get("missing")

    def test_get_or_default(self) -> None:
        reg: PluginRegistry[str] = PluginRegistry("demo")
        reg.register_item("found", "exists")

        assert reg.get_or_default("found", "fallback") == "exists"
        assert reg.get_or_default("unknown", "fallback") == "fallback"

    def test_list_plugins_returns_sorted(self) -> None:
        reg: PluginRegistry[str] = PluginRegistry("demo")
        reg.register_item("zulu", "z")
        reg.register_item("bravo", "b")
        reg.register_item("alpha", "a")

        assert reg.list_plugins() == ["alpha", "bravo", "zulu"]

    def test_unregister_and_clear(self) -> None:
        reg: PluginRegistry[str] = PluginRegistry("demo")
        reg.register_item("p1", "1")
        reg.register_item("p2", "2")

        assert reg.unregister("p1") is True
        assert reg.unregister("p1") is False
        assert reg.has("p1") is False
        assert reg.has("p2") is True

        reg.clear()
        assert len(reg.list_plugins()) == 0


class TestBuiltinExporters:
    def test_markdown_exporter(self) -> None:
        exporter = MarkdownExporter()
        out = exporter.export("Doc Title", "Body text")
        assert out == "# Doc Title\n\nBody text"

    def test_html_exporter(self) -> None:
        exporter = HTMLExporter()
        out = exporter.export("Doc Title", "Body text")
        assert out == "<article><h1>Doc Title</h1><p>Body text</p></article>"

    def test_json_exporter(self) -> None:
        exporter = JSONExporter()
        out = exporter.export("Doc Title", "Body text")
        data = json.loads(out)
        assert data == {"title": "Doc Title", "content": "Body text"}

    def test_pre_registered_exporters(self) -> None:
        assert "markdown" in exporter_registry.list_plugins()
        assert "html" in exporter_registry.list_plugins()
        assert "json" in exporter_registry.list_plugins()

        exp_cls: type[DocumentExporter] = exporter_registry.get("markdown")
        instance = exp_cls()
        assert instance.export("T", "C") == "# T\n\nC"

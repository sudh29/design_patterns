"""Tests for the Registry pattern implementation."""

import pytest

from design_patterns.architectural.registry import (
    DataExporter,
    PluginRegistry,
    exporter_registry,
)


class TestPluginRegistry:
    def test_builtin_exporters_registered(self) -> None:
        available = exporter_registry.list_plugins()
        assert "json" in available
        assert "csv" in available

    def test_json_export_execution(self) -> None:
        exporter: DataExporter = exporter_registry.create("json")
        res = exporter.export({"id": 1, "valid": True})
        assert '"id": 1' in res
        assert '"valid": true' in res

    def test_csv_export_execution(self) -> None:
        exporter: DataExporter = exporter_registry.create("csv")
        res = exporter.export({"col1": "A", "col2": "B"})
        assert "col1,col2" in res
        assert "A,B" in res

    def test_duplicate_registration_raises(self) -> None:
        reg = PluginRegistry("test")

        @reg.register("plug")
        class P1:
            pass

        with pytest.raises(KeyError, match="already registered"):

            @reg.register("plug")
            class P2:
                pass

    def test_unknown_plugin_raises(self) -> None:
        reg = PluginRegistry("test")
        with pytest.raises(KeyError, match="Unknown plugin 'missing'"):
            reg.create("missing")

    def test_dynamic_plugin_registration(self) -> None:
        reg = PluginRegistry("custom")

        @reg.register("xml")
        class XmlExporter:
            def __init__(self, root_tag: str = "root") -> None:
                self.root = root_tag

            def export(self, data: dict[str, str]) -> str:
                return f"<{self.root}>...</{self.root}>"

        plugin = reg.create("xml", root_tag="payload")
        assert plugin.export({}) == "<payload>...</payload>"

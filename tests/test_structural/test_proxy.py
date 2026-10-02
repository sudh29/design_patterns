"""Tests for the Proxy pattern implementation."""

import pytest

from design_patterns.structural.proxy import (
    HeavyDocument,
    LazyDocumentProxy,
    ProtectedDocumentProxy,
)


class TestVirtualProxy:
    def test_lazy_loading_behavior(self) -> None:
        proxy = LazyDocumentProxy("REPORT-99")
        assert proxy.is_loaded is False

        content = proxy.read("test_user")
        assert proxy.is_loaded is True
        assert "CONFIDENTIAL FINANCIAL AUDIT DATA FOR REPORT-99" in content

    def test_lazy_write_delegation(self) -> None:
        proxy = LazyDocumentProxy("REPORT-100")
        assert proxy.is_loaded is False
        assert proxy.write("admin", "new content") is True
        assert proxy.is_loaded is True
        assert proxy.read("admin") == "new content"


class TestProtectionProxy:
    def setup_method(self) -> None:
        self.doc = HeavyDocument("DOC-SECURE")
        self.roles = {
            "admin_user": {"admin"},
            "view_user": {"viewer"},
            "unauthorized": set(),
        }
        self.proxy = ProtectedDocumentProxy(self.doc, self.roles)

    def test_read_permissions(self) -> None:
        assert "DOC-SECURE" in self.proxy.read("admin_user")
        assert "DOC-SECURE" in self.proxy.read("view_user")

        with pytest.raises(PermissionError, match="does not have read permissions"):
            self.proxy.read("unauthorized")

        with pytest.raises(PermissionError, match="does not have read permissions"):
            self.proxy.read("unknown_stranger")

    def test_write_permissions(self) -> None:
        # Viewer cannot write
        with pytest.raises(PermissionError, match="does not have admin write privileges"):
            self.proxy.write("view_user", "malicious edit")

        # Admin can write
        assert self.proxy.write("admin_user", "updated safe content") is True
        assert self.proxy.read("admin_user") == "updated safe content"

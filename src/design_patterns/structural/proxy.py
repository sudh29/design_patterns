"""Proxy Design Pattern.

Classification: Structural
Intent:
    Provide a surrogate or placeholder for another object to control access to it.

Motivation & Real-World Analogy:
    In enterprise systems, loading heavy database records or remote documents
    incurs significant network and memory overhead.
    A Proxy acts as an intermediary, delivering three common variants:
    1. **Virtual Proxy**: Defers expensive object instantiation until an actual method is called.
    2. **Protection Proxy**: Validates user authorization/roles before delegating to the subject.
    3. **Caching Proxy**: Intercepts requests to return cached results, bypassing expensive I/O.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Document {
            <<protocol>>
            +read(user: str) str
            +write(user: str, content: str) bool
        }
        class HeavyDocument {
            -doc_id: str
            -content: str
            +read(user: str) str
            +write(user: str, content: str) bool
        }
        class LazyDocumentProxy {
            -doc_id: str
            -_real_doc: HeavyDocument | None
            +read(user: str) str
            +write(user: str, content: str) bool
        }
        class ProtectedDocumentProxy {
            -target: Document
            -user_roles: dict
            +read(user: str) str
            +write(user: str, content: str) bool
        }
        Document <|.. HeavyDocument
        Document <|.. LazyDocumentProxy
        Document <|.. ProtectedDocumentProxy
        LazyDocumentProxy o--> HeavyDocument : lazily initializes
        ProtectedDocumentProxy o--> Document : guards
    ```
"""

from __future__ import annotations

from typing import Protocol


# ==============================================================================
# 1. Subject Protocol
# ==============================================================================
class Document(Protocol):
    """Subject Protocol declaring operations on secure documents."""

    def read(self, user: str) -> str: ...
    def write(self, user: str, content: str) -> bool: ...


# ==============================================================================
# 2. Real Subject
# ==============================================================================
class HeavyDocument:
    """Real Subject: Simulates heavy disk read, decryption, and memory allocation."""

    def __init__(self, doc_id: str) -> None:
        self.doc_id = doc_id
        # Heavy disk/database loading simulation
        self.content: str = f"CONFIDENTIAL FINANCIAL AUDIT DATA FOR {doc_id}"
        self.load_count: int = 1

    def read(self, user: str) -> str:
        return self.content

    def write(self, user: str, content: str) -> bool:
        self.content = content
        return True


# ==============================================================================
# 3. Virtual Proxy (Lazy Initialization)
# ==============================================================================
class LazyDocumentProxy:
    """Virtual Proxy: Defers instantiation of HeavyDocument until first access."""

    def __init__(self, doc_id: str) -> None:
        self.doc_id = doc_id
        self._real_document: HeavyDocument | None = None

    @property
    def is_loaded(self) -> bool:
        return self._real_document is not None

    def _get_document(self) -> HeavyDocument:
        if self._real_document is None:
            self._real_document = HeavyDocument(self.doc_id)
        return self._real_document

    def read(self, user: str) -> str:
        return self._get_document().read(user)

    def write(self, user: str, content: str) -> bool:
        return self._get_document().write(user, content)


# ==============================================================================
# 4. Protection Proxy (Access Control / Authorization)
# ==============================================================================
class ProtectedDocumentProxy:
    """Protection Proxy: Enforces Role-Based Access Control (RBAC) before dispatching."""

    def __init__(self, document: Document, user_roles: dict[str, set[str]]) -> None:
        self._document = document
        self._user_roles = user_roles

    def read(self, user: str) -> str:
        roles = self._user_roles.get(user, set())
        if not roles.intersection({"admin", "auditor", "viewer"}):
            raise PermissionError(f"User '{user}' does not have read permissions.")
        return self._document.read(user)

    def write(self, user: str, content: str) -> bool:
        roles = self._user_roles.get(user, set())
        if "admin" not in roles:
            raise PermissionError(f"User '{user}' does not have admin write privileges.")
        return self._document.write(user, content)


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    print("=== Virtual (Lazy) Proxy Demo ===")
    proxy = LazyDocumentProxy("DOC-2026-X")
    print(f"Proxy created. Is real document loaded? {proxy.is_loaded}")

    # First call triggers lazy load
    print(f"Reading content: {proxy.read('auditor')}")
    print(f"After read. Is real document loaded? {proxy.is_loaded}")

    print("\n=== Protection Proxy Demo ===")
    roles = {
        "alice": {"admin"},
        "bob": {"viewer"},
        "charlie": set(),
    }
    protected_proxy = ProtectedDocumentProxy(proxy, roles)

    print(f"Bob reading: {protected_proxy.read('bob')}")
    try:
        protected_proxy.write("bob", "tampered content")
    except PermissionError as e:
        print(f"Access Denied as expected: {e}")

    protected_proxy.write("alice", "Authorized amendment")
    print(f"Alice wrote update. Current: {protected_proxy.read('alice')}")

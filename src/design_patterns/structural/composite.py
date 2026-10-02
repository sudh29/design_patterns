"""Composite Design Pattern.

Classification: Structural
Intent:
    Compose objects into tree structures to represent part-whole hierarchies.
    Composite lets clients treat individual objects and compositions of objects uniformly.

Motivation & Real-World Analogy:
    In a file system (or organization chart / cloud resource group), a directory
    contains files and subdirectories. Clients should be able to query the size,
    search for names, or compute storage costs uniformly on a single `File` or
    on a root `Directory` containing thousands of nested items, without branching
    on type checks.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class FileSystemItem {
            <<protocol>>
            +name: str
            +get_size() int
            +display(indent: int) str
        }
        class FileLeaf {
            +name: str
            -size: int
            +get_size() int
            +display(indent: int) str
        }
        class DirectoryComposite {
            +name: str
            -children: list[FileSystemItem]
            +add(item: FileSystemItem)
            +remove(item: FileSystemItem)
            +get_size() int
            +display(indent: int) str
        }
        FileSystemItem <|.. FileLeaf
        FileSystemItem <|.. DirectoryComposite
        DirectoryComposite o--> FileSystemItem : contains
    ```
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol


# ==============================================================================
# 1. Component Protocol: Uniform Interface for Leaves and Composites
# ==============================================================================
class FileSystemItem(Protocol):
    """Component Protocol: Defines operations common to both files and directories."""

    @property
    def name(self) -> str: ...

    def get_size(self) -> int:
        """Returns size in bytes."""
        ...

    def display(self, indent: int = 0) -> str:
        """Renders tree structure representation."""
        ...


# ==============================================================================
# 2. Leaf: Represents terminal nodes with no children
# ==============================================================================
@dataclass
class File(FileSystemItem):
    """Leaf node representing an individual file."""

    _name: str
    _size: int

    @property
    def name(self) -> str:
        return self._name

    def get_size(self) -> int:
        return self._size

    def display(self, indent: int = 0) -> str:
        padding = "  " * indent
        return f"{padding}📄 {self._name} ({self._size:,} bytes)"


# ==============================================================================
# 3. Composite: Represents complex nodes containing children
# ==============================================================================
class Directory(FileSystemItem):
    """Composite node representing a directory containing files and sub-directories."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._children: list[FileSystemItem] = []

    @property
    def name(self) -> str:
        return self._name

    def add(self, item: FileSystemItem) -> None:
        self._children.append(item)

    def remove(self, item: FileSystemItem) -> None:
        self._children.remove(item)

    def get_size(self) -> int:
        """Recursively aggregates size across all children without type branching."""
        return sum(child.get_size() for child in self._children)

    def display(self, indent: int = 0) -> str:
        padding = "  " * indent
        lines = [f"{padding}📁 {self._name}/ [Total: {self.get_size():,} bytes]"]
        for child in self._children:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)

    def __iter__(self) -> Iterator[FileSystemItem]:
        """Pythonic generator: Recursively yields all descendant nodes."""
        for child in self._children:
            yield child
            if isinstance(child, Directory):
                yield from child


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    # Assemble tree hierarchy
    root = Directory("workspace")
    src = Directory("src")
    docs = Directory("docs")

    main_py = File("main.py", 1024)
    utils_py = File("utils.py", 2048)
    readme = File("README.md", 512)

    src.add(main_py)
    src.add(utils_py)
    docs.add(readme)

    root.add(src)
    root.add(docs)
    root.add(File(".gitignore", 128))

    print(root.display())
    print(f"\nTotal Workspace Size: {root.get_size():,} bytes")

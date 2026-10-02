"""Iterator Design Pattern.

Classification: Behavioral
Intent:
    Provide a way to access the elements of an aggregate object sequentially
    without exposing its underlying representation.

Motivation & Real-World Analogy:
    In complex domain structures such as a Binary Search Tree (BST) or a
    Paginated Cloud API, the underlying representation is non-linear (trees,
    remote page tokens). The client should be able to iterate linearly over
    items in sorted order, or stream through pages, using standard `for item in collection:`
    syntax without knowing how memory or networking is managed.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Iterator {
            <<protocol>>
            +__iter__() Iterator
            +__next__() Any
        }
        class IterableCollection {
            <<protocol>>
            +__iter__() Iterator
        }
        class BinarySearchTree {
            -root: TreeNode | None
            +insert(val: int)
            +__iter__() Iterator
            +in_order() Generator
        }
        class BSTInOrderIterator {
            -stack: list
            +__next__() int
        }
        Iterator <|.. BSTInOrderIterator
        IterableCollection <|.. BinarySearchTree
        BinarySearchTree ..> BSTInOrderIterator : creates
    ```
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
from dataclasses import dataclass
from typing import Any, Protocol


# ==============================================================================
# 1. Iterator and Iterable Protocols
# ==============================================================================
class CustomIterator(Protocol):
    """Iterator Protocol conforming to Python's dunder __iter__ and __next__."""

    def __iter__(self) -> CustomIterator: ...
    def __next__(self) -> Any: ...


@dataclass
class TreeNode:
    value: int
    left: TreeNode | None = None
    right: TreeNode | None = None


# ==============================================================================
# 2. GoF Class-Based Iterator
# ==============================================================================
class BSTInOrderIterator:
    """Explicit class-based Iterator traversing a Binary Search Tree in-order."""

    def __init__(self, root: TreeNode | None) -> None:
        self._stack: list[TreeNode] = []
        self._push_left(root)

    def _push_left(self, node: TreeNode | None) -> None:
        curr = node
        while curr is not None:
            self._stack.append(curr)
            curr = curr.left

    def __iter__(self) -> BSTInOrderIterator:
        return self

    def __next__(self) -> int:
        if not self._stack:
            raise StopIteration
        node = self._stack.pop()
        self._push_left(node.right)
        return node.value


# ==============================================================================
# 3. Aggregate Collection
# ==============================================================================
class BinarySearchTree:
    """Aggregate Collection holding the tree hierarchy."""

    def __init__(self) -> None:
        self.root: TreeNode | None = None

    def insert(self, value: int) -> None:
        if self.root is None:
            self.root = TreeNode(value)
        else:
            self._insert_node(self.root, value)

    def _insert_node(self, current: TreeNode, value: int) -> None:
        if value < current.value:
            if current.left is None:
                current.left = TreeNode(value)
            else:
                self._insert_node(current.left, value)
        else:
            if current.right is None:
                current.right = TreeNode(value)
            else:
                self._insert_node(current.right, value)

    def __iter__(self) -> Iterator[int]:
        """Provides default in-order traversal via GoF iterator class."""
        return BSTInOrderIterator(self.root)

    # ==========================================================================
    # 4. Pythonic Twist: Generator-based In-Order and Pre-Order Traversal
    # ==========================================================================
    def in_order_generator(self) -> Generator[int, None, None]:
        """Pythonic generator alternative using recursive 'yield from'."""

        def _traverse(node: TreeNode | None) -> Generator[int, None, None]:
            if node is not None:
                yield from _traverse(node.left)
                yield node.value
                yield from _traverse(node.right)

        yield from _traverse(self.root)

    def pre_order_generator(self) -> Generator[int, None, None]:
        """Pre-order traversal (Root -> Left -> Right)."""

        def _traverse(node: TreeNode | None) -> Generator[int, None, None]:
            if node is not None:
                yield node.value
                yield from _traverse(node.left)
                yield from _traverse(node.right)

        yield from _traverse(self.root)


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    bst = BinarySearchTree()
    for val in [50, 30, 70, 20, 40, 60, 80]:
        bst.insert(val)

    print("=== GoF Class-Based Iterator ===")
    print([x for x in bst])

    print("\n=== Pythonic Generator-Based In-Order ===")
    print(list(bst.in_order_generator()))

    print("\n=== Pythonic Generator-Based Pre-Order ===")
    print(list(bst.pre_order_generator()))

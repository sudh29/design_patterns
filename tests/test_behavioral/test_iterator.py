"""Tests for the Iterator pattern implementation."""

import pytest

from design_patterns.behavioral.iterator import (
    BinarySearchTree,
    BSTInOrderIterator,
)


class TestIteratorPattern:
    def test_empty_tree_iterator(self) -> None:
        bst = BinarySearchTree()
        it = iter(bst)
        with pytest.raises(StopIteration):
            next(it)

    def test_in_order_iterator(self) -> None:
        bst = BinarySearchTree()
        for num in [5, 3, 7, 2, 4, 6, 8]:
            bst.insert(num)

        result = list(bst)
        assert result == [2, 3, 4, 5, 6, 7, 8]

    def test_in_order_generator(self) -> None:
        bst = BinarySearchTree()
        for num in [10, 5, 15, 3, 7, 12, 18]:
            bst.insert(num)

        gen_result = list(bst.in_order_generator())
        assert gen_result == sorted([10, 5, 15, 3, 7, 12, 18])

    def test_pre_order_generator(self) -> None:
        bst = BinarySearchTree()
        for num in [4, 2, 5, 1, 3]:
            bst.insert(num)

        # Pre-order: 4 -> 2 -> 1 -> 3 -> 5
        pre_result = list(bst.pre_order_generator())
        assert pre_result == [4, 2, 1, 3, 5]

    def test_iterator_protocol_self_return(self) -> None:
        iterator = BSTInOrderIterator(None)
        assert iter(iterator) is iterator

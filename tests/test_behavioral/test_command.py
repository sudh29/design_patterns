"""Tests for the Command pattern implementation."""

import pytest

from design_patterns.behavioral.command import (
    DeleteTextCommand,
    EditorInvoker,
    InsertTextCommand,
    TextDocument,
)


class TestTextDocument:
    def test_insert_out_of_bounds(self) -> None:
        doc = TextDocument("abc")
        with pytest.raises(IndexError, match="Position out of bounds"):
            doc.insert(10, "x")

    def test_delete_out_of_bounds(self) -> None:
        doc = TextDocument("abc")
        with pytest.raises(IndexError, match="Range out of bounds"):
            doc.delete(2, 5)


class TestCommandPattern:
    def test_execute_and_undo_flow(self) -> None:
        doc = TextDocument()
        invoker = EditorInvoker()

        # Step 1: Insert "Python"
        invoker.execute_command(InsertTextCommand(doc, 0, "Python"))
        assert doc.content == "Python"

        # Step 2: Insert " 3.12"
        invoker.execute_command(InsertTextCommand(doc, 6, " 3.12"))
        assert doc.content == "Python 3.12"

        # Step 3: Undo step 2
        assert invoker.undo() is True
        assert doc.content == "Python"

        # Step 4: Redo step 2
        assert invoker.redo() is True
        assert doc.content == "Python 3.12"

    def test_delete_and_undo(self) -> None:
        doc = TextDocument("Hello Beautiful World")
        invoker = EditorInvoker()

        # Delete "Beautiful " (pos 6, len 10)
        invoker.execute_command(DeleteTextCommand(doc, 6, 10))
        assert doc.content == "Hello World"

        # Undo delete
        invoker.undo()
        assert doc.content == "Hello Beautiful World"

    def test_empty_stacks_return_false(self) -> None:
        invoker = EditorInvoker()
        assert invoker.undo() is False
        assert invoker.redo() is False

    def test_redo_stack_cleared_on_new_command(self) -> None:
        doc = TextDocument("Init")
        invoker = EditorInvoker()

        invoker.execute_command(InsertTextCommand(doc, 4, " 1"))
        invoker.undo()
        assert doc.content == "Init"

        # Execute a different command; previous redo branch should be discarded
        invoker.execute_command(InsertTextCommand(doc, 4, " 2"))
        assert doc.content == "Init 2"
        assert invoker.redo() is False

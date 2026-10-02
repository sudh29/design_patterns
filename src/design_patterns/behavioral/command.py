"""Command Design Pattern.

Classification: Behavioral
Intent:
    Encapsulate a request as an object, thereby letting you parameterize clients with
    different requests, queue or log requests, and support undoable operations.

Motivation & Real-World Analogy:
    In rich text editors, IDEs, or transactional databases, user actions
    (typing text, deleting blocks, formatting) must be recorded so that they can be
    undone (`Ctrl+Z`), redone (`Ctrl+Y`), macro-recorded, or scheduled into async task queues.
    The Command pattern encapsulates the action, its receiver, and the state required
    to revert it into a standalone object.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class Command {
            <<protocol>>
            +execute() bool
            +undo() bool
        }
        class InsertTextCommand {
            -receiver: TextDocument
            -text: str
            -position: int
            +execute() bool
            +undo() bool
        }
        class DeleteTextCommand {
            -receiver: TextDocument
            -deleted_text: str
            -position: int
            +execute() bool
            +undo() bool
        }
        class TextDocument {
            -content: str
            +insert(pos: int, text: str)
            +delete(pos: int, length: int) str
        }
        class EditorInvoker {
            -undo_stack: list[Command]
            -redo_stack: list[Command]
            +execute_command(cmd: Command)
            +undo()
            +redo()
        }
        Command <|.. InsertTextCommand
        Command <|.. DeleteTextCommand
        InsertTextCommand o--> TextDocument
        DeleteTextCommand o--> TextDocument
        EditorInvoker o--> Command
    ```
"""

from __future__ import annotations

from typing import Protocol


# ==============================================================================
# 1. Receiver: Holds core business logic & state
# ==============================================================================
class TextDocument:
    """Receiver: The actual document containing raw text content."""

    def __init__(self, initial_text: str = "") -> None:
        self.content: str = initial_text

    def insert(self, position: int, text: str) -> None:
        if position < 0 or position > len(self.content):
            raise IndexError("Position out of bounds")
        self.content = self.content[:position] + text + self.content[position:]

    def delete(self, position: int, length: int) -> str:
        if position < 0 or position + length > len(self.content):
            raise IndexError("Range out of bounds")
        deleted = self.content[position : position + length]
        self.content = self.content[:position] + self.content[position + length :]
        return deleted


# ==============================================================================
# 2. Command Protocol & Concrete Commands
# ==============================================================================
class Command(Protocol):
    """Command Protocol: Encapsulates operation execution and reverse undo logic."""

    def execute(self) -> bool: ...
    def undo(self) -> bool: ...


class InsertTextCommand:
    """Concrete Command for inserting text."""

    def __init__(self, doc: TextDocument, position: int, text: str) -> None:
        self._doc = doc
        self._position = position
        self._text = text

    def execute(self) -> bool:
        self._doc.insert(self._position, self._text)
        return True

    def undo(self) -> bool:
        self._doc.delete(self._position, len(self._text))
        return True


class DeleteTextCommand:
    """Concrete Command for deleting text, capturing deleted snippet for undo."""

    def __init__(self, doc: TextDocument, position: int, length: int) -> None:
        self._doc = doc
        self._position = position
        self._length = length
        self._deleted_text: str = ""

    def execute(self) -> bool:
        self._deleted_text = self._doc.delete(self._position, self._length)
        return True

    def undo(self) -> bool:
        self._doc.insert(self._position, self._deleted_text)
        return True


# ==============================================================================
# 3. Invoker: Manages Execution and Undo/Redo Stacks
# ==============================================================================
class EditorInvoker:
    """Invoker: Triggers commands and maintains history for undo/redo."""

    def __init__(self) -> None:
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute_command(self, command: Command) -> bool:
        if command.execute():
            self._undo_stack.append(command)
            self._redo_stack.clear()  # Clear forward history on new action
            return True
        return False

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        cmd = self._undo_stack.pop()
        if cmd.undo():
            self._redo_stack.append(cmd)
            return True
        return False

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        cmd = self._redo_stack.pop()
        if cmd.execute():
            self._undo_stack.append(cmd)
            return True
        return False


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    doc = TextDocument("Hello")
    invoker = EditorInvoker()

    print(f"Initial: '{doc.content}'")

    invoker.execute_command(InsertTextCommand(doc, 5, " World!"))
    print(f"After Insert: '{doc.content}'")

    invoker.execute_command(DeleteTextCommand(doc, 5, 7))
    print(f"After Delete: '{doc.content}'")

    invoker.undo()
    print(f"After Undo: '{doc.content}'")

    invoker.redo()
    print(f"After Redo: '{doc.content}'")

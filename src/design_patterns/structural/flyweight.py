"""Flyweight Design Pattern.

Classification: Structural
Intent:
    Use sharing to support large numbers of fine-grained objects efficiently.

Motivation & Real-World Analogy:
    In graphical rendering systems (such as a 3D forest simulation or text editor
    glyph rendering), rendering 500,000 trees naively by storing texture bitmaps,
    mesh vertices, and color profiles in every individual tree object will instantly
    exhaust RAM.
    The Flyweight pattern splits object state into:
    1. **Intrinsic State**: Immutable, shared context stored once in the Flyweight
       (e.g., Species, Texture, Polygon Mesh).
    2. **Extrinsic State**: Context-dependent properties stored in the client or
       lightweight container (e.g., X, Y coordinates, scale, age).

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class TreeType {
            <<flyweight>>
            -species: str
            -mesh_data: bytes
            -texture: str
            +render(x: float, y: float, scale: float) str
        }
        class TreeFactory {
            -_tree_types: dict
            +get_tree_type(species: str, texture: str) TreeType
        }
        class TreeContext {
            <<extrinsic>>
            -x: float
            -y: float
            -scale: float
            -tree_type: TreeType
            +draw() str
        }
        TreeFactory o--> TreeType : pools & reuses
        TreeContext o--> TreeType : references
    ```
"""

from __future__ import annotations

from typing import ClassVar


# ==============================================================================
# 1. Flyweight: Stores Intrinsic State (Shared & Immutable)
# ==============================================================================
class TreeType:
    """Flyweight: Holds large intrinsic state shared across thousands of tree instances."""

    __slots__ = ("species", "texture", "mesh_data")

    def __init__(self, species: str, texture: str, mesh_data: bytes) -> None:
        self.species = species
        self.texture = texture
        self.mesh_data = mesh_data  # Simulates heavy geometry payload

    def render(self, x: float, y: float, scale: float) -> str:
        """Renders tree at extrinsic coordinates using shared intrinsic geometry."""
        return (
            f"Rendered {self.species} at ({x:.1f}, {y:.1f}) "
            f"with scale {scale:.1f} using texture '{self.texture}'"
        )


# ==============================================================================
# 2. Flyweight Factory: Manages Cache of Flyweights
# ==============================================================================
class TreeFactory:
    """Flyweight Factory: Ensures identical tree types are shared rather than re-instantiated."""

    _types: ClassVar[dict[tuple[str, str], TreeType]] = {}

    @classmethod
    def get_tree_type(
        cls, species: str, texture: str, mesh_data: bytes = b"default_mesh"
    ) -> TreeType:
        key = (species, texture)
        if key not in cls._types:
            cls._types[key] = TreeType(species, texture, mesh_data)
        return cls._types[key]

    @classmethod
    def total_flyweights(cls) -> int:
        return len(cls._types)

    @classmethod
    def clear(cls) -> None:
        cls._types.clear()


# ==============================================================================
# 3. Context / Client Container: Stores Extrinsic State
# ==============================================================================
class Tree:
    """Extrinsic context holding unique coordinates and a reference to the shared Flyweight."""

    __slots__ = ("x", "y", "scale", "tree_type")

    def __init__(self, x: float, y: float, scale: float, tree_type: TreeType) -> None:
        self.x = x
        self.y = y
        self.scale = scale
        self.tree_type = tree_type

    def draw(self) -> str:
        return self.tree_type.render(self.x, self.y, self.scale)


# ==============================================================================
# 4. Forest Simulation
# ==============================================================================
class Forest:
    """Client managing an entire ecosystem of thousands of trees."""

    def __init__(self) -> None:
        self.trees: list[Tree] = []

    def plant_tree(self, x: float, y: float, scale: float, species: str, texture: str) -> Tree:
        tree_type = TreeFactory.get_tree_type(species, texture)
        tree = Tree(x, y, scale, tree_type)
        self.trees.append(tree)
        return tree

    def count(self) -> int:
        return len(self.trees)


# ==============================================================================
# 5. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    forest = Forest()

    # Plant 10,000 trees of 2 species
    for i in range(5000):
        forest.plant_tree(
            x=float(i), y=float(i * 2), scale=1.0, species="Oak", texture="oak_bark.png"
        )
        forest.plant_tree(
            x=float(i * 3), y=float(i), scale=1.2, species="Pine", texture="pine_needles.png"
        )

    print(f"Total Trees in Forest:     {forest.count():,}")
    print(f"Unique Flyweights in Memory: {TreeFactory.total_flyweights()}")
    assert TreeFactory.total_flyweights() == 2, "Failed to share Flyweight instances!"

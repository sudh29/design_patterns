"""Tests for the Flyweight pattern implementation."""

from design_patterns.structural.flyweight import Forest, TreeFactory


class TestFlyweightPattern:
    def setup_method(self) -> None:
        TreeFactory.clear()

    def test_flyweight_instance_sharing(self) -> None:
        forest = Forest()
        forest.plant_tree(10.0, 20.0, 1.0, "Birch", "birch_white.png")
        forest.plant_tree(15.0, 25.0, 1.5, "Birch", "birch_white.png")
        forest.plant_tree(30.0, 40.0, 2.0, "Redwood", "redwood_rough.png")

        assert forest.count() == 3
        # Birch should share the single flyweight instance
        assert TreeFactory.total_flyweights() == 2

        t1, t2, t3 = forest.trees
        assert t1.tree_type is t2.tree_type
        assert t1.tree_type is not t3.tree_type

    def test_extrinsic_rendering(self) -> None:
        forest = Forest()
        t = forest.plant_tree(5.0, 10.0, 1.2, "Maple", "maple.png")
        output = t.draw()
        assert "Rendered Maple at (5.0, 10.0)" in output
        assert "scale 1.2" in output
        assert "texture 'maple.png'" in output

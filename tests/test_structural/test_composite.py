"""Tests for the Composite pattern implementation."""

from design_patterns.structural.composite import Directory, File


class TestCompositePattern:
    def test_leaf_file(self) -> None:
        file = File("app.py", 2048)
        assert file.name == "app.py"
        assert file.get_size() == 2048
        assert "📄 app.py (2,048 bytes)" in file.display()

    def test_directory_recursive_size(self) -> None:
        root = Directory("root")
        sub1 = Directory("sub1")
        sub2 = Directory("sub2")

        f1 = File("f1.txt", 100)
        f2 = File("f2.txt", 200)
        f3 = File("f3.txt", 300)

        sub1.add(f1)
        sub2.add(f2)
        sub2.add(f3)

        root.add(sub1)
        root.add(sub2)

        assert sub1.get_size() == 100
        assert sub2.get_size() == 500
        assert root.get_size() == 600

    def test_directory_remove(self) -> None:
        root = Directory("test")
        file1 = File("f1.txt", 50)
        file2 = File("f2.txt", 50)

        root.add(file1)
        root.add(file2)
        assert root.get_size() == 100

        root.remove(file1)
        assert root.get_size() == 50

    def test_directory_generator_iteration(self) -> None:
        root = Directory("root")
        sub = Directory("sub")
        f1 = File("f1.txt", 10)
        f2 = File("f2.txt", 20)

        sub.add(f2)
        root.add(f1)
        root.add(sub)

        items = list(root)
        names = [item.name for item in items]
        assert "f1.txt" in names
        assert "sub" in names
        assert "f2.txt" in names

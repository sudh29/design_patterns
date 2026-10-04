"""Tests for CLI runner implementation."""

from unittest.mock import patch

import pytest

from design_patterns.cli import (
    PATTERNS,
    find_pattern,
    list_patterns,
    main,
    run_pattern,
)


class TestCliPatternCatalog:
    def test_all_28_patterns_registered(self) -> None:
        assert len(PATTERNS) == 28

        categories = {p.category for p in PATTERNS}
        assert categories == {"Creational", "Structural", "Behavioral", "Architectural"}

        creational = [p for p in PATTERNS if p.category == "Creational"]
        structural = [p for p in PATTERNS if p.category == "Structural"]
        behavioral = [p for p in PATTERNS if p.category == "Behavioral"]
        architectural = [p for p in PATTERNS if p.category == "Architectural"]

        assert len(creational) == 5
        assert len(structural) == 7
        assert len(behavioral) == 10
        assert len(architectural) == 6

    def test_list_patterns_filter(self) -> None:
        all_p = list_patterns()
        assert len(all_p) == 28

        creational = list_patterns("creational")
        assert len(creational) == 5
        assert all(p.category == "Creational" for p in creational)

        empty = list_patterns("nonexistent")
        assert len(empty) == 0

    def test_find_pattern_various_formats(self) -> None:
        # Full name
        p1 = find_pattern("Factory Method")
        assert p1 is not None and p1.name == "Factory Method"

        # Module suffix
        p2 = find_pattern("factory_method")
        assert p2 is not None and p2.name == "Factory Method"

        # Hyphenated
        p3 = find_pattern("factory-method")
        assert p3 is not None and p3.name == "Factory Method"

        # Subpackage format
        p4 = find_pattern("creational.factory_method")
        assert p4 is not None and p4.name == "Factory Method"

        # Not found
        assert find_pattern("invalid_pattern") is None


class TestCliExecution:
    def test_cli_list_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main(["--list"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Found 28 pattern(s)" in captured.out
        assert "Factory Method" in captured.out
        assert "Visitor" in captured.out

    def test_cli_list_with_category(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main(["--list", "--category", "behavioral"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Found 10 pattern(s)" in captured.out
        assert "Template Method" in captured.out
        assert "Factory Method" not in captured.out

    def test_cli_run_invalid_pattern(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main(["--run", "fake_pattern"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error: Pattern 'fake_pattern' not recognized" in captured.err

    def test_cli_run_valid_pattern(self) -> None:
        p = find_pattern("strategy")
        assert p is not None
        with patch("runpy.run_module") as mock_run:
            run_pattern(p)
            mock_run.assert_called_once_with(p.module, run_name="__main__")

    def test_cli_no_args_shows_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main([])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "usage: design-patterns" in captured.out

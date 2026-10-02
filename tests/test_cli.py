"""Tests for the interactive CLI runner."""

import pytest

from design_patterns.cli import list_patterns, main, run_pattern


def test_cli_list_patterns(capsys: pytest.CaptureFixture[str]) -> None:
    list_patterns()
    captured = capsys.readouterr()
    assert "DESIGN PATTERNS IN PYTHON" in captured.out
    assert "CREATIONAL PATTERNS" in captured.out
    assert "STRUCTURAL PATTERNS" in captured.out
    assert "BEHAVIORAL PATTERNS" in captured.out
    assert "ARCHITECTURAL PATTERNS" in captured.out


def test_cli_run_pattern_success(capsys: pytest.CaptureFixture[str]) -> None:
    success = run_pattern("creational", "factory_method")
    captured = capsys.readouterr()
    assert success is True
    assert "completed successfully" in captured.out


def test_cli_run_pattern_invalid_category(capsys: pytest.CaptureFixture[str]) -> None:
    success = run_pattern("invalid_category", "factory_method")
    captured = capsys.readouterr()
    assert success is False
    assert "Unknown category" in captured.out


def test_cli_run_pattern_invalid_pattern(capsys: pytest.CaptureFixture[str]) -> None:
    success = run_pattern("creational", "nonexistent_pattern")
    captured = capsys.readouterr()
    assert success is False
    assert "Unknown pattern" in captured.out


def test_cli_main_list(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["cli.py", "list"])
    main()
    captured = capsys.readouterr()
    assert "DESIGN PATTERNS IN PYTHON" in captured.out


def test_cli_main_run(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["cli.py", "run", "structural", "adapter"])
    main()
    captured = capsys.readouterr()
    assert "completed successfully" in captured.out


def test_cli_main_run_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["cli.py", "run", "structural", "unknown"])
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1

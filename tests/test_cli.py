from __future__ import annotations

import json

import pytest

from omsf_prefix_smoke import __version__
from omsf_prefix_smoke.cli import main


def test_verify_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["verify"]) == 0

    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["status"] == "ok"
    assert captured.err == ""


def test_pretty_verify_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["verify", "--pretty"]) == 0

    captured = capsys.readouterr()
    assert "\n  \"data\"" in captured.out
    assert captured.err == ""


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match="0"):
        main(["--version"])

    captured = capsys.readouterr()
    assert captured.out == f"omsf-prefix-smoke {__version__}\n"
    assert captured.err == ""


def test_verification_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import omsf_prefix_smoke.cli as cli

    def fail() -> dict[str, object]:
        raise cli.VerificationError("deliberate test failure")

    monkeypatch.setattr(cli, "build_report", fail)
    assert cli.main(["verify"]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "verification failed: deliberate test failure\n"


def test_unhandled_command_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    import argparse

    import omsf_prefix_smoke.cli as cli

    class FakeParser:
        def parse_args(self, argv: object) -> argparse.Namespace:
            return argparse.Namespace(command="unknown")

    monkeypatch.setattr(cli, "build_parser", FakeParser)
    with pytest.raises(AssertionError, match="unhandled command"):
        cli.main([])


def test_python_module_entry_point(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import runpy
    import sys

    monkeypatch.setattr(sys, "argv", ["python -m omsf_prefix_smoke", "verify"])
    with pytest.raises(SystemExit, match="0"):
        runpy.run_module("omsf_prefix_smoke", run_name="__main__")

    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == "ok"
    assert captured.err == ""

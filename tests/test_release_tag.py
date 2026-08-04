from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_release_tag.py"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_release_tag", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matching_release_tag() -> None:
    module = load_script()
    assert module.main("v0.1.0") == 0
    assert module.main("0.1.0") == 0


def test_mismatched_release_tag() -> None:
    module = load_script()
    assert module.main("v9.9.9") == 1

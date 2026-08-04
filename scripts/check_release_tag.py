#!/usr/bin/env python3
"""Check that a GitHub release tag matches all declared package versions."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pyproject_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    version = project["version"]
    if not isinstance(version, str):
        raise TypeError("project.version must be a string")
    return version


def recipe_version() -> str:
    recipe = (ROOT / "conda.recipe" / "recipe.yaml").read_text(encoding="utf-8")
    match = re.search(r'^\s*version:\s*"([^\"]+)"\s*$', recipe, flags=re.MULTILINE)
    if match is None:
        raise ValueError("could not find context.version in conda.recipe/recipe.yaml")
    return match.group(1)


def main(tag: str) -> int:
    normalized_tag = tag.removeprefix("v")
    declared_versions = {
        "pyproject.toml": pyproject_version(),
        "conda.recipe/recipe.yaml": recipe_version(),
    }

    mismatches = {
        location: version
        for location, version in declared_versions.items()
        if version != normalized_tag
    }
    if mismatches:
        print(f"release tag {tag!r} resolves to version {normalized_tag!r}", file=sys.stderr)
        for location, version in mismatches.items():
            print(f"{location} declares {version!r}", file=sys.stderr)
        return 1

    print(f"release tag {tag!r} matches version {normalized_tag}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <release-tag>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))

"""Deterministic verification report for the installed smoke-test package."""

from __future__ import annotations

import hashlib
import json
import platform
from importlib import metadata, resources
from typing import Any

PACKAGE_NAME = "omsf-prefix-smoke"
DEPENDENCY_NAMES = ("packaging",)
PAYLOAD_RESOURCE = "data/payload.json"
EXPECTED_PAYLOAD_SHA256 = "59bbfcac12f2d047a322f393b9c98dc2d14e693a019c76365cd4429b5b1736d3"


class VerificationError(RuntimeError):
    """Raised when the installed package does not match its expected payload."""


def payload_bytes() -> bytes:
    """Read the embedded payload exactly as installed."""

    return resources.files("omsf_prefix_smoke").joinpath(PAYLOAD_RESOURCE).read_bytes()


def sha256_hex(data: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(data).hexdigest()


def build_report() -> dict[str, Any]:
    """Build and validate a stable, machine-readable installation report."""

    payload = payload_bytes()
    actual_digest = sha256_hex(payload)
    if actual_digest != EXPECTED_PAYLOAD_SHA256:
        raise VerificationError(
            "embedded payload digest mismatch: "
            f"expected {EXPECTED_PAYLOAD_SHA256}, got {actual_digest}"
        )

    dependency_versions = {
        dependency: metadata.version(dependency) for dependency in DEPENDENCY_NAMES
    }

    return {
        "data": {
            "path": PAYLOAD_RESOURCE,
            "sha256": actual_digest,
            "size": len(payload),
        },
        "dependencies": dependency_versions,
        "package": {
            "name": PACKAGE_NAME,
            "version": metadata.version(PACKAGE_NAME),
        },
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
        "schema_version": 1,
        "status": "ok",
    }


def render_report(report: dict[str, Any], *, pretty: bool = False) -> str:
    """Serialize a report with stable key ordering and one trailing newline."""

    if pretty:
        return json.dumps(report, indent=2, sort_keys=True) + "\n"
    return json.dumps(report, separators=(",", ":"), sort_keys=True) + "\n"

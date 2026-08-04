from __future__ import annotations

import json
from importlib import metadata

import pytest

from omsf_prefix_smoke.verification import (
    EXPECTED_PAYLOAD_SHA256,
    build_report,
    payload_bytes,
    render_report,
    sha256_hex,
)


def test_payload_matches_embedded_digest() -> None:
    assert sha256_hex(payload_bytes()) == EXPECTED_PAYLOAD_SHA256


def test_report_describes_installed_environment() -> None:
    report = build_report()

    assert report["status"] == "ok"
    assert report["schema_version"] == 1
    assert report["package"] == {
        "name": "omsf-prefix-smoke",
        "version": metadata.version("omsf-prefix-smoke"),
    }
    assert report["dependencies"] == {"packaging": metadata.version("packaging")}
    assert report["data"]["sha256"] == EXPECTED_PAYLOAD_SHA256
    assert report["data"]["size"] == len(payload_bytes())


def test_compact_report_is_stable_json() -> None:
    report = build_report()
    rendered = render_report(report)

    assert rendered.endswith("\n")
    assert "\n" not in rendered[:-1]
    assert json.loads(rendered) == report
    assert rendered == render_report(report)


def test_pretty_report_is_stable_json() -> None:
    report = build_report()
    rendered = render_report(report, pretty=True)

    assert rendered.endswith("\n")
    assert "\n  \"data\"" in rendered
    assert json.loads(rendered) == report


def test_tampered_payload_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    import omsf_prefix_smoke.verification as verification

    monkeypatch.setattr(verification, "payload_bytes", lambda: b"tampered")
    with pytest.raises(verification.VerificationError, match="payload digest mismatch"):
        verification.build_report()

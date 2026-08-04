"""Command-line interface for omsf-prefix-smoke."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from omsf_prefix_smoke import __version__
from omsf_prefix_smoke.verification import VerificationError, build_report, render_report


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""

    parser = argparse.ArgumentParser(
        prog="omsf-prefix-smoke",
        description="Verify an installed OMSF prefix.dev smoke-test package.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)
    verify_parser = subparsers.add_parser(
        "verify",
        help="validate package data and print a machine-readable report",
    )
    verify_parser.add_argument(
        "--pretty",
        action="store_true",
        help="indent the JSON report for humans",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""

    args = build_parser().parse_args(argv)

    if args.command == "verify":
        try:
            report = build_report()
        except (VerificationError, OSError) as error:
            print(f"verification failed: {error}", file=sys.stderr)
            return 1
        sys.stdout.write(render_report(report, pretty=args.pretty))
        return 0

    raise AssertionError(f"unhandled command: {args.command}")

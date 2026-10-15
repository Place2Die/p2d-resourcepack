"""Command line: ``./pack.py validate`` and ``./pack.py build``."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from p2dpack.build import BuildError, PackBuilder
from p2dpack.merge import MergeError
from p2dpack.report import Report
from p2dpack.validation import PackValidator

DEFAULT_SOURCE = Path("pack")
DEFAULT_OUTPUT = Path("build")
# Optional BetterModel output (its build folder, or the zip it writes with pack-type: zip).
DEFAULT_BETTERMODEL = (Path("bettermodel"), Path("bettermodel.zip"))


def _print_report(title: str, report: Report) -> None:
    for line in report.messages():
        print(f"  {line}")
    print(f"{title}: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")


def _default_bettermodel() -> Path | None:
    return next((path for path in DEFAULT_BETTERMODEL if path.exists()), None)


def _github_output(**values: str) -> None:
    target = os.environ.get("GITHUB_OUTPUT")
    if target:
        with open(target, "a", encoding="utf-8") as output:
            for key, value in values.items():
                output.write(f"{key}={value}\n")


def validate(args: argparse.Namespace) -> int:
    report = PackValidator.default().validate(args.pack)
    _print_report(f"validate {args.pack}", report)
    return 0 if report.ok else 1


def build(args: argparse.Namespace) -> int:
    bettermodel = args.bettermodel if args.bettermodel is not None else _default_bettermodel()
    print(f"BetterModel pack: {bettermodel if bettermodel else 'none, nothing to merge'}")
    try:
        result = PackBuilder.default().build(args.pack, args.out, bettermodel)
    except BuildError as error:
        _print_report(f"validate {error.stage}", error.report)
        return 1
    except MergeError as error:
        for problem in error.problems:
            print(f"  ERROR {problem}")
        print(f"merge {bettermodel}: {len(error.problems)} error(s)")
        return 1
    _print_report(f"validate {args.pack}", result.source_report)
    if result.merge is not None:
        print(f"merged {bettermodel}: {len(result.merge.added)} file(s) added, "
              f"{len(result.merge.identical)} identical skipped, "
              f"root files replaced by ours: {', '.join(result.merge.replaced_root_files) or 'none'}")
    print(f"archive: {result.archive}")
    print(f"sha1: {result.sha1}")
    _github_output(archive=str(result.archive), sha1=result.sha1)
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="pack.py", description="Place2Die resource pack tooling")
    commands = root.add_subparsers(dest="command", required=True)

    validate_command = commands.add_parser("validate", help="validate the pack sources")
    validate_command.add_argument("--pack", type=Path, default=DEFAULT_SOURCE)
    validate_command.set_defaults(handler=validate)

    build_command = commands.add_parser("build", help="validate, merge BetterModel's pack, zip, print the SHA-1")
    build_command.add_argument("--pack", type=Path, default=DEFAULT_SOURCE)
    build_command.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    build_command.add_argument("--bettermodel", type=Path, default=None,
                               help="BetterModel pack folder or zip (default: ./bettermodel or "
                                    "./bettermodel.zip when present)")
    build_command.set_defaults(handler=build)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())

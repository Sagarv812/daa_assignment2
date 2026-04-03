#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from check_triangle_counts import ROOT, build_solver, check_file


def discover_testcases(tests_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in tests_dir.iterdir()
        if path.is_file() and path.suffix in {".in", ".txt"}
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run triangle-count validity checks for every testcase in tests/."
    )
    parser.add_argument(
        "--tests-dir",
        default="tests",
        help="directory containing assignment-format .in/.txt testcase files (default: tests)",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="do not run make before checking",
    )
    args = parser.parse_args()

    tests_dir = Path(args.tests_dir)
    if not tests_dir.is_absolute():
        tests_dir = ROOT / tests_dir

    if not tests_dir.is_dir():
        print(f"{tests_dir}: not a directory", file=sys.stderr)
        return 2

    testcases = discover_testcases(tests_dir)
    if not testcases:
        print(f"{tests_dir}: no .in or .txt testcase files found", file=sys.stderr)
        return 2

    try:
        build_solver(skip_build=args.skip_build)
    except subprocess.CalledProcessError as exc:
        print(f"build failed with exit code {exc.returncode}", file=sys.stderr)
        return 2

    passed_files = 0
    failed_files = 0
    error_files = 0

    for testcase in testcases:
        try:
            passed = check_file(testcase)
            print()
        except FileNotFoundError:
            print(f"{testcase}: file not found", file=sys.stderr)
            error_files += 1
            continue
        except ValueError as exc:
            print(f"{testcase}: parse error: {exc}", file=sys.stderr)
            error_files += 1
            continue
        except subprocess.CalledProcessError as exc:
            print(f"{testcase}: solver failed with exit code {exc.returncode}", file=sys.stderr)
            if exc.stderr:
                print(exc.stderr, file=sys.stderr, end="")
            error_files += 1
            continue

        if passed:
            passed_files += 1
        else:
            failed_files += 1

    total_files = len(testcases)
    print(
        f"Summary: {passed_files} passed, {failed_files} failed, {error_files} errors "
        f"out of {total_files} testcase files."
    )

    if failed_files > 0:
        return 1
    if error_files > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOLVER = ROOT / "build" / "art_gallery"


@dataclass
class InputSummary:
    case_count: int
    expected_triangles: list[int]
    trailing_tokens: int


@dataclass
class OutputSummary:
    actual_triangles: list[int]
    trailing_tokens: int


def parse_input_file(path: Path) -> InputSummary:
    tokens = path.read_text().split()
    if not tokens:
        raise ValueError("input file is empty")

    idx = 0

    def next_token() -> str:
        nonlocal idx
        if idx >= len(tokens):
            raise ValueError("unexpected end of input while parsing testcase file")
        token = tokens[idx]
        idx += 1
        return token

    case_count = int(next_token())
    expected_triangles: list[int] = []

    for _ in range(case_count):
        outer_vertices = int(next_token())
        for _ in range(outer_vertices):
            next_token()
            next_token()

        hole_count = int(next_token())
        total_vertices = outer_vertices

        for _ in range(hole_count):
            hole_vertices = int(next_token())
            total_vertices += hole_vertices
            for _ in range(hole_vertices):
                next_token()
                next_token()

        expected_triangles.append(total_vertices + 2 * hole_count - 2)

    return InputSummary(
        case_count=case_count,
        expected_triangles=expected_triangles,
        trailing_tokens=len(tokens) - idx,
    )


def is_integer_token(token: str) -> bool:
    if not token:
        return False
    if token[0] in "+-":
        return token[1:].isdigit()
    return token.isdigit()


def parse_float_list(line: str, expected_count: int, what: str) -> list[float]:
    parts = line.split()
    if len(parts) != expected_count:
        raise ValueError(f"expected {expected_count} values for {what}, got {len(parts)}")
    return [float(part) for part in parts]


def parse_solver_output(output: str, expected_triangles: list[int]) -> OutputSummary:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    idx = 0

    actual_triangles: list[int] = []

    for case_idx, expected_triangle_count in enumerate(expected_triangles, start=1):
        if idx >= len(lines):
            raise ValueError("unexpected end of solver output")

        if is_integer_token(lines[idx]) and int(lines[idx]) == expected_triangle_count:
            idx += 1

        triangle_count = 0
        while idx < len(lines) and not is_integer_token(lines[idx]):
            parse_float_list(lines[idx], 6, f"triangle in case {case_idx}")
            triangle_count += 1
            idx += 1
        actual_triangles.append(triangle_count)

        if idx >= len(lines) or not is_integer_token(lines[idx]):
            raise ValueError("unexpected end of solver output")

        guard_count = int(lines[idx])
        idx += 1
        for _ in range(guard_count):
            if idx >= len(lines):
                raise ValueError("unexpected end of solver output")
            parse_float_list(lines[idx], 2, f"guard in case {case_idx}")
            idx += 1

    return OutputSummary(
        actual_triangles=actual_triangles,
        trailing_tokens=len(lines) - idx,
    )


def build_solver(skip_build: bool) -> None:
    if skip_build:
        return

    subprocess.run(["make"], cwd=ROOT, check=True)


def run_solver(input_path: Path) -> str:
    input_text = input_path.read_text()
    completed = subprocess.run(
        [str(SOLVER)],
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout


def check_file(path: Path) -> bool:
    summary = parse_input_file(path)
    output = parse_solver_output(run_solver(path), summary.expected_triangles)

    print(path)
    passed = True

    for case_idx, (actual, expected) in enumerate(
        zip(output.actual_triangles, summary.expected_triangles), start=1
    ):
        status = "OK" if actual == expected else "FAIL"
        print(f"  case {case_idx}: expected {expected}, got {actual} [{status}]")
        if actual != expected:
            passed = False

    if summary.trailing_tokens > 0:
        print(f"  warning: ignored {summary.trailing_tokens} trailing input tokens")
    if output.trailing_tokens > 0:
        print(f"  warning: ignored {output.trailing_tokens} trailing output tokens")

    return passed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the solver on one or more testcase files and verify triangle counts."
    )
    parser.add_argument("inputs", nargs="+", help="assignment-format input file(s) to check")
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="do not run make before checking",
    )
    args = parser.parse_args()

    try:
        build_solver(skip_build=args.skip_build)
    except subprocess.CalledProcessError as exc:
        print(f"build failed with exit code {exc.returncode}", file=sys.stderr)
        return 2

    all_passed = True

    for input_name in args.inputs:
        input_path = Path(input_name)
        if not input_path.is_absolute():
            input_path = ROOT / input_path

        try:
            passed = check_file(input_path)
        except FileNotFoundError:
            print(f"{input_path}: file not found", file=sys.stderr)
            return 2
        except ValueError as exc:
            print(f"{input_path}: parse error: {exc}", file=sys.stderr)
            return 2
        except subprocess.CalledProcessError as exc:
            print(f"{input_path}: solver failed with exit code {exc.returncode}", file=sys.stderr)
            if exc.stderr:
                print(exc.stderr, file=sys.stderr, end="")
            return 2

        all_passed = all_passed and passed

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

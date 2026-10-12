#!/usr/bin/env python3
"""Run repository checks without requiring pytest."""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
import sys
import traceback


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    failures: list[str] = []
    total = 0
    for path in sorted((PROJECT_ROOT / "tests").glob("test_*.py")):
        module = load_module(path)
        for name, function in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("test_") or function.__module__ != module.__name__:
                continue
            total += 1
            try:
                function()
                print(f"PASS {path.name}::{name}")
            except Exception:
                failures.append(f"{path.name}::{name}")
                traceback.print_exc()
    print(f"\n{total - len(failures)}/{total} checks passed")
    if failures:
        print("Failed: " + ", ".join(failures))
        raise SystemExit(1)


if __name__ == "__main__":
    main()

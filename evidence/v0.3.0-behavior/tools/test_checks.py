"""Count the checks of every retained test function in 0.2.0 and 0.3.0.

test_checks.py --base DIR --repo DIR > test-checks.txt

DIR for --base is an export of the 0.2.0 source commit (git archive d086973);
--repo is the 0.3.0 checkout. A check is an assert statement or a call of
pytest.raises, pytest.warns or pytest.fail. test_file_map.json maps each 0.2.0
test file to its 0.3.0 path. The output lists every function with fewer checks,
every function that is no longer present and the number of new functions.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

MAP = json.loads(Path(__file__).with_name("test_file_map.json").read_text())


def checks(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}

    def visit(node: ast.AST, prefix: str = "") -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                visit(child, prefix + child.name + ".")
            elif isinstance(
                child, ast.FunctionDef | ast.AsyncFunctionDef
            ) and child.name.startswith("test"):
                count = 0
                for sub in ast.walk(child):
                    if isinstance(sub, ast.Assert):
                        count += 1
                    elif isinstance(sub, ast.Call):
                        func = sub.func
                        name = (
                            func.attr
                            if isinstance(func, ast.Attribute)
                            else getattr(func, "id", "")
                        )
                        count += name in ("raises", "warns", "fail")
                out[prefix + child.name] = count

    visit(ast.parse(path.read_text(encoding="utf-8")))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    fewer, missing, new = [], [], 0
    for old, current in sorted(MAP.items()):
        before, after = checks(args.base / old), checks(args.repo / current)
        for name, count in before.items():
            if name not in after:
                missing.append(f"{current}::{name}")
            elif after[name] < count:
                fewer.append(f"{current}::{name}: {count} -> {after[name]}")
        new += sum(name not in before for name in after)
    print(f"test files compared: {len(MAP)}")
    print(f"functions with fewer checks: {len(fewer)}")
    print("\n".join(f"  {line}" for line in fewer))
    print(f"functions no longer present: {len(missing)}")
    print("\n".join(f"  {line}" for line in missing))
    print(f"new functions: {new}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

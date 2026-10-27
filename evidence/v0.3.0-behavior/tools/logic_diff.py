"""Compare the audit-runtime logic of 0.2.0 and 0.3.0 module by module.

logic_diff.py --base DIR --repo DIR > logic-diff.txt

Imports and docstrings are removed from both syntax trees; the rest is
unparsed and compared. module_map.json maps each 0.2.0 module to its 0.3.0
path. The output lists every module whose remaining code differs, with the
changed lines.
"""

from __future__ import annotations

import argparse
import ast
import difflib
import json
from pathlib import Path

MAP = json.loads(Path(__file__).with_name("module_map.json").read_text())


class Strip(ast.NodeTransformer):
    def visit_Import(self, node: ast.Import) -> None:
        return None

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        return None

    def _body(self, node):
        self.generic_visit(node)
        first = node.body[0] if node.body else None
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
            if isinstance(first.value.value, str):
                node.body = node.body[1:] or [ast.Pass()]
        return node

    visit_Module = visit_ClassDef = visit_FunctionDef = visit_AsyncFunctionDef = _body


def logic(path: Path) -> list[str]:
    tree = Strip().visit(ast.parse(path.read_text(encoding="utf-8")))
    return ast.unparse(tree).splitlines()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    identical = 0
    for old, new in sorted(MAP.items()):
        before, after = logic(args.base / old), logic(args.repo / new)
        if before == after:
            identical += 1
            continue
        changed = [
            line
            for line in difflib.unified_diff(before, after, lineterm="", n=0)
            if line[:1] in "+-" and line[:3] not in ("+++", "---")
        ]
        print(f"== {old} -> {new}: {len(changed)} changed lines")
        print("\n".join(f"   {line}" for line in changed))
    print(f"modules with identical logic: {identical} of {len(MAP)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

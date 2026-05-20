"""Lint: measurements are framework-blind.

Every file under ccdr/data/ (loaders, estimators, common helpers — but
NOT data/tests/) must not import `ccdr.core.parameters` or anything from
`ccdr.derivations`.

See CLAUDE.md §7 constraint 4.
"""
import ast
import pathlib

import ccdr.data

FORBIDDEN_IMPORTS = ("ccdr.core.parameters", "ccdr.derivations")


def test_no_framework_imports_in_measurements():
    data_root = pathlib.Path(ccdr.data.__file__).parent
    py_files = sorted(p for p in data_root.rglob("*.py") if "tests" not in p.parts)
    for py_file in py_files:
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            module = None
            names: list = []
            if isinstance(node, ast.ImportFrom):
                module = node.module
                names = [a.name for a in node.names]
            elif isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            for n in [module] + names:
                if not n:
                    continue
                for forbidden in FORBIDDEN_IMPORTS:
                    if n == forbidden or n.startswith(forbidden + "."):
                        raise AssertionError(
                            f"{py_file}: forbidden import of {n}. "
                            f"Measurements are framework-blind. "
                            f"See CLAUDE.md §7 constraint 4."
                        )

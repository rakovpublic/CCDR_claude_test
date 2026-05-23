"""Lint: dataset loaders are framework-blind (CLAUDE_op11_nu.md §11 #3).

datasets/*.py must not import from ccdr.derivations or ccdr.core.parameters.
The likelihoods compute chi2(nu) from a *passed-in* nu; they never read the
committed value. AST-walk every loader.
"""
import ast
import pathlib

import ccdr.audits.op11_nu.datasets as datasets_pkg

FORBIDDEN_IMPORTS = ("ccdr.derivations", "ccdr.core.parameters")


def test_no_framework_imports_in_loaders():
    root = pathlib.Path(datasets_pkg.__file__).parent
    py_files = sorted(p for p in root.rglob("*.py") if "tests" not in p.parts)
    assert py_files, "no dataset loaders found"
    for py_file in py_files:
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.ImportFrom):
                names = [node.module] + [a.name for a in node.names]
            elif isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            for n in names:
                if not n:
                    continue
                for forbidden in FORBIDDEN_IMPORTS:
                    if n == forbidden or n.startswith(forbidden + "."):
                        raise AssertionError(
                            f"{py_file}: forbidden import of {n}. "
                            f"Dataset loaders are framework-blind. "
                            f"See CLAUDE_op11_nu.md §11 constraint 3."
                        )


def test_evaluate_chi2_does_not_read_committed_nu():
    """A loader must not call into the parameters gate (the obvious
    circular-dependency smell). The import ban above already forbids importing
    the module; this also rules out calling _load_nu via any alias."""
    root = pathlib.Path(datasets_pkg.__file__).parent
    for py_file in sorted(root.glob("*.py")):
        tree = ast.parse(py_file.read_text())
        called = {
            (node.func.id if isinstance(node.func, ast.Name)
             else node.func.attr if isinstance(node.func, ast.Attribute) else None)
            for node in ast.walk(tree) if isinstance(node, ast.Call)
        }
        assert "_load_nu" not in called, f"{py_file} calls _load_nu"

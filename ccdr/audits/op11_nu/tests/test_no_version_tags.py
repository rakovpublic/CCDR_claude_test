"""Lint: no version-tagged status strings in the audit (CLAUDE_op11_nu.md §11 #7).

Mirrors the parent project's lint. Diagnostic FUNCTION ids may carry an
`@v\\d+` pre-registration suffix; standalone `_v\\d+` suffixes and the explicit
forbidden tokens are not allowed.
"""
import re
import pkgutil
import importlib

import ccdr.audits.op11_nu as pkg

FORBIDDEN = re.compile(r"_v\d+|_confirm_like|_resolved_like|_committed_v\d+"
                       r"|_ready|_compatible|_schema_backed|borderline")


def _walk_pkg(p):
    yield from pkgutil.walk_packages(p.__path__, p.__name__ + ".")


def test_no_version_tagged_strings():
    for finder, name, ispkg in _walk_pkg(pkg):
        if ".tests" in name:
            continue
        mod = importlib.import_module(name)
        for attr in dir(mod):
            val = getattr(mod, attr, None)
            if not isinstance(val, str):
                continue
            stripped = re.sub(r"@v\d+", "", val)
            if FORBIDDEN.search(stripped):
                raise AssertionError(
                    f"Forbidden version-tagged string in {name}.{attr}: {val!r}\n"
                    f"The OP11 taxonomy is closed. See CLAUDE_op11_nu.md §11."
                )

"""Lint: no version-tagged or _ready/_compatible/_schema_backed strings
inside predictions or derivations. The status taxonomy is closed.
See CLAUDE.md §7.

Note: derivation FUNCTION ids may legitimately carry a `@v\\d+` version
suffix (CLAUDE.md §7 #2 pre-registration). We only catch standalone
`_v\\d+` suffixes that would smuggle a version tag into a status string,
and the explicit forbidden tokens.
"""
import re
import pkgutil
import importlib

import ccdr.predictions
import ccdr.derivations

FORBIDDEN = re.compile(r"_v\d+|_confirm_like|_ready|_compatible|_schema_backed")


def _walk_pkg(pkg):
    yield from pkgutil.walk_packages(pkg.__path__, pkg.__name__ + ".")


def test_no_version_tagged_status_strings():
    for pkg in (ccdr.predictions, ccdr.derivations):
        for finder, name, ispkg in _walk_pkg(pkg):
            if ".tests" in name:
                continue
            mod = importlib.import_module(name)
            for attr in dir(mod):
                val = getattr(mod, attr, None)
                if not isinstance(val, str):
                    continue
                # allow `@v\d+` inside derivation function ids (pre-registration tag)
                stripped = re.sub(r"@v\d+", "", val)
                if FORBIDDEN.search(stripped):
                    raise AssertionError(
                        f"Forbidden version-tagged string in {name}.{attr}: {val!r}\n"
                        f"The status taxonomy is closed. See CLAUDE.md §7."
                    )

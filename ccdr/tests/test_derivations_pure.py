"""Lint: derivation functions are pure.

Every public callable in ccdr.derivations.* (excluding tests/base) must
return a DerivationResult when called with all-None keyword arguments and
must perform no I/O. We monkey-patch `builtins.open` to assert that.

See CLAUDE.md §7 constraint 3.
"""
import importlib
import inspect
import pkgutil
from unittest.mock import patch

import ccdr.derivations
from ccdr.core.status import DerivationResult


def _all_derivation_fns():
    fns = []
    for finder, name, ispkg in pkgutil.walk_packages(
        ccdr.derivations.__path__, "ccdr.derivations.",
    ):
        if ".tests" in name or name.endswith(".base"):
            continue
        mod = importlib.import_module(name)
        for attr in dir(mod):
            if attr.startswith("_"):
                continue
            val = getattr(mod, attr)
            if not callable(val):
                continue
            if getattr(val, "__module__", None) != name:
                continue
            fns.append((name, attr, val))
    return fns


def test_derivations_do_no_io():
    def _refuse_open(*args, **kwargs):
        raise OSError("derivations may not perform I/O (see CLAUDE.md §7 #3)")

    with patch("builtins.open", _refuse_open):
        for mod_name, attr, fn in _all_derivation_fns():
            try:
                sig = inspect.signature(fn)
                kwargs = {p: None for p in sig.parameters}
                # joint_inference.posterior accepts an iterable kwarg; None
                # is a valid sentinel and the function returns PENDING.
                result = fn(**kwargs)
            except OSError as e:
                raise AssertionError(
                    f"{mod_name}.{attr} attempted I/O. Derivations must be pure. "
                    f"See CLAUDE.md §7 constraint 3."
                ) from e
            except TypeError as e:
                raise AssertionError(
                    f"{mod_name}.{attr} does not accept None-defaults. "
                    f"All derivation parameters must be optional. {e}"
                ) from e
            assert isinstance(result, DerivationResult), (
                f"{mod_name}.{attr} did not return DerivationResult (got {type(result)})"
            )

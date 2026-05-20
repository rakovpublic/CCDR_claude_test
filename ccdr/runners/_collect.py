"""Walk the predictions package and collect all prediction modules."""
import importlib
import pkgutil
from types import ModuleType
from typing import List

import ccdr.predictions


def all_prediction_modules() -> List[ModuleType]:
    mods = []
    for finder, name, ispkg in pkgutil.iter_modules(
        ccdr.predictions.__path__, ccdr.predictions.__name__ + ".",
    ):
        if name.endswith(".base") or name.endswith("._tier_b_stub"):
            continue
        mod = importlib.import_module(name)
        if all(hasattr(mod, attr) for attr in ("ID", "derive", "measure", "test")):
            mods.append(mod)
    # stable ordering by ID
    mods.sort(key=lambda m: m.ID)
    return mods

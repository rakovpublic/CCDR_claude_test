"""NANOGrav 15-yr cosmic-string Gμ posterior loader.

The cached file stores log10(Gμ) samples; this loader converts them to
linear Gμ values for `cosmic_string_template_fit`.
"""
from ccdr.data.loaders._common import read_cached_json


def load_15yr():
    data, sha = read_cached_json("nanograv_15yr")
    payload = [10.0 ** float(x) for x in data["rows"]]
    return payload, sha

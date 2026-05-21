"""Neutrinoless double-beta decay (KamLAND-Zen) and KATRIN loaders.

Payload contract for `see_saw_consistency`: iterable of (value, sigma)
pairs in eV.
"""
from ccdr.data.loaders._common import read_cached_json


def _load_rows(name):
    data, sha = read_cached_json(name)
    payload = [(float(v), float(s)) for _name, v, s in data["rows"]]
    return payload, sha


def load_kamland_zen():
    return _load_rows("kamland_zen")


def load_katrin():
    return _load_rows("katrin")

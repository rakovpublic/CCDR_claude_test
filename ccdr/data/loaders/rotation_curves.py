"""Rotation-curve loaders for KMOS3D, SPARC, MaNGA DR17.

Each loader returns (curves, sha) where curves is an iterable of curves,
each curve a list of (r_kpc, v_km_s) tuples.
"""
from ccdr.data.loaders._common import read_cached_json
from ccdr.data.loaders._stub import stub


def _load_curve_collection(name):
    data, sha = read_cached_json(name)
    curves = [[tuple(p) for p in g["rv"]] for g in data["curves"]]
    return curves, sha


def load_kmos3d():
    return _load_curve_collection("kmos3d")


def load_sparc():
    return _load_curve_collection("sparc")


def load_manga():
    return _load_curve_collection("manga_dr17")


# DESI BGS rotation curves are not currently bundled.
load_desi_bgs = stub("desi_bgs", "DESI BGS rotation curves (not yet cached)")

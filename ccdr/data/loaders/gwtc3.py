"""GWTC-3 ringdown loaders.

Payload contracts:
  * `load_high_snr_ringdowns` → iterable of (f_meas_hz, f_kerr_hz) pairs
    for `population_deviation`.
  * `load_ringdowns` → iterable of (mode_id, fractional_residual, sigma)
    triples for `boundary_deformation_residual`.
"""
from ccdr.data.loaders._common import read_cached_json


def load_high_snr_ringdowns():
    data, sha = read_cached_json("gwtc3_ringdowns")
    payload = [(row[1], row[2]) for row in data["rows"]]
    return payload, sha


def load_ringdowns():
    data, sha = read_cached_json("gwtc3_ringdowns")
    payload = []
    for row in data["rows"]:
        event, f_meas, f_kerr, tau_meas, tau_kerr = row
        residual = (f_meas - f_kerr) / f_kerr
        sigma = max(abs(f_kerr) * 0.01, 0.005)
        payload.append((f"qnm220.{event}", residual, sigma))
    return payload, sha

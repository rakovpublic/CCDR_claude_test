"""Tier B + P-A15 + P-D01 data loaders.

Every loader returns (payload, sha) where payload is in the format the
matching estimator expects. Framework-blind by construction.
"""
from ccdr.data.loaders._common import read_cached_json


# --- P-B01 RVM BAO scale shift -------------------------------------------
def load_desi_dr2_bao_shift():
    data, sha = read_cached_json("desi_dr2_bao")
    payload = [(float(v), float(s)) for _name, v, s in data["rows"]]
    return payload, sha


# --- P-B02 Planck NPIPE f_NL bispectrum ----------------------------------
def load_planck_bispectrum():
    data, sha = read_cached_json("planck_bispectrum")
    payload = [(name, float(v), float(s)) for name, v, s in data["rows"]]
    return payload, sha


# --- P-B03 ALICE / CMS η/s -----------------------------------------------
def load_alice_cms_qgp():
    data, sha = read_cached_json("alice_cms_qgp")
    payload = [(name, float(v), float(s)) for name, v, s in data["rows"]]
    return payload, sha


# --- P-B04 NANOGrav δn_GW ------------------------------------------------
def load_nanograv_spectral_index():
    data, sha = read_cached_json("nanograv_spectral_index")
    payload = [(float(v), float(s)) for _name, v, s in data["rows"]]
    return payload, sha


# --- P-B05 NANOGrav × κ correlation --------------------------------------
def load_nanograv_kappa_correlation():
    data, sha = read_cached_json("nanograv_kappa_correlation")
    payload = [(float(v), float(s)) for _name, v, s in data["rows"]]
    return payload, sha


# --- P-B06 fσ_8 compilation ----------------------------------------------
def load_fsigma8():
    data, sha = read_cached_json("fsigma8")
    # Return ratio (measured / ΛCDM) per z bin as a value/sigma pair
    payload = []
    for row in data["rows"]:
        z, fs, sig, fs_lcdm = row
        if fs_lcdm == 0:
            continue
        ratio = fs / fs_lcdm
        ratio_sigma = sig / abs(fs_lcdm)
        payload.append((float(ratio), float(ratio_sigma)))
    return payload, sha


# --- P-B07 ACT DR6 Δκ ----------------------------------------------------
def load_act_dr6_kappa():
    data, sha = read_cached_json("act_dr6_kappa")
    payload = [(float(v), float(s)) for _name, v, s in data["rows"]]
    return payload, sha


# --- P-B08 FIRAS μ, y limits ---------------------------------------------
def load_firas():
    data, sha = read_cached_json("firas")
    payload = {name: (float(v), float(s)) for name, v, s in data["rows"]}
    return payload, sha


# --- P-B09 DESI DR2 density-stratified r_d -------------------------------
def load_desi_density_rd():
    data, sha = read_cached_json("desi_dr2_density_rd")
    payload = [(float(v), float(s)) for _name, v, s in data["rows"]]
    return payload, sha


# --- P-B10 GAIA + DESI MWS phase-space drift -----------------------------
def load_gaia_phase_space():
    data, sha = read_cached_json("gaia_phase_space")
    payload = [(float(v), float(s)) for _name, v, s in data["rows"]]
    return payload, sha


# --- P-B11 ν extraction posterior ----------------------------------------
def load_nu_extraction():
    data, sha = read_cached_json("nu_extraction")
    payload = [(name, float(v), float(s)) for name, v, s in data["rows"]]
    return payload, sha


# --- P-A15 CDT chirality ensemble ----------------------------------------
def load_cdt_chirality_ensemble():
    data, sha = read_cached_json("cdt_chirality_ensemble")
    row = data["rows"][0]
    n4, plus, minus = int(row[0]), int(row[1]), int(row[2])
    payload = {"N_4": n4, "plus": plus, "minus": minus, "total": plus + minus}
    return payload, sha


# --- P-D01 PDG charged-lepton masses -------------------------------------
def load_pdg_lepton_masses():
    data, sha = read_cached_json("pdg_lepton_masses")
    payload = {name: (float(m), float(s)) for name, m, s in data["rows"]}
    return payload, sha

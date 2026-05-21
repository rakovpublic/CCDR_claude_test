"""Koide-Q estimator from PDG charged-lepton masses (P-D01).

Q = (m_e + m_μ + m_τ) / (√m_e + √m_μ + √m_τ)^2
"""
from typing import Mapping, Tuple


def koide_q(masses: Mapping[str, Tuple[float, float]]) -> Tuple[float, float, int]:
    """`masses` maps lepton name → (mass_mev, sigma_mev)."""
    try:
        m_e, s_e = masses["electron"]
        m_mu, s_mu = masses["muon"]
        m_tau, s_tau = masses["tau"]
    except KeyError:
        return (0.0, 0.0, 0)
    num = m_e + m_mu + m_tau
    den_root = m_e ** 0.5 + m_mu ** 0.5 + m_tau ** 0.5
    q = num / (den_root ** 2)
    # propagate the dominant uncertainty (tau)
    sigma_rel = (s_e / m_e) ** 2 + (s_mu / m_mu) ** 2 + (s_tau / m_tau) ** 2
    sigma = q * sigma_rel ** 0.5
    return (q, max(sigma, 1.0e-7), 3)

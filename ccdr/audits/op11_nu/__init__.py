"""OP11 nu-resolution audit.

Diagnoses the documented 500x disagreement between the joint and standalone nu
extractors, then either resolves it or documents a defensible dataset-dependent
choice. Output is op11_report.json, the only file core/parameters.py reads to
gate the NU parameter. See CLAUDE_op11_nu.md for the full specification.
"""

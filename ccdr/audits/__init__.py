"""Pre-prediction audits that gate framework parameters.

Each audit is a self-contained sub-project that diagnoses an Open Problem and
emits a machine-readable report which core/parameters.py consumes to decide
whether a parameter may be committed.
"""

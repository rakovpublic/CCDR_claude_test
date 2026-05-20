"""Frozen status taxonomies and result dataclasses.

This module is the spine of the project. Its enum members and dataclass field
sets are frozen by `tests/test_status_taxonomy_frozen.py`. Do not extend.

See CLAUDE.md §2 and §7.
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class DerivationStatus(Enum):
    DERIVED = "DERIVED"
    PARAMETER_PENDING = "PARAMETER_PENDING"
    DERIVATION_INCOMPLETE = "DERIVATION_INCOMPLETE"
    DERIVATION_FAILED = "DERIVATION_FAILED"


class MeasurementStatus(Enum):
    MEASURED = "MEASURED"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    DATA_QUALITY_FAILED = "DATA_QUALITY_FAILED"
    INSUFFICIENT_STATISTICS = "INSUFFICIENT_STATISTICS"


class TestStatus(Enum):
    CONFIRM = "CONFIRM"
    REJECT = "REJECT"
    INCONCLUSIVE = "INCONCLUSIVE"
    NOT_RUN = "NOT_RUN"
    PARAMETER_PENDING = "PARAMETER_PENDING"


@dataclass(frozen=True)
class DerivationResult:
    status: DerivationStatus
    value: Optional[float] = None
    uncertainty: Optional[float] = None
    provenance: str = ""
    missing_parameters: tuple = ()
    parameters_used: dict = field(default_factory=dict)
    derivation_function_id: str = ""


@dataclass(frozen=True)
class MeasurementResult:
    status: MeasurementStatus
    value: Optional[float] = None
    uncertainty: Optional[float] = None
    data_source: str = ""
    data_sha256: str = ""
    estimator_id: str = ""
    n_samples: int = 0


@dataclass(frozen=True)
class TestResult:
    prediction_id: str
    status: TestStatus
    derivation: DerivationResult
    measurement: MeasurementResult
    test_statistic: Optional[float] = None
    pass_threshold: Optional[float] = None
    parameters_revision: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""

"""ThanosStateMachine: the Infinity Saga as an exploitation state machine.

Offender-side ESM (Thanos's layered stone campaign) + guardian-side
decision tree (the 14,000,605 futures). A zero-sensitivity stress test of
the CaseNoesis exploitation-state-machine formalism.
"""

from .campaign import (
    STRANGE_FUTURES,
    analytic_win_probability,
    build_decision_tree,
    build_machine,
    winning_line,
)
from .machine import Phase, Polarity, StateMachine, Trajectory
from .search import failure_modes, strange_report
from .simulate import rollout, strange_search

__all__ = [
    "STRANGE_FUTURES",
    "analytic_win_probability",
    "build_decision_tree",
    "build_machine",
    "winning_line",
    "Phase",
    "Polarity",
    "StateMachine",
    "Trajectory",
    "failure_modes",
    "strange_report",
    "rollout",
    "strange_search",
    "__version__",
]

__version__ = "0.2.0"

"""ThanosStateMachine: the Infinity Saga as an offense/harm state machine.

Offender-centric campaign trajectory (Thanos's layered stone campaign) +
guardian-side decision tree (the 14,000,605 futures). A zero-sensitivity
stress test of the CaseNoesis exploitation-state-machine formalism —
including where the *exploitation* label stops applying (see
``exploitation``).
"""

from .campaign import (
    STRANGE_FUTURES,
    analytic_win_probability,
    build_decision_tree,
    build_machine,
    winning_line,
)
from .exploitation import (
    BenefitSource,
    campaign_verdict,
    classify_campaign_edges,
    exploitation_predicate,
    exploitation_report,
)
from .machine import Phase, Polarity, StateMachine, Trajectory
from .reward import (
    DEFAULT_MOTIVATION,
    accumulate_rewards,
    build_edge_rewards,
    defender_leverage_notes,
    reward_report,
)
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
    "DEFAULT_MOTIVATION",
    "accumulate_rewards",
    "build_edge_rewards",
    "defender_leverage_notes",
    "reward_report",
    "BenefitSource",
    "campaign_verdict",
    "classify_campaign_edges",
    "exploitation_predicate",
    "exploitation_report",
    "failure_modes",
    "strange_report",
    "rollout",
    "strange_search",
    "__version__",
]

__version__ = "1.2.0"

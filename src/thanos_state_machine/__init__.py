"""ThanosStateMachine: the Infinity Saga as an offense/harm state machine.

Offender-centric campaign trajectory (Thanos's layered stone campaign) +
guardian-side decision tree (the 14,000,605 futures). A zero-sensitivity
stress test of the CaseNoesis exploitation-state-machine formalism —
including where the *exploitation* label stops applying (see
``exploitation``).
"""

from .campaign import (
    STRANGE_FUTURES,
    GuardianAnchor,
    GuardianPolicy,
    analytic_win_probability,
    build_decision_tree,
    build_machine,
    guardian_offender_anchors,
    validate_guardian_anchors,
    winning_line,
)
from .exploitation import (
    BenefitAnatomy,
    BenefitSource,
    InterdictionShape,
    campaign_verdict,
    classify_campaign_edges,
    derive_benefit_source,
    exploitation_predicate,
    exploitation_report,
    guardian_interdiction_shapes,
    trajectory_verdict,
    validate_against_rewards,
    validate_guardian_interdiction_coverage,
)
from .formalism import (
    STONES,
    CampaignState,
    CampaignTrajectory,
    OffenseMachine,
    TupleEdge,
    build_thanos_tuple,
    tuple_report,
)
from .formalism import validate_against_ledger as validate_tuple_against_ledger
from .formalism import validate_against_machine as validate_tuple_against_machine
from .machine import Phase, Polarity, StateMachine, Trajectory
from .reward import (
    DEFAULT_MOTIVATION,
    accumulate_rewards,
    build_edge_rewards,
    defender_leverage_notes,
    reward_report,
    validate_motivation_profile,
)
from .search import (
    absorbing_outcome_count,
    failure_modes,
    interdiction_leverage,
    strange_report,
)
from .simulate import rollout, strange_search

__all__ = [
    "STRANGE_FUTURES",
    "GuardianAnchor",
    "GuardianPolicy",
    "analytic_win_probability",
    "build_decision_tree",
    "build_machine",
    "guardian_offender_anchors",
    "validate_guardian_anchors",
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
    "validate_motivation_profile",
    "BenefitAnatomy",
    "BenefitSource",
    "derive_benefit_source",
    "InterdictionShape",
    "campaign_verdict",
    "classify_campaign_edges",
    "exploitation_predicate",
    "exploitation_report",
    "guardian_interdiction_shapes",
    "trajectory_verdict",
    "validate_against_rewards",
    "validate_guardian_interdiction_coverage",
    "STONES",
    "CampaignState",
    "CampaignTrajectory",
    "OffenseMachine",
    "TupleEdge",
    "build_thanos_tuple",
    "tuple_report",
    "validate_tuple_against_ledger",
    "validate_tuple_against_machine",
    "absorbing_outcome_count",
    "failure_modes",
    "interdiction_leverage",
    "strange_report",
    "rollout",
    "strange_search",
    "__version__",
]

__version__ = "2.1.0"

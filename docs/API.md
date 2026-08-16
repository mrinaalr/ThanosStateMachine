"""Public API (frozen for 1.0.0).

Import from the package root. Anything not listed in ``__all__`` is
internal and may move without a major bump.

```python
from thanos_state_machine import (
    STRANGE_FUTURES,          # 14_000_605
    __version__,
    build_machine,            # offender-side ESM
    build_decision_tree,      # guardian decision nodes (ordered)
    analytic_win_probability, # Fraction; GuardianPolicy.UNIFORM | OPTIMAL
    winning_line,             # [(node, surviving_label), ...]
    GuardianPolicy,           # UNIFORM | OPTIMAL
    GuardianAnchor,           # guardian node ↔ offender machine link
    guardian_offender_anchors,
    validate_guardian_anchors,
    interdiction_leverage,    # per-node reach / loss / continue mass
    absorbing_outcome_count,  # failure modes + win (16)
    failure_modes,            # exact loss masses under uniform play
    strange_report,           # human-readable exact analysis (str)
    strange_search,           # Monte Carlo win count (policy=, seed=)
    rollout,                  # single-future tree walk
    DEFAULT_MOTIVATION,       # goal G + purpose quotes + preference weights
    build_edge_rewards,       # multi-channel R per offender edge
    accumulate_rewards,       # canon-path RewardAccount (accepts motiv=, validate_motiv=)
    validate_motivation_profile,  # enactment must dominate capability
    defender_leverage_notes,  # guardian read of R channels
    reward_report,            # human-readable motivation / R ledger
    BenefitSource,            # victim_sourced | victim_targeted | none
    BenefitAnatomy,           # the 3 facts a classification is derived from
    derive_benefit_source,    # anatomy -> BenefitSource (the stated rule)
    classify_campaign_edges,  # benefit-source per benefit-bearing edge
    exploitation_predicate,   # SEP test: goal benefit victim-sourced?
    trajectory_verdict,       # generic SEP verdict for any annotated path
    campaign_verdict,         # ExploitationVerdict for this campaign
    guardian_interdiction_shapes,  # tree nodes → extraction/enactment/maintenance/remediation
    validate_against_rewards, # parity with build_edge_rewards()
    validate_guardian_interdiction_coverage,
    exploitation_report,      # human-readable boundary analysis
    Phase, Polarity,          # enums
    StateMachine, Trajectory, # ontology-view containers
    # --- the executable tuple (2.1.0) ---
    build_thanos_tuple,       # M = (S, A, T, R_G, s0, F), validated
    OffenseMachine,           # the tuple: transition(), admissible_actions(), ...
    CampaignState,            # s = (position, keyring)
    CampaignTrajectory,       # sigma, with account() and ledger()
    TupleEdge,                # one entry of T, carrying its R_G row
    STONES,                   # X, in canon acquisition order
    tuple_report,             # full spec + the realized run (str)
    validate_tuple_against_machine,  # label parity with build_machine()
    validate_tuple_against_ledger,   # channel parity with accumulate_rewards()
)
```

## CLIs

| command | module |
|---|---|
| `strange-report` | exact DP report to stdout |
| `strange-search` | sample futures (``-n``, ``--seed``, ``--policy``; default seed 42 → 1 win under uniform) |
| `thanos-reward` | motivation + multi-channel reward ledger + defender notes |
| `is-it-exploitation` | SEP source-vs-target boundary test on the campaign |
| `thanos-tuple` | full M = (S, A, T, R_G, s0, F) spec, the realized s0→F run, and the experiments over it |

Also: [docs/DEFENDER_READ.md](DEFENDER_READ.md), [docs/THANOS_PURPOSE.md](THANOS_PURPOSE.md).


## Regenerate derived artifacts

```bash
python scripts/export_mermaid.py   # -> docs/campaign.mermaid
python scripts/export_ttl.py       # -> graphs/thanos_campaign.ttl
python scripts/export_tuple.py     # -> graphs/thanos_tuple.json
pytest                             # includes TTL↔machine and tuple↔ledger parity
```

## Stability promise

- Calibration identity ``P(win|uniform) == 1/STRANGE_FUTURES`` is load-bearing.
- ``Polarity.REMEDIATED`` and layered stone campaigns are part of the public
  model, not experiments.
- ``RewardAccount.goal_attainment`` was added in 1.2.0 *after* ``edges`` and
  defaulted, so 1.0.0-era construction still works.
- **2.0.0 breaking:** ``Phase.EXPLOITATION`` → ``Phase.HARM_EXECUTION``
  (``"ExploitationPhase"`` → ``"HarmExecutionPhase"``). The backbone no longer
  presumes the SEP verdict; ``exploitation.py`` decides it. See ONTOLOGY.md §5.
- ``EdgeBenefit.kind`` is *derived* from ``EdgeBenefit.anatomy``; do not set it
  by hand (``validate_derivation()`` enforces this).
- **2.1.0 additive:** ``formalism`` is a new view, not a replacement.
  ``build_machine()`` stays the ontology twin and the TTL's source of truth;
  ``build_thanos_tuple()`` is the executable one. Their labels and their
  reward totals are kept in parity by test, so neither can drift.
- Tuple ``EdgeReward`` rows are *taken from* ``build_edge_rewards()``, never
  redefined. Two rows are re-attached to the edge that performs the act (the
  exogenous Power grant; the enactment edge into ``SnapEvent``); the totals
  are unchanged and pinned to ``accumulate_rewards()``.
- Defender-side *parameters* stay canon-calibrated fiction; see SECURITY.md.
"""

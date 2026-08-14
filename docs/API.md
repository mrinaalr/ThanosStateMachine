"""Public API (frozen for 1.0.0).

Import from the package root. Anything not listed in ``__all__`` is
internal and may move without a major bump.

```python
from thanos_state_machine import (
    STRANGE_FUTURES,          # 14_000_605
    __version__,
    build_machine,            # offender-side ESM
    build_decision_tree,      # guardian decision nodes (ordered)
    analytic_win_probability, # Fraction; policy in {"uniform","optimal"}
    winning_line,             # [(node, surviving_label), ...]
    failure_modes,            # exact loss masses under uniform play
    strange_report,           # human-readable exact analysis (str)
    strange_search,           # Monte Carlo win count (default n=STRANGE_FUTURES)
    rollout,                  # single-future tree walk
    DEFAULT_MOTIVATION,       # goal G + purpose quotes + preference weights
    build_edge_rewards,       # multi-channel R per offender edge
    accumulate_rewards,       # canon-path RewardAccount (accepts motiv=)
    defender_leverage_notes,  # guardian read of R channels
    reward_report,            # human-readable motivation / R ledger
    BenefitSource,            # victim_sourced | victim_targeted | none
    classify_campaign_edges,  # benefit-source per benefit-bearing edge
    exploitation_predicate,   # SEP test: goal benefit victim-sourced?
    campaign_verdict,         # ExploitationVerdict for this campaign
    exploitation_report,      # human-readable boundary analysis
    Phase, Polarity,          # enums
    StateMachine, Trajectory, # ESM containers
)
```

## CLIs

| command | module |
|---|---|
| `strange-report` | exact DP report to stdout |
| `strange-search` | sample futures (``-n``, ``--seed``; default seed 42 → 1 win) |
| `thanos-reward` | motivation + multi-channel reward ledger + defender notes |
| `is-it-exploitation` | SEP source-vs-target boundary test on the campaign |

Also: [docs/DEFENDER_READ.md](DEFENDER_READ.md), [docs/THANOS_PURPOSE.md](THANOS_PURPOSE.md).


## Regenerate derived artifacts

```bash
python scripts/export_mermaid.py   # -> docs/campaign.mermaid
python scripts/export_ttl.py       # -> graphs/thanos_campaign.ttl
pytest                             # includes TTL↔machine parity
```

## Stability promise

- Calibration identity ``P(win|uniform) == 1/STRANGE_FUTURES`` is load-bearing.
- ``Polarity.REMEDIATED`` and layered stone campaigns are part of the public
  model, not experiments.
- ``RewardAccount.goal_attainment`` was added in 1.2.0 *after* ``edges`` and
  defaulted, so 1.0.0-era construction still works.
- Defender-side *parameters* stay canon-calibrated fiction; see SECURITY.md.
"""

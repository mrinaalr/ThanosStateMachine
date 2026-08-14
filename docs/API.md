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
    Phase, Polarity,          # enums
    StateMachine, Trajectory, # ESM containers
)
```

## CLIs

| command | module |
|---|---|
| `strange-report` | exact DP report to stdout |
| `strange-search` | sample futures (``-n``, ``--seed``; default seed 42 → 1 win) |

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
- Defender-side *parameters* stay canon-calibrated fiction; see SECURITY.md.
"""

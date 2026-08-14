# ThanosStateMachine

The Infinity Saga as an offense/harm state machine: Thanos's stone
campaign modeled as an offender-centric trajectory and the Avengers'
response as a search over the guardian policy space — the 14,000,605
futures, of which exactly one wins.

Canon scope: *Infinity War* + *Endgame*. All probabilities are
calibrated, not measured; the calibration rule and its consequences are
in [docs/FORMALISM.md](docs/FORMALISM.md).

## Why

A zero-sensitivity stress test of the exploitation-state-machine
formalism from an ongoing research program on the mechanics of
technology-mediated exploitation
([context](docs/RESEARCH_CONTEXT.md); [CaseNoesis](https://casenoesis.up.railway.app/);
[*Affordances for Harm*](https://doi.org/10.5281/zenodo.21347781)):
a fully observable fictional "case record" with a canon-provided ground
truth (1 win in 14,000,605) against which the layered-trajectory
vocabulary, the four empirical laws, and kill-chain analysis can be
exercised without touching real victims or real records. Findings that
came out of the exercise are listed at the end of
[docs/FORMALISM.md](docs/FORMALISM.md) and
[docs/ONTOLOGY.md](docs/ONTOLOGY.md) — two of them
(remediation as a third terminal polarity; dynamic affordance
environments) are candidate changes to the real vocabulary.

This repo is also a side project in agentic development: built
end-to-end with frontier agentic tooling, outside my
research obligations, as a low-stakes way to see what these workflows
can do.

## Results

```
P(win | uniform guardian policy) = 1/14,000,605   (exact, by calibration)
P(win | optimal guardian policy) = 324/14,000,605 (~1 in 43,212)
14,000,605 sampled futures (seed 42) -> observed wins: 1
```

Even perfect play leaves the outcome hostage to four coin flips and a
rat with a 1-in-675 chance of stepping on the right button. Strange's
number is a measure over policies, not a prophecy.

## Quickstart

```bash
pip install -e ".[dev]"
strange-report            # exact analysis: win lines, failure modes
strange-search            # 14,000,605 Monte Carlo futures (~10s)
thanos-reward             # motivation + multi-channel R (Gamora / Stark / Garden)
is-it-exploitation        # SEP boundary test: source vs target (verdict: not exploitation)
pytest                    # invariants: calibration, backbone, honesty, TTL parity, reward
```

Version history: [CHANGELOG.md](CHANGELOG.md). Current: **2.0.1**.
Public API: [docs/API.md](docs/API.md). Motive: [docs/THANOS_PURPOSE.md](docs/THANOS_PURPOSE.md).
Defender read: [docs/DEFENDER_READ.md](docs/DEFENDER_READ.md).

## Layout

```
src/thanos_state_machine/
  machine.py     generic ESM primitives (S, A, T, R_G, s0, F; layers)
  campaign.py    the Thanos machine + the guardian decision tree
  search.py      exact DP: probabilities, the winning line, failure modes
  simulate.py    vectorized Monte Carlo over 14,000,605 futures
  reward.py      Thanos motivation + multi-channel R_G
  exploitation.py  SEP predicate: is the victim a source or a target?
graphs/
  thanos_campaign.ttl   CaseNoesis traj: twin (regen: scripts/export_ttl.py)
docs/
  API.md         frozen public surface for 1.0.0
  THANOS_PURPOSE.md  statement of purpose + reward channels (film quotes)
  RESEARCH_CONTEXT.md   what the underlying research is and how this fits
  FORMALISM.md   the model, the calibration, the four laws vs. canon
  ONTOLOGY.md    CASE/UCO fit assessment (spoiler: traj: only, on purpose)
  campaign.mermaid      machine diagram (regen: scripts/export_mermaid.py)
SECURITY.md      dual-use threat model for two-sided (offender+defender) ESMs
CHANGELOG.md     release notes
tests/
```

New here? [docs/RESEARCH_CONTEXT.md](docs/RESEARCH_CONTEXT.md) explains
the research program this project stress-tests.

## Dual-use note

This repo models both an offender *and* a defender, with the offender
reaching the harm state — a different posture from the offender-centric
ESM in the underlying research. [SECURITY.md](SECURITY.md) works through
whether that creates adversarial risk. Short version: the risk lives in
*defender-side parameters*, never in the framework or its structure, and
this repo sits at zero-risk by construction (its defender side is public
canon, its probabilities calibrated not measured, no real entity
modeled). The document extends the utility-asymmetry argument from
*CaseLinker: Scaling Considerations* (Tech Report #3) from aggregation
risk to two-sided-modeling risk, and fixes the publishable-structure /
non-publishable-parameterization boundary as a norm.

## The one line

```
heimdall_bifrost_hulk -> stormbreaker_forged -> confront_thanos
-> trade_time_stone_for_stark -> aim_for_the_chest -> decapitate
-> rat_frees_lang -> canon_assignment -> detour_to_1970
-> gauntlet_kept_moving -> i_am_iron_man
```

The winning trajectory passes *through* the harm state. Denial branches
all lose (Law 4: displacement, not defeat); the only exit is
remediation. That asymmetry — and what it implies for where guardians
should spend interdiction effort — is the actual research content here.

## Relation to the research

Offender-side vocabulary follows the CaseNoesis ESM and its layered
trajectory extension; the elder-fraud instantiation
([elder_scheme.ttl](https://github.com/built-by-mars/CaseNoesis/blob/main/state_machines/graphs/elder_scheme.ttl))
is the structural template. This repo is fiction and makes no claims
about real cases.

MIT license.

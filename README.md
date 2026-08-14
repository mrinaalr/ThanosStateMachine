# ThanosStateMachine

The Infinity Saga as an offense/harm state machine: Thanos's stone
campaign modeled as an offender-centric trajectory and the Avengers'
response as a search over the guardian policy space — the 14,000,605
futures, of which exactly one wins.

Canon: *Infinity War* + *Endgame*. All probabilities are calibrated to
canon, not measured. Fiction; no claims about real cases.

## Results

```
P(win | uniform guardian policy) = 1/14,000,605     (exact, by calibration)
P(win | optimal guardian policy) = 324/14,000,605   (~1 in 43,212)
14,000,605 sampled futures (seed 42) -> observed wins: 1

324 pure guardian policies; exactly 1 is non-null
16 absorbing outcomes; 0 of them avert the Snap
E[named permanent deaths | uniform play] ~= 2.09; the win costs 6
```

Strange's line is not the best policy — it is the only one that is not
measure-zero. Every other policy loses with probability 1. And no future
prevents the Snap: the outcomes are enacted, enacted later by force,
enacted twice, or enacted-and-reversed. The win is remediation, not
prevention.

## Quickstart

```bash
pip install -e ".[dev]"
futures-atlas       # all 16 outcomes: exact mass, world-state, failure kind
strange-report      # exact DP: winning line, interdiction leverage
strange-search      # 14,000,605 Monte Carlo futures (~10s)
thanos-reward       # offender R_G channels + defender read
is-it-exploitation  # SEP source-vs-target test (verdict: not exploitation)
pytest
```

Current: **2.1.0** ([CHANGELOG](CHANGELOG.md)) · API: [docs/API.md](docs/API.md)

## Layout

```
src/thanos_state_machine/
  machine.py       offense/harm primitives (S, A, T, R_G, s0, F; layers)
  campaign.py      the Thanos machine + the guardian decision tree
  futures.py       exact atlas: 16 outcomes, 324 policies, world-states
  search.py        exact DP: probabilities, winning line, leverage
  simulate.py      vectorized Monte Carlo (samples what futures.py enumerates)
  reward.py        offender motivation + multi-channel R_G
  exploitation.py  SEP predicate: is the victim a source or a target?
graphs/thanos_campaign.ttl   CaseNoesis traj: twin (generated)
docs/FORMALISM.md            the model, calibration, four laws, findings
docs/ONTOLOGY.md             CASE/UCO fit assessment
docs/RESEARCH_CONTEXT.md     the research program this stress-tests
docs/API.md                  public surface
SECURITY.md                  dual-use threat model
```

## Why

A zero-sensitivity stress test of the exploitation-state-machine
formalism from research on the mechanics of technology-mediated
exploitation ([context](docs/RESEARCH_CONTEXT.md);
[CaseNoesis](https://casenoesis.up.railway.app/);
[*Affordances for Harm*](https://doi.org/10.5281/zenodo.21347781)): a
fully observable fictional case with canon ground truth, against which
the layered-trajectory vocabulary, the four laws, and kill-chain
analysis can be exercised without touching real victims or records.

Findings that fed back into the research are at the end of
[FORMALISM](docs/FORMALISM.md) and [ONTOLOGY](docs/ONTOLOGY.md) — chiefly
remediation as a third terminal polarity, dynamic affordance
environments, capability ≠ enactment, and "exploitation" as a predicate
over trajectories rather than a name for the machine.

Also a side project in agentic development, built end-to-end with
agentic tooling.

## Dual-use

This models an offender *and* a defender, which the offender-centric ESM
does not. [SECURITY.md](SECURITY.md) works through whether that creates
risk: the answer is that risk lives in defender-side *parameters*, never
in the structure, and this repo is zero-risk by construction — public
canon defender, calibrated-not-measured numbers, no real entity.

MIT license.

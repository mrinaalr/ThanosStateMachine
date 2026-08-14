# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.1] - 2026-08-14

### Fixed

- ``derive_benefit_source`` was listed in ``__all__`` / API but not exported
  from ``__init__.py``.

### Added

- ``GuardianPolicy`` enum (``UNIFORM`` | ``OPTIMAL``) — typed policy surface
  for ``analytic_win_probability``, ``rollout``, and ``strange_search``.
- ``interdiction_leverage()`` — per-node reach / loss / continue mass under a
  guardian policy (FORMALISM §4 contact-primacy argument, now computable).
- ``guardian_offender_anchors()`` + ``validate_guardian_anchors()`` — explicit
  link between guardian tree nodes and offender-machine coordinates.
- ``absorbing_outcome_count()`` — verifies the 16 absorbing outcomes
  (15 failure modes + 1 win).
- ``validate_guardian_interdiction_coverage()`` — every choice node must carry
  an interdiction shape; ``heist_assignment`` tagged ``remediation``.
- Monte Carlo ``--policy optimal`` CLI flag; integer-safe Bernoulli sampling
  (no float threshold drift on chance nodes).
- ``tests/test_public_api.py``, ``tests/test_defender.py``; ruff in CI.

### Changed

- ``strange_report()`` includes interdiction leverage summary; no longer
  recomputes ``failure_modes()`` twice.

## [2.0.0] - 2026-08-14

Major bump: a public enum member was renamed.

### Changed — BREAKING

- `Phase.EXPLOITATION` → **`Phase.HARM_EXECUTION`**, value
  `"ExploitationPhase"` → **`"HarmExecutionPhase"`** (emitted as
  `traj:phaseLabel` in the TTL). Cornish's backbone calls the third
  phase "exploitation" meaning only *the offense is executed*; that
  collides with the SEP sense (victim as *source* of the benefit), and
  the collision made the Snap read as exploitation by construction —
  it occupies the third phase, so it got the label, despite failing the
  SEP test. The backbone is now neutral and the exploitation question
  belongs to the predicate. Proposed upstream; deliberate divergence
  from current CaseNoesis vocabulary, so consumers matching the old
  string will not match these graphs. See ONTOLOGY.md §5.

### Added

- `BenefitAnatomy` + `derive_benefit_source()`: edge classifications are
  now **derived from a stated rule**, not asserted per-edge.
  Extraction = a *preexisting* object changes hands and keeps its value
  without the victim; destruction = the benefit *is* the victim's
  absence. This is what separates the fatal Mind Stone taking
  (extraction) from the Snap (destruction) — lethality does not, since
  both kill.
- `validate_derivation()` guard: every edge must carry an anatomy and
  its `kind` must equal what the rule derives, so a label cannot drift
  from the criterion.
- Derivation shown in `is-it-exploitation` output; truth-table and
  elder-fraud-shape tests (`tests/test_benefit_anatomy.py`).

## [1.2.1] - 2026-08-14

### Added

- `trajectory_verdict()` — generic SEP predicate over any annotated
  trajectory; `campaign_verdict()` is now a thin wrapper.
- `guardian_interdiction_shapes()` — maps Strange's decision nodes to
  extraction / enactment / maintenance interdiction shapes.
- `validate_against_rewards()` — parity check between benefit
  classifications and the reward ledger.
- `validate_motivation_profile()` — guards the enactment-dominates-
  capability invariant; `accumulate_rewards(..., validate_motiv=)`.

### Changed

- `campaign_verdict().rationale` is derived from edge kinds, not hardcoded.
- Power Stone opening edge classified as `BenefitSource.NONE` (exogenous).
- TTL + module docstrings: "completed harm" wording; offense/harm parent
  formalism vs ESM specialization (FORMALISM §5 glossary).
- `docs/DEFENDER_READ.md`: capability ≠ enactment Wakanda window.

## [1.2.0] - 2026-08-14

### Added

- `exploitation.py` — computable SEP boundary predicate (*is the victim a
  **source** of the offender's benefit, or a **target** of its
  elimination?*) plus `is-it-exploitation` CLI. Verdict on this campaign:
  **not an exploitation trajectory** — the goal-realizing edge (the Snap)
  is victim-targeted, though all five stone acquisitions are
  victim-sourced. See FORMALISM §5.
- `goal_attainment` reward channel: capability (`Δprogress`) and
  enactment are now separate facts. A full, unsnapped gauntlet scores
  `progress=1, attainment=0` — the gap is the last window where denial
  prevents rather than reprices. Weighted to strictly dominate any
  capability subtotal.
- Defender leverage note for that window; tests for both additions.

### Changed

- Tagline: "exploitation state machine" → "offense/harm state machine",
  since the SEP test says the campaign is not exploitation.
- `accumulate_rewards(..., motiv=)` now threads preference weights
  through to `RewardAccount.utility` (previously custom weights were
  silently ignored at accumulation).

### Fixed

- SECURITY.md intro attributed "evasion" to the defender's policy space;
  evasion is adversary-side. The search is for defender *success*.

## [1.1.1] - 2026-08-14

### Fixed

- CI: exact `Fraction` stone progress (float `6*(1/6)` failed equality on
  some runners); pytest `--tb=short`, `fail-fast: false`

### Added

- Defender leverage notes + [docs/DEFENDER_READ.md](docs/DEFENDER_READ.md)
  (Strange's policy ↔ Thanos `R_G`; playbook for later similar-shaped threats)

## [1.1.0] - 2026-08-14

### Added

- Multi-channel offender reward `R_G` (`reward.py`): `Δprogress`,
  `personal_cost`, `lock_in`, with preference-weighted utility
- Film-grounded motivation profile + purpose quotes
  ([docs/THANOS_PURPOSE.md](docs/THANOS_PURPOSE.md))
- `thanos-reward` CLI; Gamora / Stark / Garden channel tests

### Changed

- Formalism `R_G` section now describes channels, not a scalar stub
- Version bump 1.0.0 → 1.1.0

## [1.0.0] - 2026-08-14

First stable release of the Infinity-Saga stress test.

### 1.0.0 criteria (met)

- Public API frozen (`__all__` + [docs/API.md](docs/API.md))
- Offender TTL regenerated from `build_machine()` + parity-tested
- CI green on `main`
- SECURITY.md dual-use norm intact
- No orphan actions / no Python↔TTL structural drift
- Version tagged and changelog cut

### Notes

- Same calibrated identities as 0.3.0: `P(win|uniform) = 1/14,000,605`,
  `P(win|optimal) = 324/14,000,605`, seed 42 → one observed win.
- Research findings (`remediated`, dynamic affordances / `unlockedBy`,
  composite backbone) are part of the shipped model, not drafts.

## [0.3.0] - 2026-08-14

### Added

- [docs/API.md](docs/API.md) — frozen public surface
- `scripts/export_ttl.py` — regenerate `graphs/thanos_campaign.ttl` from
  `build_machine()`, including proposed `tsm:unlockedBy` links
- Exporter round-trip + `unlockedBy` tests
- Contact-phase failure-mass invariant (`2/3` die at first choice under
  uniform play)

### Changed

- Campaign TTL is now generated (hand commentary preserved via exporter
  overlays); version bump 0.2.0 → 0.3.0

## [0.2.0] - 2026-08-14

### Added

- This changelog and an explicit slow path to 1.0.0
- GitHub Actions CI (`pytest` on push/PR)
- TTL↔Python structural parity test
- Action-coverage invariant (every declared action labels ≥1 transition)
- Exact optimal-win probability check (`324/14,000,605`)
- Composite layered-backbone test (Law 2 finding)
- `py.typed` marker for typed consumers

### Fixed

- Wired `a_black_order` onto delegated-acquisition edges (Statesman boarding,
  Wakanda assault); it was declared in code and TTL but unused
- Aligned `graphs/thanos_campaign.ttl` transitions with `build_machine()`
- Dropped unused imports in `campaign.py`, `search.py`, `simulate.py`

### Changed

- Version bump 0.1.1 → 0.2.0

## [0.1.1] - 2026-08-13

### Added

- `SECURITY.md` dual-use threat model for two-sided ESMs
- `docs/RESEARCH_CONTEXT.md` and README wiring to the public research stack

## [0.1.0] - 2026-08-13

### Added

- Offender-side layered ESM (`machine.py`, `campaign.py`)
- Guardian decision tree + exact analysis (`search.py`)
- Monte Carlo Strange search (`simulate.py`)
- Calibration to `P(win|uniform) = 1/14,000,605`
- `graphs/thanos_campaign.ttl`, formalism/ontology docs, mermaid export
- Invariant tests

[Unreleased]: https://github.com/mrinaalr/ThanosStateMachine/compare/v2.0.1...HEAD
[2.0.1]: https://github.com/mrinaalr/ThanosStateMachine/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/mrinaalr/ThanosStateMachine/compare/v1.2.1...v2.0.0
[1.2.1]: https://github.com/mrinaalr/ThanosStateMachine/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/mrinaalr/ThanosStateMachine/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/mrinaalr/ThanosStateMachine/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/mrinaalr/ThanosStateMachine/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/mrinaalr/ThanosStateMachine/compare/v0.3.0...v1.0.0
[0.3.0]: https://github.com/mrinaalr/ThanosStateMachine/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mrinaalr/ThanosStateMachine/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/mrinaalr/ThanosStateMachine/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/mrinaalr/ThanosStateMachine/releases/tag/v0.1.0

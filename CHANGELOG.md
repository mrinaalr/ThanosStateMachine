# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Toward 1.0.0

Ship 1.0.0 when these hold — not before:

- [ ] Public API frozen (`__all__` + short API note in README)
- [ ] Offender TTL regenerated from `build_machine()` (or parity-tested) on every release
- [ ] CI green on `main` (unit + calibration + seed-42 search)
- [ ] SECURITY.md dual-use norm unchanged and still accurate
- [ ] No orphan actions / no Python↔TTL structural drift
- [ ] Version tagged and changelog cut

Out of scope for 1.0.0 (research follow-ons, not repo blockers):

- Upstreaming `remediated` / `unlockedBy` into CaseNoesis
- CASE/UCO imports (deliberately excluded; see docs/ONTOLOGY.md)
- Real defender-side parameterization

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

[Unreleased]: https://github.com/mrinaalr/ThanosStateMachine/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/mrinaalr/ThanosStateMachine/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/mrinaalr/ThanosStateMachine/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/mrinaalr/ThanosStateMachine/releases/tag/v0.1.0

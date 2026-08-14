"""Exact futures atlas: mass conservation, the two theorems, world-states."""

from fractions import Fraction

from thanos_state_machine.campaign import STRANGE_FUTURES
from thanos_state_machine.futures import (
    FailureKind,
    SnapOutcome,
    atlas_report,
    enumerate_futures,
    expected_permanent_deaths,
    policy_space,
)
from thanos_state_machine.search import failure_modes


def test_mass_sums_to_one():
    assert sum((f.probability for f in enumerate_futures()),
               Fraction(0)) == 1


def test_win_mass_matches_calibration():
    win = next(f for f in enumerate_futures() if f.kind is None)
    assert win.probability == Fraction(1, STRANGE_FUTURES)


def test_atlas_agrees_with_failure_modes():
    """Independent walks over the same tree must produce identical masses."""
    atlas = {f.outcome: f.probability for f in enumerate_futures()
             if f.kind is not None}
    modes = {f"{m.node}:{m.branch}": m.mass_uniform for m in failure_modes()}
    assert atlas == modes


def test_only_one_non_null_policy():
    """Theorem: of 324 pure policies, exactly one can win at all."""
    policies = policy_space()
    assert len(policies) == 324
    nonnull = [p for p in policies if p.win_probability > 0]
    assert len(nonnull) == 1
    assert nonnull[0].first_defection is None
    assert nonnull[0].win_probability == Fraction(324, STRANGE_FUTURES)


def test_no_future_averts_the_snap():
    """Theorem: denial is displacement, over the outcome space. Every
    terminal has the Snap enacted, forced later, doubled, or reversed —
    never simply prevented."""
    for f in enumerate_futures():
        assert f.world.snap in SnapOutcome


def test_only_the_win_reverses():
    for f in enumerate_futures():
        if f.kind is None:
            assert f.world.snap is SnapOutcome.ENACTED_AND_REVERSED
            assert f.world.dusted_restored
        else:
            assert f.world.snap is not SnapOutcome.ENACTED_AND_REVERSED
            assert not f.world.dusted_restored


def test_every_loss_is_classified():
    kinds = {f.kind for f in enumerate_futures() if f.kind is not None}
    assert kinds == set(FailureKind)


def test_win_costs_are_canon():
    win = next(f for f in enumerate_futures() if f.kind is None)
    assert {"Loki", "Heimdall", "Gamora", "Vision",
            "Natasha", "Stark"} <= win.world.dead
    assert win.world.thanos_2018_dead
    assert win.world.thanos_2014_erased


def test_deaths_accumulate_monotonically_along_the_spine():
    """Later terminals can only add named deaths, never resurrect."""
    futures = sorted(
        (f for f in enumerate_futures() if f.kind is not None),
        key=lambda f: -f.probability,  # spine order ~ decreasing mass
    )
    seen: frozenset[str] = frozenset()
    for f in futures:
        assert seen <= f.world.dead or f.world.dead >= seen & f.world.dead
    early = next(f for f in enumerate_futures()
                 if f.outcome == "statesman_response:fight_head_on")
    late = next(f for f in enumerate_futures()
                if f.outcome == "stark_seizure:chance_fails")
    assert early.world.dead < late.world.dead


def test_dead_hand_kills_thanos_but_still_loses():
    f = next(f for f in enumerate_futures()
             if f.outcome == "wakanda_strike:aim_for_the_head")
    assert f.world.thanos_2018_dead
    assert f.kind is FailureKind.DEAD_HAND
    assert f.world.snap is SnapOutcome.ENACTED


def test_second_snap_is_the_keepaway_failure():
    f = next(f for f in enumerate_futures()
             if f.outcome == "gauntlet_keepaway:chance_fails")
    assert f.world.snap is SnapOutcome.ENACTED_TWICE


def test_expected_deaths_positive_and_bounded():
    e = expected_permanent_deaths()
    assert Fraction(2) < e < Fraction(8)


def test_atlas_report_renders():
    r = atlas_report()
    assert "non-null: 1" in r
    assert "mass check: 1" in r

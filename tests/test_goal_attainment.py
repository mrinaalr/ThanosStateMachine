"""Capability != enactment: the goal_attainment channel."""

from fractions import Fraction

from thanos_state_machine.reward import (
    DEFAULT_MOTIVATION,
    MotivationProfile,
    ThanosGoal,
    THANOS_PURPOSE_QUOTES,
    accumulate_rewards,
    build_edge_rewards,
    canon_offender_path,
)

SNAP_EDGE = ("SnapEvent", "GardenWithdrawal")


def test_attainment_books_only_at_the_snap():
    rewards = build_edge_rewards()
    for key, e in rewards.items():
        if key == SNAP_EDGE:
            assert e.goal_attainment == Fraction(1)
        else:
            assert e.goal_attainment == Fraction(0)


def test_full_gauntlet_without_snap_is_not_the_goal():
    """Stop the walk one edge before the Snap: progress is already 1,
    attainment is 0. Capability-complete != harm-enacted."""
    path = canon_offender_path()
    pre_snap = path[: path.index(SNAP_EDGE)]
    acct = accumulate_rewards(pre_snap)
    assert acct.progress == Fraction(1)
    assert acct.goal_attainment == Fraction(0)


def test_snap_dominates_gauntlet():
    """Enactment strictly outranks any capability subtotal:
    w_goal * 1 > w_progress * total_progress."""
    m = DEFAULT_MOTIVATION
    assert m.w_goal_attainment * Fraction(1) > m.w_progress * Fraction(1)
    rewards = build_edge_rewards()
    snap_u = rewards[SNAP_EDGE].utility()
    capability_u = sum(
        (e.utility() for k, e in rewards.items() if k != SNAP_EDGE),
        Fraction(0),
    )
    assert snap_u > capability_u


def test_motivation_threads_through_accumulation():
    """Custom weights actually change priced utility (the old API
    silently ignored them)."""
    default_u = accumulate_rewards().utility
    heavy_grief = MotivationProfile(
        goal=ThanosGoal(),
        quotes=THANOS_PURPOSE_QUOTES,
        w_personal_cost=Fraction(3),
    )
    grief_u = accumulate_rewards(motiv=heavy_grief).utility
    assert grief_u != default_u
    assert grief_u < default_u  # heavier grief weight lowers the total


def test_full_path_utility_still_positive():
    assert accumulate_rewards().utility > 0

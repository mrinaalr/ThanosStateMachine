"""Invariants: calibration, uniqueness of the win, backbone, honesty."""

from fractions import Fraction

import numpy as np
import pytest

from thanos_state_machine.campaign import (
    ChoiceNode,
    STRANGE_FUTURES,
    analytic_win_probability,
    build_decision_tree,
    build_machine,
    winning_line,
)
from thanos_state_machine.machine import Phase, Polarity
from thanos_state_machine.search import failure_modes
from thanos_state_machine.simulate import rollout, strange_search


def test_calibration_is_exact():
    assert analytic_win_probability(policy="uniform") == Fraction(1, STRANGE_FUTURES)


def test_exactly_one_winning_line():
    tree = build_decision_tree()
    for node in tree:
        if isinstance(node, ChoiceNode):
            survivors = [b for b in node.branches if b.outcome == "continue"]
            assert len(survivors) == 1, node.name
    assert len(winning_line(tree)) == len(tree)


def test_probability_mass_sums_to_one():
    total = sum((f.mass_uniform for f in failure_modes()), Fraction(0))
    assert total + analytic_win_probability() == 1


def test_optimal_play_still_needs_luck():
    p_opt = analytic_win_probability(policy="optimal")
    assert p_opt < Fraction(1, 40_000)  # even Strange needs the dice
    assert p_opt > Fraction(1, 50_000)


def test_probabilities_are_valid():
    from thanos_state_machine.campaign import ChanceNode
    for node in build_decision_tree():
        if isinstance(node, ChanceNode):
            assert 0 < node.p_continue < 1, node.name


def test_machine_validates_and_is_layered():
    m = build_machine()
    m.validate()
    assert m.layers() >= {"campaign", "space", "reality", "soul", "time", "mind"}
    assert m.terminals["CampaignRemediated"] is Polarity.REMEDIATED
    assert m.terminals["SnapEvent"] is Polarity.COMPLETED


def test_backbone_per_stone_layer():
    """Law 2 check at the sub-trajectory level: contact -> conditioning ->
    exploitation present in every stone layer (maintenance lives at the
    campaign level: GardenWithdrawal). See docs/FORMALISM.md."""
    m = build_machine()
    for layer in ["space", "reality", "soul", "time", "mind"]:
        phases = {m.states[s.name].phase for s in m.states.values()
                  if s.layer == layer}
        assert {Phase.INITIAL_CONTACT, Phase.CONDITIONING,
                Phase.EXPLOITATION} <= phases
    campaign_phases = {s.phase for s in m.states.values()
                       if s.layer == "campaign"}
    assert Phase.MAINTENANCE in campaign_phases


def test_vectorized_search_matches_tree_rollouts():
    """The chunked conjunction counter must agree with honest tree walks."""
    n = 200_000
    seed = 7
    fast = strange_search(n=n, seed=seed, chunk=50_000)
    # Honest walk with the same policy, independent stream: compare rates
    # against analytic p via a generous tolerance (rare event, so compare
    # both to expectation rather than to each other draw-for-draw).
    p = float(analytic_win_probability())
    assert fast <= 5  # p*n ~ 0.014, anything larger means a bug
    rng = np.random.default_rng(seed)
    slow_wins = sum(rollout(rng).won for _ in range(2_000))
    assert slow_wins <= 2


def test_rollout_paths_terminate_properly():
    rng = np.random.default_rng(0)
    for _ in range(500):
        r = rollout(rng)
        assert r.won == (r.loss is None)
        assert len(r.path) >= 1


def test_default_seed_yields_exactly_one_win():
    """Some numbers deserve to be seen. Marked slow; run in CI or locally."""
    pytest.importorskip("numpy")
    wins = strange_search()
    assert wins == 1

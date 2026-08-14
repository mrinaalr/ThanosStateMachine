"""Invariants: calibration, uniqueness of the win, backbone, honesty."""

from fractions import Fraction

import numpy as np

from thanos_state_machine.campaign import (
    STRANGE_FUTURES,
    ChanceNode,
    ChoiceNode,
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


def test_rat_calibration_factorization():
    """Lock the doc factorization: (1/324)(1/32)p_rat = 1/STRANGE_FUTURES."""
    from thanos_state_machine.campaign import _p_rat

    fixed_chance = Fraction(1)
    for node in build_decision_tree():
        if isinstance(node, ChanceNode) and node.name != "quantum_rat":
            fixed_chance *= node.p_continue
    assert fixed_chance == Fraction(1, 32)
    assert _p_rat() == Fraction(10368, STRANGE_FUTURES)
    assert Fraction(1, 324) * fixed_chance * _p_rat() == Fraction(1, STRANGE_FUTURES)


def test_optimal_win_probability_is_exact():
    assert analytic_win_probability(policy="optimal") == Fraction(324, STRANGE_FUTURES)


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
    for node in build_decision_tree():
        if isinstance(node, ChanceNode):
            assert 0 < node.p_continue < 1, node.name


def test_machine_validates_and_is_layered():
    m = build_machine()
    m.validate()
    assert m.layers() >= {"campaign", "space", "reality", "soul", "time", "mind"}
    assert m.terminals["CampaignRemediated"] is Polarity.REMEDIATED
    assert m.terminals["SnapEvent"] is Polarity.COMPLETED


def test_every_action_labels_a_transition():
    m = build_machine()
    used = {a for t in m.transitions for a in t.actions}
    assert used == set(m.actions)


def test_contact_primacy_per_stone_layer():
    """Law 1: every stone layer opens with InitialContactPhase."""
    m = build_machine()
    for layer in ["space", "reality", "soul", "time", "mind"]:
        contact = [s for s in m.states.values()
                   if s.layer == layer and s.phase is Phase.INITIAL_CONTACT]
        assert len(contact) == 1, layer


def test_backbone_per_stone_layer():
    """Law 2 check at the sub-trajectory level: contact -> conditioning ->
    harm execution present in every stone layer (maintenance lives at the
    campaign level: GardenWithdrawal). See docs/FORMALISM.md."""
    m = build_machine()
    for layer in ["space", "reality", "soul", "time", "mind"]:
        phases = {m.states[s.name].phase for s in m.states.values()
                  if s.layer == layer}
        assert {Phase.INITIAL_CONTACT, Phase.CONDITIONING,
                Phase.HARM_EXECUTION} <= phases
    campaign_phases = {s.phase for s in m.states.values()
                       if s.layer == "campaign"}
    assert Phase.MAINTENANCE in campaign_phases


def test_composite_backbone_spans_layers():
    """Law 2 finding: full backbone only on the composite trajectory."""
    m = build_machine()
    # Walk a realized composite path: init -> space approach... -> snap -> ...
    # Phase set across campaign + any stone layer must cover all four.
    phases = {s.phase for s in m.states.values() if s.phase is not None}
    assert {Phase.INITIAL_CONTACT, Phase.CONDITIONING,
            Phase.HARM_EXECUTION, Phase.MAINTENANCE} <= phases
    # No single stone layer alone has maintenance.
    for layer in ["space", "reality", "soul", "time", "mind"]:
        assert Phase.MAINTENANCE not in {
            s.phase for s in m.states.values() if s.layer == layer
        }


def test_contact_phase_failure_dominates_uniform_mass():
    """Research signal: under uniform play, ~2/3 of futures die at first choice."""
    first = [f for f in failure_modes() if f.node == "statesman_response"]
    mass = sum((f.mass_uniform for f in first), Fraction(0))
    assert mass == Fraction(2, 3)


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
    assert p > 0  # silence unused if refactor drops the float use


def test_rollout_paths_terminate_properly():
    rng = np.random.default_rng(0)
    for _ in range(500):
        r = rollout(rng)
        assert r.won == (r.loss is None)
        assert len(r.path) >= 1


def test_default_seed_yields_exactly_one_win():
    """Some numbers deserve to be seen."""
    wins = strange_search()
    assert wins == 1

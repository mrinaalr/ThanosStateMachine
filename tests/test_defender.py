"""Guardian-side model: anchors, leverage, coverage, policy parity."""

from fractions import Fraction

import numpy as np

from thanos_state_machine.campaign import (
    STRANGE_FUTURES,
    GuardianPolicy,
    analytic_win_probability,
    build_decision_tree,
    validate_guardian_anchors,
    winning_line,
)
from thanos_state_machine.exploitation import (
    guardian_interdiction_shapes,
    validate_guardian_interdiction_coverage,
)
from thanos_state_machine.search import (
    absorbing_outcome_count,
    failure_modes,
    interdiction_leverage,
)
from thanos_state_machine.simulate import rollout, strange_search


def test_guardian_anchors_validate_against_machine():
    validate_guardian_anchors()


def test_every_choice_node_has_interdiction_shape():
    validate_guardian_interdiction_coverage()


def test_heist_assignment_interdicts_remediation():
    shapes = {row.node: row.shapes for row in guardian_interdiction_shapes()}
    assert "remediation" in shapes["heist_assignment"]


def test_sixteen_absorbing_outcomes():
    """15 distinct failure modes + 1 win leaf (FORMALISM §2)."""
    assert absorbing_outcome_count() == 16
    assert len(failure_modes()) == 15


def test_interdiction_leverage_mass_conservation_uniform():
    tree = build_decision_tree()
    p_win = analytic_win_probability(tree, GuardianPolicy.UNIFORM)
    total_loss = sum((lev.loss_mass for lev in interdiction_leverage(tree)), Fraction(0))
    assert total_loss + p_win == 1


def test_interdiction_leverage_optimal_has_no_choice_losses():
    for lev in interdiction_leverage(policy=GuardianPolicy.OPTIMAL):
        if lev.node_kind == "choice":
            assert lev.loss_mass == 0


def test_first_node_dominates_uniform_loss_mass():
    first = next(lev for lev in interdiction_leverage()
                 if lev.node == "statesman_response")
    total_loss = sum((lev.loss_mass for lev in interdiction_leverage()), Fraction(0))
    assert first.loss_mass == Fraction(2, 3)
    assert first.loss_mass > total_loss / 2


def test_optimal_monte_carlo_rate_matches_analytic():
    n = 2_000_000
    seed = 11
    wins = strange_search(n=n, seed=seed, policy=GuardianPolicy.OPTIMAL)
    p = float(analytic_win_probability(policy=GuardianPolicy.OPTIMAL))
    expected = p * n
    assert abs(wins - expected) < max(30, expected * 0.15)


def test_uniform_rollout_and_vectorized_agree_in_expectation():
    n = 500_000
    seed = 3
    fast = strange_search(n=n, seed=seed, chunk=100_000)
    p = float(analytic_win_probability())
    assert abs(fast - p * n) < max(5, p * n * 0.5)


def test_optimal_rollout_always_picks_winning_branch():
    rng = np.random.default_rng(0)
    tree = build_decision_tree()
    win_line = dict(winning_line(tree))
    for _ in range(200):
        r = rollout(rng, tree, policy=GuardianPolicy.OPTIMAL)
        if r.won:
            assert dict(r.path) == win_line


def test_optimal_full_search_expects_324_wins():
    p = analytic_win_probability(policy=GuardianPolicy.OPTIMAL)
    assert p == Fraction(324, STRANGE_FUTURES)
    assert float(p) * STRANGE_FUTURES == 324.0

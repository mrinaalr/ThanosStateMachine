"""The tuple has to hold up as a machine, not just as a picture.

Everything here is an integrity claim about M = (S, A, T, R_G, s0, F): T is a
function, A is state-indexed and gated, every state is reachable, the realized
trajectory is an actual walk, and the numbers are the same numbers
``reward.py`` already publishes.
"""

from __future__ import annotations

import json
import random
from fractions import Fraction
from pathlib import Path

import pytest

from thanos_state_machine.campaign import build_machine
from thanos_state_machine.exploitation import BenefitSource
from thanos_state_machine.formalism import (
    GAUNTLET_STAGING,
    STONES,
    CampaignState,
    build_thanos_tuple,
    stone_layers,
    tuple_report,
    validate_against_ledger,
    validate_against_machine,
)
from thanos_state_machine.machine import ActionKind, Polarity
from thanos_state_machine.reward import (
    DEFAULT_MOTIVATION,
    MotivationProfile,
    accumulate_rewards,
)

JSON_PATH = Path(__file__).resolve().parents[1] / "graphs" / "thanos_tuple.json"


@pytest.fixture(scope="module")
def m():
    return build_thanos_tuple()


# ---------------------------------------------------------------------------
# T is a function; the machine is well formed
# ---------------------------------------------------------------------------

def test_validate_passes(m):
    m.validate()


def test_tuple_dimensions_match_the_documented_ones(m):
    """README, FORMALISM §6 and CHANGELOG quote these; pin them."""
    assert (len(m.states), len(m.actions), len(m.edges)) == (54, 22, 57)


def test_the_only_position_the_tuple_adds_is_the_staging_accumulator(m):
    """The tuple must not quietly invent campaign vocabulary. It adds exactly
    one position — the capability accumulator that ``SnapEvent`` was doing
    double duty as — and no others."""
    onto = set(build_machine().states)
    positions = {s.position for s in m.states}
    assert onto <= positions
    assert positions - onto == {GAUNTLET_STAGING}


def test_the_only_actions_the_tuple_adds_are_the_unlabelled_ones(m):
    """Additions exist so every edge carries a label; nothing else."""
    onto = set(build_machine().actions)
    added = set(m.actions) - onto
    assert added == {
        "a_engage", "a_socket", "a_withdraw",
        *(f"a_seek_{lay.stone}" for lay in stone_layers()),
    }
    assert onto <= set(m.actions)


def test_transition_is_a_deterministic_function(m):
    seen = {}
    for e in m.edges:
        key = (e.source, e.action)
        assert key not in seen, f"T({e.source.label}, {e.action}) is multivalued"
        seen[key] = e.target
    for (s, a), target in seen.items():
        assert m.transition(s, a) == target


def test_every_edge_carries_a_known_action(m):
    """The ontology view leaves three socket edges unlabelled; T cannot be a
    function of (s, a) if any edge is unlabelled."""
    for e in m.edges:
        assert e.action in m.actions
        for lb in e.co_labels:
            assert lb in m.actions


def test_transition_undefined_raises(m):
    with pytest.raises(KeyError):
        m.transition(m.initial, "a_snap")


def test_all_states_reachable_from_s0(m):
    assert m.reachable() == set(m.states)


def test_no_orphan_states(m):
    """build_machine() leaves four approach states with no incoming edge.
    The tuple must have none."""
    incoming = {e.target for e in m.edges}
    orphans = [s for s in m.states if s != m.initial and s not in incoming]
    assert orphans == []


def test_ontology_view_orphans_are_the_gap_this_module_closes():
    """Pins the defect that motivates the factoring, so it cannot silently
    change meaning underneath the tuple."""
    onto = build_machine()
    incoming = {t.target for t in onto.transitions}
    orphans = {s for s in onto.states if s != onto.initial and s not in incoming}
    assert orphans == {
        "KnowhereApproach", "VormirApproach", "TitanAmbush", "WakandaAssault",
    }


# ---------------------------------------------------------------------------
# A is state-indexed and gated
# ---------------------------------------------------------------------------

def test_affordance_gating_blocks_unheld_capabilities(m):
    """Every edge in T invokes only affordances already in K."""
    for e in m.edges:
        for lb in e.labels:
            req = m.requires.get(lb)
            if req is not None:
                assert req in e.source.keyring, (
                    f"{e.source.label} -{e.action}-> uses {lb} without {req}"
                )


def test_action_space_grows_along_the_trajectory(m):
    """A(s) is not static — the property FORMALISM §4.2 states in prose."""
    canon = m.canon_trajectory()
    sizes = [len(m.admissible_actions(s)) for s in canon.states]
    assert max(sizes) > min(sizes)

    before = CampaignState(GAUNTLET_STAGING, frozenset({"power"}))
    after = CampaignState(GAUNTLET_STAGING, frozenset({"power", "space"}))
    seekable_before = {a.name for a in m.admissible_actions(before)}
    seekable_after = {a.name for a in m.admissible_actions(after)}
    assert seekable_before == {"a_seek_space"}
    assert seekable_after == {"a_seek_reality", "a_seek_time"}


def test_soul_requires_reality_and_mind_requires_time(m):
    """The two cross-layer affordance dependencies, read off T."""
    reachable_keyrings = {
        s.keyring for s in m.states if s.position == GAUNTLET_STAGING
    }
    for K in reachable_keyrings:
        if "soul" in K:
            assert "reality" in K
        if "mind" in K:
            assert "time" in K


def test_offender_actions_exclude_guardian_interventions(m):
    battle = next(s for s in m.states if s.position == "RemediationBattle")
    assert [a.name for a in m.admissible_actions(battle)] == ["a_counter_snap"]
    assert m.offender_actions(battle) == ()


def test_action_kinds_partition_the_space(m):
    kinds = {a.kind for a in m.actions.values()}
    assert kinds == {
        ActionKind.OFFENDER, ActionKind.AFFORDANCE, ActionKind.INTERVENTION,
    }


# ---------------------------------------------------------------------------
# Parity with the ontology view and the reward ledger
# ---------------------------------------------------------------------------

def test_label_parity_with_ontology_view(m):
    validate_against_machine(m)


def test_every_ontology_label_survives_on_its_edge(m):
    onto = build_machine()
    onto_labels = {(t.source, t.target): set(t.actions) for t in onto.transitions}
    claimed = {e.canon_edge for e in m.edges if e.canon_edge}
    for e in m.edges:
        if e.canon_edge:
            assert onto_labels[e.canon_edge] <= set(e.labels)
    # every rewarded ontology edge is represented
    assert claimed >= {
        (lay.approach, lay.coercion) for lay in stone_layers()
    }


def test_reward_parity_with_ledger(m):
    validate_against_ledger(m)
    acct = m.canon_trajectory().account()
    want = accumulate_rewards()
    assert acct.progress == want.progress == Fraction(1)
    assert acct.personal_cost == want.personal_cost == Fraction(-1)
    assert acct.lock_in == want.lock_in == Fraction(1)
    assert acct.goal_attainment == want.goal_attainment == Fraction(1)
    assert acct.utility == want.utility == Fraction(33, 10)


def test_reward_rows_are_taken_from_the_ledger_not_reinvented(m):
    """No tuple edge may carry a reward the ledger does not publish."""
    from thanos_state_machine.reward import build_edge_rewards

    ledger = build_edge_rewards()
    rewarded = [e for e in m.edges if e.reward is not None]
    assert rewarded, "the tuple carries no rewards at all"
    for e in rewarded:
        assert e.reward == ledger[e.canon_edge]


def test_custom_motivation_reprices_without_moving_channels():
    strict = MotivationProfile(
        goal=DEFAULT_MOTIVATION.goal,
        quotes=DEFAULT_MOTIVATION.quotes,
        w_personal_cost=Fraction(3),
    )
    m = build_thanos_tuple(motivation=strict)
    acct = m.canon_trajectory().account(strict)
    assert acct.personal_cost == Fraction(-1)          # channel unchanged
    assert acct.utility != Fraction(33, 10)            # price changed


# ---------------------------------------------------------------------------
# s0 -> F: the realized trajectory
# ---------------------------------------------------------------------------

def test_canon_trajectory_is_an_actual_walk(m):
    """reward.canon_offender_path() has four discontinuities; a walk has none."""
    canon = m.canon_trajectory()
    for a, b in zip(canon.edges, canon.edges[1:]):
        assert a.target == b.source


def test_canon_trajectory_starts_at_s0_and_ends_in_F(m):
    canon = m.canon_trajectory()
    assert canon.states[0] == m.initial
    assert canon.states[-1] in m.terminals
    assert canon.polarity is Polarity.REMEDIATED


def test_canon_acquisition_order_is_the_film_order(m):
    assert m.canon_trajectory().acquisition_order == STONES


def test_ledger_cumulative_is_monotone_in_progress(m):
    rows = m.canon_trajectory().ledger()
    prog = [r["cumulative"]["progress"] for r in rows]
    assert prog == sorted(prog)
    assert prog[-1] == Fraction(1)


def test_terminal_polarities(m):
    pols = set(m.terminals.values())
    assert pols == {Polarity.COMPLETED, Polarity.REMEDIATED}
    snap = next(s for s, p in m.terminals.items() if p is Polarity.COMPLETED)
    assert m.successors(snap), "SnapEvent is terminal-capable but continues"
    done = next(s for s, p in m.terminals.items() if p is Polarity.REMEDIATED)
    assert m.is_absorbing(done)


def test_walk_replays_the_canon_action_sequence(m):
    canon = m.canon_trajectory()
    assert m.walk(list(canon.actions)).states == canon.states


# ---------------------------------------------------------------------------
# Capability vs enactment, structurally
# ---------------------------------------------------------------------------

def test_exactly_one_goal_realizing_edge(m):
    e = m.goal_realizing_edge()
    assert e.action == "a_snap"
    assert e.source.progress == Fraction(1)


def test_no_attainment_before_full_capability(m):
    for e in m.edges:
        if e.reward is not None and e.reward.goal_attainment > 0:
            assert e.source.keyring == frozenset(STONES)


def test_enactment_window_is_unique_and_unavoidable(m):
    win = m.enactment_window()
    assert len(win) == 1
    (s,) = win
    assert s == CampaignState(GAUNTLET_STAGING, frozenset(STONES))
    assert s.progress == Fraction(1)
    for t in m.trajectories():
        assert s in t.states


def test_snap_edge_outscores_the_entire_capability_subtotal(m):
    snap = m.goal_realizing_edge()
    capability = sum(
        (e.utility() for e in m.canon_trajectory().edges
         if e.reward is not None and e.reward.delta_progress),
        Fraction(0),
    )
    assert snap.utility() > capability


def test_keyring_shrinks_exactly_once_and_it_buys_lock_in(m):
    shrinking = [e for e in m.edges if not e.source.keyring <= e.target.keyring]
    assert len(shrinking) == 1
    (e,) = shrinking
    assert e.action == "a_stone_destruction"
    assert e.reward is not None and e.reward.lock_in == Fraction(1)
    assert e.target.keyring == frozenset()


def test_socket_edges_add_exactly_one_stone(m):
    for e in m.edges:
        if e.action == "a_socket":
            assert len(e.target.keyring - e.source.keyring) == 1


# ---------------------------------------------------------------------------
# Experiments over the tuple
# ---------------------------------------------------------------------------

def test_exactly_six_admissible_acquisition_orders(m):
    orders = {t.acquisition_order for t in m.trajectories()}
    assert len(orders) == 6
    assert STONES in orders
    for o in orders:
        assert o[0] == "power" and o[1] == "space"
        assert o.index("reality") < o.index("soul")
        assert o.index("time") < o.index("mind")


def test_return_is_invariant_across_every_trajectory(m):
    returns = {t.account().utility for t in m.trajectories()}
    assert returns == {Fraction(33, 10)}


def test_necessary_states_cover_the_space_layer_and_the_spine(m):
    labels = {s.label for s in m.necessary_states()}
    assert "StatesmanIntercept[P]" in labels
    assert "LokiCoercion[P]" in labels
    assert "SpaceExtraction[P]" in labels
    assert "GauntletStaging[P+Sp+R+So+T+M]" in labels
    # nothing from a re-orderable layer can be necessary
    assert not any(lbl.startswith("VormirApproach") for lbl in labels)


def test_offender_monte_carlo_has_zero_variance(m):
    rng = random.Random(42)
    orders, returns = set(), set()
    for _ in range(200):
        t = m.sample_trajectory(rng)
        assert t.polarity is Polarity.REMEDIATED
        orders.add(t.acquisition_order)
        returns.add(t.account().utility)
    assert returns == {Fraction(33, 10)}
    assert orders <= {t.acquisition_order for t in m.trajectories()}


# ---------------------------------------------------------------------------
# The predicate applied to the tuple
# ---------------------------------------------------------------------------

def test_predicate_returns_false_on_this_machine(m):
    v = m.verdict()
    assert v.is_exploitation_trajectory is False
    assert v.goal_edge_kind is BenefitSource.VICTIM_TARGETED
    assert len(v.sourced_edges) == 5


def test_predicate_is_not_part_of_the_tuple(m):
    """Nothing in M inspects benefit anatomy — that is FORMALISM §5's claim."""
    assert not hasattr(m, "benefit_source")
    assert m.benefit_of(m.goal_realizing_edge()) is not None
    arrival = next(e for e in m.edges if e.action.startswith("a_seek_"))
    assert m.benefit_of(arrival) is None


# ---------------------------------------------------------------------------
# The shippable artifacts
# ---------------------------------------------------------------------------

def test_export_json_roundtrip_matches_checked_in_graph():
    import sys

    sys.path.insert(0, str(JSON_PATH.parents[1] / "scripts"))
    from export_tuple import to_json  # type: ignore

    assert to_json() == JSON_PATH.read_text()


def test_exported_json_is_complete():
    data = json.loads(JSON_PATH.read_text())
    assert set(data) >= {"S", "A", "T", "R_G", "s0", "F", "canon_trajectory"}
    m = build_thanos_tuple()
    assert len(data["S"]) == len(m.states)
    assert len(data["A"]) == len(m.actions)
    assert len(data["T"]) == len(m.edges)
    assert data["s0"] == m.initial.label


def test_report_covers_every_required_section(m):
    text = tuple_report(m)
    for section in ("S — states", "A — action space", "T — transition function",
                    "R_G — reward", "s0 and F",
                    "s0 -> F — the realized trajectory",
                    "Experiments over the tuple", "The predicate"):
        assert section in text
    assert "EXPLOITATION        : False" in text
    assert "33/10" in text

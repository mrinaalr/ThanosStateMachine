"""Tests for Thanos motivation / multi-channel reward."""

from thanos_state_machine.reward import (
    DEFAULT_MOTIVATION,
    STONE_FRACTION,
    RewardAccount,
    accumulate_rewards,
    build_edge_rewards,
    canon_offender_path,
    validate_rewards_against_machine,
)


def test_rewards_align_with_machine_edges():
    validate_rewards_against_machine()


def test_gamora_hurts_and_advances():
    """Vormir: grief on sacrifice; progress on socket.

    Under default weights the two-edge package is *locally* negative —
    he still takes it because Soul is required for any completing path
    (max progress without Soul is 5/6). Local scalar R alone does not
    explain the beat; path-enablement does.
    """
    r = build_edge_rewards()
    sacrifice = r[("GamoraLeverage", "SoulExtraction")]
    socket = r[("SoulExtraction", "SnapEvent")]
    assert sacrifice.personal_cost < 0
    assert sacrifice.delta_progress == 0.0
    assert socket.delta_progress == STONE_FRACTION
    assert socket.personal_cost == 0.0
    assert sacrifice.utility() < 0
    assert sacrifice.utility() + socket.utility() < 0
    assert accumulate_rewards().utility > 0

    soul = {"VormirApproach", "GamoraLeverage", "SoulExtraction"}
    edges = [
        r[k] for k in canon_offender_path()
        if k[0] not in soul and k[1] not in soul
    ]
    partial = RewardAccount(
        progress=sum(e.delta_progress for e in edges),
        personal_cost=sum(e.personal_cost for e in edges),
        lock_in=sum(e.lock_in for e in edges),
        edges=tuple(edges),
    )
    assert abs(partial.progress - 5 * STONE_FRACTION) < 1e-9
    assert partial.progress < 1.0


def test_stark_spare_is_instrumental_not_competing_goal():
    r = build_edge_rewards()
    bargain = r[("StrangeBargain", "TimeExtraction")]
    assert bargain.personal_cost == 0.0
    assert "Stark" in bargain.beat or "Stark" in bargain.quote
    assert bargain.utility() >= 0


def test_canon_path_reaches_full_progress_and_nonzero_grief():
    acct = accumulate_rewards()
    assert abs(acct.progress - 1.0) < 1e-9
    assert acct.personal_cost == -1.0
    assert acct.lock_in == 1.0
    assert acct.utility > 0  # full path still ranks under destiny
    assert len(acct.edges) == len(canon_offender_path())


def test_goal_statement_is_balance_cull():
    g = DEFAULT_MOTIVATION.goal
    assert "half" in g.statement.lower()
    assert "stone" in g.means.lower()


def test_scalar_collapse_hides_channels_unless_kept():
    """Sanity: total utility alone does not equal personal_cost."""
    acct = accumulate_rewards()
    assert acct.utility != acct.personal_cost
    assert acct.as_dict()["personal_cost"] < 0
    assert acct.as_dict()["progress"] == 1.0

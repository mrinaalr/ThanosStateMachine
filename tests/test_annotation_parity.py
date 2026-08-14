"""Cross-module parity: reward ledger ↔ SEP benefit classifications."""

import pytest
from fractions import Fraction

from thanos_state_machine.exploitation import (
    GOAL_REALIZING_EDGE,
    BenefitSource,
    campaign_verdict,
    classify_campaign_edges,
    guardian_interdiction_shapes,
    trajectory_verdict,
    validate_against_rewards,
)
from thanos_state_machine.reward import (
    MotivationProfile,
    ThanosGoal,
    THANOS_PURPOSE_QUOTES,
    accumulate_rewards,
    build_edge_rewards,
    validate_motivation_profile,
)


def test_benefit_classifications_align_with_rewards():
    validate_against_rewards()


def test_goal_edge_matches_attainment_and_sep_kind():
    rewards = build_edge_rewards()
    edges = classify_campaign_edges()
    assert rewards[GOAL_REALIZING_EDGE].goal_attainment == Fraction(1)
    assert edges[GOAL_REALIZING_EDGE].kind is BenefitSource.VICTIM_TARGETED


def test_extraction_edges_are_victim_sourced_in_both_modules():
    rewards = build_edge_rewards()
    edges = classify_campaign_edges()
    extraction_pairs = {
        ("LokiCoercion", "SpaceExtraction"),
        ("CollectorConcealment", "RealityExtraction"),
        ("GamoraLeverage", "SoulExtraction"),
        ("StrangeBargain", "TimeExtraction"),
        ("DefensePenetration", "MindExtraction"),
    }
    for key in extraction_pairs:
        assert key in edges
        assert edges[key].kind is BenefitSource.VICTIM_SOURCED
        assert key in rewards


def test_power_stone_edge_is_none_not_sourced():
    key = ("CampaignInitiation", "StatesmanIntercept")
    assert classify_campaign_edges()[key].kind is BenefitSource.NONE
    assert build_edge_rewards()[key].delta_progress == Fraction(1, 6)


def test_campaign_verdict_matches_generic_api():
    assert campaign_verdict() == trajectory_verdict(
        GOAL_REALIZING_EDGE, classify_campaign_edges()
    )


def test_wakanda_node_interdicts_enactment():
    shapes = {row.node: row.shapes for row in guardian_interdiction_shapes()}
    assert "enactment" in shapes["wakanda_strike"]
    assert "extraction" in shapes["statesman_response"]


def test_default_motivation_passes_dominance_check():
    validate_motivation_profile(
        MotivationProfile(goal=ThanosGoal(), quotes=THANOS_PURPOSE_QUOTES)
    )


def test_bad_motivation_weights_raise_by_default():
    flat = MotivationProfile(
        goal=ThanosGoal(),
        quotes=THANOS_PURPOSE_QUOTES,
        w_goal_attainment=Fraction(1),
    )
    with pytest.raises(ValueError, match="w_goal_attainment"):
        accumulate_rewards(motiv=flat)


def test_bad_motivation_can_be_opted_out():
    flat = MotivationProfile(
        goal=ThanosGoal(),
        quotes=THANOS_PURPOSE_QUOTES,
        w_goal_attainment=Fraction(1),
    )
    accumulate_rewards(motiv=flat, validate_motiv=False)

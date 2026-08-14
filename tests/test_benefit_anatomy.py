"""The SEP criterion must be DERIVED from anatomy, not asserted.

The hard case is Vision: the Mind Stone taking kills him, and the Snap
kills billions, so "the victim dies" cannot be what separates extraction
from destruction. These tests pin the rule that actually does separate
them, so nobody can quietly relabel an edge later.
"""

import pytest

from thanos_state_machine.exploitation import (
    GOAL_REALIZING_EDGE,
    BenefitAnatomy,
    BenefitSource,
    classify_campaign_edges,
    derive_benefit_source,
    validate_derivation,
)

VISION_EDGE = ("DefensePenetration", "MindExtraction")


def test_every_edge_kind_is_derivable_from_its_anatomy():
    validate_derivation()


def test_all_edges_carry_an_anatomy():
    for key, e in classify_campaign_edges().items():
        assert e.anatomy is not None, key
        assert e.anatomy.rule, key


def test_vision_is_extraction_despite_being_fatal():
    """The taking kills him; it is still extraction, because the stone
    predates him and keeps its value without him."""
    e = classify_campaign_edges()[VISION_EDGE]
    assert e.kind is BenefitSource.VICTIM_SOURCED
    assert e.anatomy.transferred_object == "Mind Stone"
    assert e.anatomy.preexisting is True
    assert e.anatomy.value_survives_victim is True


def test_snap_is_destruction_because_nothing_transfers():
    e = classify_campaign_edges()[GOAL_REALIZING_EDGE]
    assert e.kind is BenefitSource.VICTIM_TARGETED
    assert e.anatomy.transferred_object is None
    assert e.anatomy.preexisting is False
    assert e.anatomy.value_survives_victim is False


def test_lethality_alone_does_not_decide():
    """Both decisive edges are fatal to their victims, yet they derive
    different kinds — so the rule is not tracking lethality."""
    edges = classify_campaign_edges()
    assert edges[VISION_EDGE].kind is not edges[GOAL_REALIZING_EDGE].kind


@pytest.mark.parametrize(
    "obj,preexisting,survives,expected",
    [
        # preexisting thing changes hands, still valuable without B
        ("stolen funds", True, True, BenefitSource.VICTIM_SOURCED),
        # a thing transfers but its value consists in B being gone
        ("victim's absence", True, False, BenefitSource.VICTIM_TARGETED),
        # A conjures the "object" out of the act itself — not extraction
        ("newly minted claim", False, True, BenefitSource.VICTIM_TARGETED),
        # nothing transfers and the benefit needs B gone
        (None, False, False, BenefitSource.VICTIM_TARGETED),
        # nothing transfers, no victim-linked benefit at all
        (None, True, True, BenefitSource.NONE),
    ],
)
def test_derivation_truth_table(obj, preexisting, survives, expected):
    anatomy = BenefitAnatomy(
        transferred_object=obj,
        preexisting=preexisting,
        value_survives_victim=survives,
    )
    assert derive_benefit_source(anatomy) is expected


def test_elder_fraud_shape_derives_as_exploitation():
    """Sanity check on a real-world-shaped case: the victim's money is a
    preexisting thing that changes hands and spends fine without them."""
    anatomy = BenefitAnatomy(
        transferred_object="victim's savings",
        preexisting=True,
        value_survives_victim=True,
        rule="funds predate the scheme and retain value regardless",
    )
    assert derive_benefit_source(anatomy) is BenefitSource.VICTIM_SOURCED

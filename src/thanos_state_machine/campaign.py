"""The Thanos campaign, instantiated two ways.

1. ``build_machine()`` — the offender-side Exploitation State Machine:
   one campaign-level harm trajectory composed of five per-stone offense
   sub-trajectories (layered extension). Ontology-facing; mirrors
   graphs/thanos_campaign.ttl.

2. ``build_decision_tree()`` — the guardian-side decision problem: the
   sequence of choice and chance nodes the Avengers traverse against the
   campaign. This is the object Strange searched. Exactly one leaf is a
   win, and it lies *through* the harm state, not around it.

Canon scope: Infinity War + Endgame only. Probabilities at chance nodes
are calibrated, not measured — see docs/FORMALISM.md ("The load-bearing
rat") for the calibration rule P_uniform(win) = 1/14,000,605.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

from .machine import (
    Action,
    ActionKind,
    Phase,
    Polarity,
    State,
    StateMachine,
    Transition,
)

STRANGE_FUTURES = 14_000_605  # futures seen on Titan; exactly one win


# ---------------------------------------------------------------------------
# 1. Offender-side ESM (layered)
# ---------------------------------------------------------------------------

def build_machine() -> StateMachine:
    m = StateMachine()

    # -- actions & affordances ---------------------------------------------
    # Affordances accumulate: each extraction unlocks a capability that
    # labels later transitions (cf. elder_scheme.ttl where A is static).
    for a in [
        Action("a_fleet", ActionKind.OFFENDER, "Sanctuary II / Outrider armies"),
        Action("a_black_order", ActionKind.OFFENDER, "delegated acquisition (Children of Thanos)"),
        Action("a_hostage_leverage", ActionKind.OFFENDER, "coerce stone-holder via a hostage (Thor->Loki, Tony->Strange, Gamora->Soul)"),
        Action("a_deception", ActionKind.OFFENDER, "staged scene / concealment (Knowhere illusion)"),
        Action("a_sacrifice_rite", ActionKind.OFFENDER, "Vormir exchange: a soul for the Soul Stone"),
        Action("a_power_stone", ActionKind.AFFORDANCE, "acquired pre-s0 (Xandar, exogenous)"),
        Action("a_space_skip", ActionKind.AFFORDANCE, "portal arrival anywhere (Space Stone)"),
        Action("a_reality_warp", ActionKind.AFFORDANCE, "rewrite local reality (Reality Stone)"),
        Action("a_time_reverse", ActionKind.AFFORDANCE, "rewind events (Time Stone)"),
        Action("a_snap", ActionKind.OFFENDER, "terminal harm event: erase half of all life"),
        Action("a_stone_destruction", ActionKind.OFFENDER, "destroy the stones to make the harm irreversible"),
        Action("a_time_heist", ActionKind.INTERVENTION, "guardian remediation: quantum-tunnel retrieval of past stones"),
        Action("a_reverse_snap", ActionKind.INTERVENTION, "Hulk snap: restore the erased"),
        Action("a_counter_snap", ActionKind.INTERVENTION, "Stark snap: erase the 2014 invasion force"),
    ]:
        m.add_action(a)

    # -- campaign layer -----------------------------------------------------
    m.add_state(State("CampaignInitiation", Phase.INITIAL_CONTACT, "campaign"))
    m.add_state(State("SnapEvent", Phase.EXPLOITATION, "campaign"))
    m.add_state(State("GardenWithdrawal", Phase.MAINTENANCE, "campaign"))
    m.add_state(State("RemediationBattle", None, "campaign"))  # guardian-driven
    m.add_state(State("CampaignRemediated", None, "campaign"))
    m.initial = "CampaignInitiation"
    m.terminals["CampaignRemediated"] = Polarity.REMEDIATED
    # SnapEvent is the Completed harm state; the realized 2018 trajectory
    # terminates there with polarity=completed. The realized 2018-2023
    # composite trajectory continues through it. Both are asserted in the
    # TTL; here we mark it terminal-capable.
    m.terminals["SnapEvent"] = Polarity.COMPLETED

    # -- per-stone offense sub-trajectories (layered extension) ------------
    def stone_layer(layer: str, approach: str, coercion: str, extraction: str,
                    approach_actions: tuple[str, ...],
                    coercion_actions: tuple[str, ...],
                    extraction_actions: tuple[str, ...]) -> None:
        m.add_state(State(approach, Phase.INITIAL_CONTACT, layer))
        m.add_state(State(coercion, Phase.CONDITIONING, layer))
        m.add_state(State(extraction, Phase.EXPLOITATION, layer))
        m.add_transition(Transition(approach, coercion, approach_actions))
        m.add_transition(Transition(coercion, extraction, coercion_actions))
        # extraction feeds back into the campaign spine
        m.add_transition(Transition(extraction, "SnapEvent", extraction_actions,
                                    trigger="stone socketed into gauntlet"))

    stone_layer("space", "StatesmanIntercept", "LokiCoercion", "SpaceExtraction",
                ("a_fleet", "a_power_stone"), ("a_hostage_leverage",), ())
    stone_layer("reality", "KnowhereApproach", "CollectorConcealment", "RealityExtraction",
                ("a_space_skip",), ("a_deception",), ())
    stone_layer("soul", "VormirApproach", "GamoraLeverage", "SoulExtraction",
                ("a_space_skip",), ("a_hostage_leverage", "a_reality_warp"),
                ("a_sacrifice_rite",))
    stone_layer("time", "TitanAmbush", "StrangeBargain", "TimeExtraction",
                ("a_space_skip",), ("a_hostage_leverage",), ())
    stone_layer("mind", "WakandaAssault", "DefensePenetration", "MindExtraction",
                ("a_space_skip", "a_fleet"), ("a_fleet",), ("a_time_reverse",))

    m.add_transition(Transition("CampaignInitiation", "StatesmanIntercept",
                                ("a_power_stone",), trigger="Xandar complete (exogenous)"))
    m.add_transition(Transition("SnapEvent", "GardenWithdrawal", ("a_snap",)))
    m.add_transition(Transition("GardenWithdrawal", "RemediationBattle",
                                ("a_stone_destruction", "a_time_heist", "a_reverse_snap"),
                                trigger="guardian remediation, five years later"))
    m.add_transition(Transition("RemediationBattle", "CampaignRemediated",
                                ("a_counter_snap",)))

    m.validate()
    return m


# ---------------------------------------------------------------------------
# 2. Guardian-side decision tree (the object Strange searched)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Branch:
    label: str
    outcome: str  # "continue" (stay on the surviving line) or a loss id
    description: str = ""


@dataclass(frozen=True)
class ChoiceNode:
    name: str
    branches: tuple[Branch, ...]  # uniform over branches under random play

    @property
    def win_branch(self) -> Branch:
        (b,) = [b for b in self.branches if b.outcome == "continue"]
        return b


@dataclass(frozen=True)
class ChanceNode:
    name: str
    p_continue: Fraction
    continue_label: str
    fail_description: str


Node = ChoiceNode | ChanceNode


def _p_rat() -> Fraction:
    """Calibrated so that P_uniform(win) is exactly 1/14,000,605.

    Every other branching and chance weight below is fixed first; the
    quantum rat absorbs the residual. See docs/FORMALISM.md.
    """
    fixed_choices = Fraction(1, 3 * 3 * 3 * 2 * 2 * 3)
    fixed_chance = Fraction(1, 2) * Fraction(1, 2) * Fraction(1, 4) * Fraction(1, 2)
    return Fraction(1, STRANGE_FUTURES) / (fixed_choices * fixed_chance)


def build_decision_tree() -> list[Node]:
    """The surviving line, in order, with every branch off it a loss.

    All denial branches lose: futures where a stone is denied end in
    Thanos regrouping and completing by force (affordance displacement,
    Law 4 — removing a path reprices the trajectory, it does not change
    the goal). The single win passes through the Snap.
    """
    p_rat = _p_rat()
    return [
        ChoiceNode("statesman_response", (
            Branch("heimdall_bifrost_hulk", "continue",
                   "spend the last of the Bifrost sending the warning to Earth"),
            Branch("fight_head_on", "loss_unwarned",
                   "no warning reaches Earth; Vision is found unprepared"),
            Branch("loki_dagger_gambit", "loss_unwarned",
                   "the gambit fails as it did; still no warning"),
        )),
        ChanceNode("nidavellir_forge", Fraction(1, 2), "stormbreaker_forged",
                   "the forge stays cold; no weapon can later confirm the kill"),
        ChoiceNode("knowhere_response", (
            Branch("confront_thanos", "continue",
                   "Gamora is taken - the only route to Vormir that ends in remediation"),
            Branch("ambush_early", "loss_regroup",
                   "ambush fails against the Reality Stone"),
            Branch("evacuate_gamora", "loss_regroup",
                   "Soul Stone denied; Thanos regroups and completes by force"),
        )),
        ChoiceNode("titan_decision", (
            Branch("trade_time_stone_for_stark", "continue",
                   "Strange yields the stone; Stark lives - the winning line requires it"),
            Branch("withhold_stone", "loss_stark_dies",
                   "Thanos kills Stark, takes the stone anyway; no one builds the tunnel"),
            Branch("destroy_time_stone", "loss_regroup",
                   "stone denied; campaign completes by force in a later, darker line"),
        )),
        ChoiceNode("wakanda_strike", (
            Branch("aim_for_the_chest", "continue",
                   "the snap completes cleanly; the board stays winnable"),
            Branch("aim_for_the_head", "loss_dead_hand",
                   "a dying reflex closes the fist; the gauntlet burns with him"),
        )),
        # --- the Snap: the harm state is now reached, on the WINNING line ---
        ChoiceNode("garden_ambush", (
            Branch("decapitate", "continue",
                   "Stormbreaker confirms the stones are destroyed; the five years begin"),
            Branch("spare_and_interrogate", "loss_no_closure",
                   "no confirmation, no closure; the team never re-forms"),
        )),
        ChanceNode("quantum_rat", p_rat, "rat_frees_lang",
                   "the van stays shut; nobody learns the tunnel survived"),
        ChoiceNode("heist_assignment", (
            Branch("canon_assignment", "continue",
                   "2012 NY / 2013 Asgard / 2014 Morag-Vormir"),
            Branch("all_hands_to_2012", "loss_heist",
                   "three stones, one alarmed timeline; the heist collapses"),
            Branch("split_pairs_evenly", "loss_heist",
                   "Vormir undermanned; no soul is exchanged"),
        )),
        ChanceNode("tesseract_recovery", Fraction(1, 2), "detour_to_1970",
                   "the 2012 mishap stands; Pym particles are spent"),
        ChanceNode("gauntlet_keepaway", Fraction(1, 4), "gauntlet_kept_moving",
                   "the second snap is universal"),
        ChanceNode("stark_seizure", Fraction(1, 2), "i_am_iron_man",
                   "the stones stay socketed; the 2014 fleet ends the line"),
    ]


def analytic_win_probability(tree: list[Node] | None = None,
                             policy: str = "uniform") -> Fraction:
    """Exact P(win) under a policy in {"uniform", "optimal"}.

    uniform: guardians pick uniformly at choice nodes (Strange's measure).
    optimal: guardians always pick the surviving branch; only chance
    remains. There is exactly one surviving leaf either way.
    """
    tree = tree if tree is not None else build_decision_tree()
    p = Fraction(1)
    for node in tree:
        if isinstance(node, ChoiceNode):
            if policy == "uniform":
                p *= Fraction(1, len(node.branches))
        else:
            p *= node.p_continue
    return p


def winning_line(tree: list[Node] | None = None) -> list[tuple[str, str]]:
    """(node, surviving-branch-label) pairs — the one future out of 14,000,605."""
    tree = tree if tree is not None else build_decision_tree()
    out = []
    for node in tree:
        if isinstance(node, ChoiceNode):
            out.append((node.name, node.win_branch.label))
        else:
            out.append((node.name, node.continue_label))
    return out

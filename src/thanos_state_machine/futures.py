"""The complete atlas of the 14,000,605 futures — exact, not sampled.

The guardian choice space is finite: 3*3*3*2*2*3 = 324 pure policies.
Chance probabilities are known. So every absorbing future can be
enumerated in closed form with exact probability, a world-state (who is
dead, what happened to the Snap), and a failure classification. The
Monte Carlo in ``simulate.py`` samples from exactly this object.

Two theorems fall out and are pinned in tests:

- **Only-non-null policy:** of the 324 pure guardian policies, exactly
  one has nonzero win probability. Strange's line is not the best
  policy; it is the only one that is not measure-zero.
- **No future averts the Snap:** every terminal outcome has the Snap
  enacted, enacted later by force, enacted twice, or enacted-then-
  reversed. Denial is displacement (Law 4), stated over the outcome
  space instead of asserted.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from itertools import product

from .campaign import ChanceNode, ChoiceNode, build_decision_tree


class FailureKind(str, Enum):
    UNWARNED = "unwarned"                  # no Bifrost warning reaches Earth
    CAPABILITY_GAP = "capability_gap"      # Stormbreaker never forged
    DENIAL_DISPLACEMENT = "denial_displacement"  # stone denied; regroup (Law 4)
    ARCHITECT_LOST = "architect_lost"      # Stark dies; no one builds the tunnel
    DEAD_HAND = "dead_hand"                # kill-strike triggers reflex snap
    NO_CLOSURE = "no_closure"              # no confirmation; team never re-forms
    REMEDIATION_MISSED = "remediation_missed"  # post-Snap recovery path breaks
    SECOND_SNAP = "second_snap"            # 2014 Thanos snaps again, universal
    LAST_EXCHANGE = "last_exchange"        # final battle lost at the seizure


class SnapOutcome(str, Enum):
    ENACTED = "enacted"
    ENACTED_LATER_BY_FORCE = "enacted_later_by_force"
    ENACTED_TWICE = "enacted_twice"
    ENACTED_AND_REVERSED = "enacted_and_reversed"
    # Deliberately no AVERTED member: test_no_future_averts_the_snap
    # proves the outcome space never needs it.


@dataclass(frozen=True)
class WorldState:
    dead: frozenset[str]          # named permanent deaths at this terminal
    snap: SnapOutcome
    dusted_restored: bool
    thanos_2018_dead: bool
    thanos_2014_erased: bool


@dataclass(frozen=True)
class Future:
    """One absorbing outcome of the campaign, with exact uniform mass."""

    outcome: str                  # "win" or "<node>:<branch>"
    node: str
    branch: str
    probability: Fraction         # mass under uniform guardian play
    kind: FailureKind | None      # None for the win
    world: WorldState
    description: str


# Named, canon-fixed dustings of the 2018 Snap (restored only on the win).
DUSTED_2018 = (
    "Strange", "Parker", "Quill", "Drax", "Mantis", "Groot",
    "Barnes", "Wilson", "Maximoff", "T'Challa",
)

# Deaths that occur AT a node's encounter, on every branch of that node.
_NODE_DEATHS: dict[str, frozenset[str]] = {
    "statesman_response": frozenset({"Loki", "Heimdall"}),
    "wakanda_strike": frozenset({"Vision"}),
}

# Deaths that occur upon SURVIVING a node (its continue branch).
_SURVIVAL_DEATHS: dict[str, frozenset[str]] = {
    "knowhere_response": frozenset({"Gamora"}),   # captured -> Vormir
    "heist_assignment": frozenset({"Natasha"}),   # 2014 Vormir toll
    "stark_seizure": frozenset({"Stark"}),        # the counter-snap
}

# Failure classification per loss outcome.
_FAILURE_KIND: dict[tuple[str, str], FailureKind] = {
    ("statesman_response", "fight_head_on"): FailureKind.UNWARNED,
    ("statesman_response", "loki_dagger_gambit"): FailureKind.UNWARNED,
    ("nidavellir_forge", "chance_fails"): FailureKind.CAPABILITY_GAP,
    ("knowhere_response", "ambush_early"): FailureKind.DENIAL_DISPLACEMENT,
    ("knowhere_response", "evacuate_gamora"): FailureKind.DENIAL_DISPLACEMENT,
    ("titan_decision", "withhold_stone"): FailureKind.ARCHITECT_LOST,
    ("titan_decision", "destroy_time_stone"): FailureKind.DENIAL_DISPLACEMENT,
    ("wakanda_strike", "aim_for_the_head"): FailureKind.DEAD_HAND,
    ("garden_ambush", "spare_and_interrogate"): FailureKind.NO_CLOSURE,
    ("quantum_rat", "chance_fails"): FailureKind.REMEDIATION_MISSED,
    ("heist_assignment", "all_hands_to_2012"): FailureKind.REMEDIATION_MISSED,
    ("heist_assignment", "split_pairs_evenly"): FailureKind.REMEDIATION_MISSED,
    ("tesseract_recovery", "chance_fails"): FailureKind.REMEDIATION_MISSED,
    ("gauntlet_keepaway", "chance_fails"): FailureKind.SECOND_SNAP,
    ("stark_seizure", "chance_fails"): FailureKind.LAST_EXCHANGE,
}

# Branch-specific extra deaths on loss branches.
_BRANCH_DEATHS: dict[tuple[str, str], frozenset[str]] = {
    ("titan_decision", "withhold_stone"): frozenset({"Stark"}),
}

# The Snap has happened on-screen once the campaign passes Wakanda.
_POST_WAKANDA = (
    "garden_ambush", "quantum_rat", "heist_assignment",
    "tesseract_recovery", "gauntlet_keepaway", "stark_seizure",
)


def _snap_outcome(node: str, branch: str) -> SnapOutcome:
    if (node, branch) == ("gauntlet_keepaway", "chance_fails"):
        return SnapOutcome.ENACTED_TWICE
    if node == "wakanda_strike" or node in _POST_WAKANDA:
        return SnapOutcome.ENACTED
    return SnapOutcome.ENACTED_LATER_BY_FORCE


def enumerate_futures() -> tuple[Future, ...]:
    """All absorbing outcomes with exact uniform-play mass (sums to 1)."""
    tree = build_decision_tree()
    out: list[Future] = []
    reach = Fraction(1)
    dead: frozenset[str] = frozenset()
    passed_garden = False
    for node in tree:
        node_dead = dead | _NODE_DEATHS.get(node.name, frozenset())
        if isinstance(node, ChoiceNode):
            per = reach * Fraction(1, len(node.branches))
            for b in node.branches:
                if b.outcome == "continue":
                    continue
                key = (node.name, b.label)
                snap = _snap_outcome(*key)
                out.append(Future(
                    outcome=f"{node.name}:{b.label}",
                    node=node.name, branch=b.label, probability=per,
                    kind=_FAILURE_KIND[key],
                    world=WorldState(
                        dead=node_dead | _BRANCH_DEATHS.get(key, frozenset()),
                        snap=snap,
                        dusted_restored=False,
                        thanos_2018_dead=(key == ("wakanda_strike",
                                                  "aim_for_the_head"))
                        or passed_garden,
                        thanos_2014_erased=False,
                    ),
                    description=b.description,
                ))
            reach = per
        else:
            key = (node.name, "chance_fails")
            out.append(Future(
                outcome=f"{node.name}:chance_fails",
                node=node.name, branch="chance_fails",
                probability=reach * (1 - node.p_continue),
                kind=_FAILURE_KIND[key],
                world=WorldState(
                    dead=node_dead, snap=_snap_outcome(*key),
                    dusted_restored=False,
                    thanos_2018_dead=passed_garden,
                    thanos_2014_erased=False,
                ),
                description=node.fail_description,
            ))
            reach *= node.p_continue
        dead = node_dead | _SURVIVAL_DEATHS.get(node.name, frozenset())
        if node.name == "garden_ambush":
            passed_garden = True
    out.append(Future(
        outcome="win", node="stark_seizure", branch="i_am_iron_man",
        probability=reach, kind=None,
        world=WorldState(
            dead=dead, snap=SnapOutcome.ENACTED_AND_REVERSED,
            dusted_restored=True, thanos_2018_dead=True,
            thanos_2014_erased=True,
        ),
        description="the one",
    ))
    return tuple(out)


@dataclass(frozen=True)
class PurePolicy:
    """A deterministic branch choice at every guardian choice node."""

    choices: tuple[tuple[str, str], ...]  # (node, branch label)
    win_probability: Fraction
    first_defection: str | None  # first node whose choice leaves the line


def policy_space() -> tuple[PurePolicy, ...]:
    """All 324 pure guardian policies with exact win probability.

    P(win | pi) = product of chance survivals if pi picks the surviving
    branch at every choice node, else exactly 0 — an off-line choice is
    absorbing whenever reached, and the win requires passing that node.
    """
    tree = build_decision_tree()
    choice_nodes = [n for n in tree if isinstance(n, ChoiceNode)]
    chance = Fraction(1)
    for n in tree:
        if isinstance(n, ChanceNode):
            chance *= n.p_continue
    policies: list[PurePolicy] = []
    for combo in product(*(range(len(n.branches)) for n in choice_nodes)):
        choices = tuple(
            (n.name, n.branches[i].label)
            for n, i in zip(choice_nodes, combo)
        )
        defection = next(
            (n.name for n, i in zip(choice_nodes, combo)
             if n.branches[i].outcome != "continue"),
            None,
        )
        policies.append(PurePolicy(
            choices=choices,
            win_probability=Fraction(0) if defection else chance,
            first_defection=defection,
        ))
    return tuple(policies)


def expected_permanent_deaths() -> Fraction:
    """E[# named permanent deaths] under uniform guardian play."""
    return sum(
        (f.probability * len(f.world.dead) for f in enumerate_futures()),
        Fraction(0),
    )


def atlas_report() -> str:
    futures = enumerate_futures()
    policies = policy_space()
    nonnull = [p for p in policies if p.win_probability > 0]
    total = sum((f.probability for f in futures), Fraction(0))
    win = next(f for f in futures if f.kind is None)

    lines = [
        "FUTURES ATLAS — the 14,000,605, enumerated exactly",
        "=" * 66,
        f"absorbing outcomes: {len(futures)} ({len(futures) - 1} losses + 1 win)",
        f"pure guardian policies: {len(policies)}; non-null: {len(nonnull)}",
        "  -> Strange's line is not the best policy. It is the only one",
        "     that is not measure-zero.",
        f"mass check: {total} (must be 1)",
        f"E[named permanent deaths | uniform play] = "
        f"{expected_permanent_deaths()} "
        f"~= {float(expected_permanent_deaths()):.3f}",
        "",
        "Outcomes by mass (uniform play):",
    ]
    for f in sorted(futures, key=lambda f: -f.probability):
        kind = f.kind.value if f.kind else "WIN"
        deaths = ", ".join(sorted(f.world.dead)) or "-"
        lines.append(f"  {float(f.probability):.6f}  {f.outcome}")
        lines.append(f"      kind={kind}  snap={f.world.snap.value}")
        lines.append(f"      dead: {deaths}")
    lines.append("")
    lines.append("Failure mass by kind:")
    by_kind: dict[FailureKind, Fraction] = {}
    for f in futures:
        if f.kind:
            by_kind[f.kind] = by_kind.get(f.kind, Fraction(0)) + f.probability
    for kind, mass in sorted(by_kind.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {float(mass):.6f}  {kind.value}")
    lines.append("")
    lines.append(
        f"No future averts the Snap. The win ({win.probability}) reverses "
        "it — at the cost of " + ", ".join(sorted(win.world.dead)) + "."
    )
    return "\n".join(lines)


def atlas_report_cli() -> None:
    print(atlas_report())


if __name__ == "__main__":
    atlas_report_cli()

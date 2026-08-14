"""Thanos's motivation and reward: multi-channel R along the campaign.

Public canon only (*Infinity War*, *Endgame*). The point of keeping
channels separate — progress toward the cull vs personal cost vs
instrumental bargains — is that a single scalar erases the Gamora beat:
he advances the goal *and* is wounded. Scalar R can rank the edge; it
cannot narrate why the ranking hurt.

Progress uses ``Fraction`` so six stones sum to exactly 1 on every
platform (float ``6*(1/6)`` failed CI equality checks).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .machine import StateMachine

# ---------------------------------------------------------------------------
# Statement of purpose (film-attributed lines; public dialogue)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PurposeQuote:
    """A line that functions as purpose / motive evidence in the films."""

    text: str
    film: str  # "Infinity War" | "Endgame"
    beat: str  # scene / function


THANOS_PURPOSE_QUOTES: tuple[PurposeQuote, ...] = (
    PurposeQuote(
        "This universe is finite. Its resources, finite. If life is left "
        "unchecked, life will cease to exist. It needs correction.",
        "Infinity War",
        "ideology — scarcity → cull as 'correction'",
    ),
    PurposeQuote(
        "Perfectly balanced, as all things should be.",
        "Infinity War",
        "terminal aesthetic of the goal state",
    ),
    PurposeQuote(
        "Dread it. Run from it. Destiny arrives all the same.",
        "Infinity War",
        "self-as-destiny; motive framed as inevitability",
    ),
    PurposeQuote(
        "The hardest choices require the strongest wills.",
        "Infinity War",
        "will / cost — spoken around the Soul Stone price",
    ),
    PurposeQuote(
        "I ignored my destiny once. I cannot do that again. Even for you. "
        "I'm sorry, Gamora.",
        "Infinity War",
        "Vormir — goal over attachment; grief admitted",
    ),
    PurposeQuote(
        "Today, I lost more than you can know. But now is no time to mourn.",
        "Infinity War",
        "post-Vormir — personal cost logged, campaign continues",
    ),
    PurposeQuote(
        "You have my respect, Stark. When I'm done, half of humanity will "
        "still be alive. I hope they remember you.",
        "Infinity War",
        "Titan — Stark spared as part of the Time Stone bargain",
    ),
    PurposeQuote(
        "I used the stones to destroy the stones. It nearly killed me. "
        "But the work is done. It always will be.",
        "Endgame",
        "Garden — maintenance: lock the completed goal",
    ),
)


@dataclass(frozen=True)
class ThanosGoal:
    """Fixed primary goal G. Denial does not rewrite G — only path cost."""

    id: str = "universal_balance_cull"
    statement: str = (
        "Randomly erase half of all life so the remainder can thrive on "
        "finite resources — 'balance' as he defines it."
    )
    means: str = (
        "Assemble all six Infinity Stones, enact the Snap, then destroy "
        "the stones so the outcome cannot be undone."
    )


@dataclass(frozen=True)
class MotivationProfile:
    """What the films give us as motive structure — not a psych eval."""

    goal: ThanosGoal
    quotes: tuple[PurposeQuote, ...]
    w_progress: Fraction = Fraction(1)
    w_personal_cost: Fraction = Fraction(1, 5)  # cost already ≤ 0
    w_lock_in: Fraction = Fraction(1, 2)
    # Enactment must strictly dominate any capability subtotal:
    # w_goal_attainment * 1 > w_progress * 1 (a full, unsnapped gauntlet
    # is worth less than the Snap itself). See test_snap_dominates_gauntlet.
    w_goal_attainment: Fraction = Fraction(2)


DEFAULT_MOTIVATION = MotivationProfile(
    goal=ThanosGoal(),
    quotes=THANOS_PURPOSE_QUOTES,
)


def validate_motivation_profile(motiv: MotivationProfile) -> None:
    """Enactment must strictly dominate full capability under these weights.

    Without this, a complete unsnapped gauntlet can outrank the Snap —
    collapsing capability and enactment back into one scalar."""
    if motiv.w_goal_attainment * Fraction(1) <= motiv.w_progress * Fraction(1):
        raise ValueError(
            "w_goal_attainment must exceed w_progress so enactment strictly "
            "dominates capability (see test_snap_dominates_gauntlet)"
        )


STONE_FRACTION = Fraction(1, 6)


@dataclass(frozen=True)
class EdgeReward:
    """Immediate reward on a transition, split by channel.

    ``delta_progress`` is capability (stones toward a working gauntlet);
    ``goal_attainment`` is enactment (the cull actually happening). They
    are separate channels because they are separate facts: a guardian
    can leave capability at 1 and attainment at 0 — that gap is the
    Wakanda interdiction window.
    """

    source: str
    target: str
    delta_progress: Fraction = Fraction(0)
    personal_cost: Fraction = Fraction(0)
    lock_in: Fraction = Fraction(0)
    goal_attainment: Fraction = Fraction(0)
    beat: str = ""
    quote: str = ""

    def utility(self, motiv: MotivationProfile = DEFAULT_MOTIVATION) -> Fraction:
        return (
            motiv.w_progress * self.delta_progress
            + motiv.w_personal_cost * self.personal_cost
            + motiv.w_lock_in * self.lock_in
            + motiv.w_goal_attainment * self.goal_attainment
        )


@dataclass(frozen=True)
class RewardAccount:
    """Cumulative channels along a path, priced by ``motiv``."""

    progress: Fraction
    personal_cost: Fraction
    lock_in: Fraction
    edges: tuple[EdgeReward, ...]
    # Added in 1.2.0 after `edges` and defaulted, so existing positional
    # and keyword construction keeps working (API.md froze the surface).
    goal_attainment: Fraction = Fraction(0)
    motiv: MotivationProfile = DEFAULT_MOTIVATION

    @property
    def utility(self) -> Fraction:
        return sum((e.utility(self.motiv) for e in self.edges), Fraction(0))

    def as_dict(self) -> dict[str, float]:
        return {
            "progress": float(self.progress),
            "personal_cost": float(self.personal_cost),
            "lock_in": float(self.lock_in),
            "goal_attainment": float(self.goal_attainment),
            "utility": float(self.utility),
        }


def build_edge_rewards() -> dict[tuple[str, str], EdgeReward]:
    """Canon-labeled rewards for offender-relevant edges."""
    rows: list[EdgeReward] = [
        EdgeReward(
            "CampaignInitiation", "StatesmanIntercept",
            delta_progress=STONE_FRACTION,
            beat="Power Stone already held (Xandar, exogenous); campaign opens at 1/6",
        ),
        EdgeReward(
            "StatesmanIntercept", "LokiCoercion",
            beat="fleet / Black Order boarding",
        ),
        EdgeReward(
            "LokiCoercion", "SpaceExtraction",
            beat="Thor leveraged; Loki yields the Tesseract",
        ),
        EdgeReward(
            "SpaceExtraction", "SnapEvent",
            delta_progress=STONE_FRACTION,
            beat="Space Stone socketed",
        ),
        EdgeReward(
            "KnowhereApproach", "CollectorConcealment",
            beat="portal in; Reality Stone held by the Collector",
        ),
        EdgeReward(
            "CollectorConcealment", "RealityExtraction",
            beat="Knowhere illusion / deception",
        ),
        EdgeReward(
            "RealityExtraction", "SnapEvent",
            delta_progress=STONE_FRACTION,
            beat="Reality Stone socketed",
        ),
        EdgeReward(
            "VormirApproach", "GamoraLeverage",
            beat="brings Gamora; Red Skull names the price",
        ),
        EdgeReward(
            "GamoraLeverage", "SoulExtraction",
            personal_cost=Fraction(-1),
            beat="sacrifices Gamora — goal advances only on the next edge; "
                 "grief is booked here",
            quote="I ignored my destiny once. I cannot do that again. "
                  "Even for you. I'm sorry, Gamora.",
        ),
        EdgeReward(
            "SoulExtraction", "SnapEvent",
            delta_progress=STONE_FRACTION,
            beat="Soul Stone socketed; mourning deferred",
            quote="Today, I lost more than you can know. But now is no "
                  "time to mourn.",
        ),
        EdgeReward(
            "TitanAmbush", "StrangeBargain",
            beat="Ambush on Titan; Strange opens the bargain space",
        ),
        EdgeReward(
            "StrangeBargain", "TimeExtraction",
            beat="Accepts Strange's trade: Time Stone for Stark's life. "
                 "Stark is spared because the stone is worth more to G than "
                 "killing him — respect line is real; the ranking is still G.",
            quote="You have my respect, Stark. When I'm done, half of "
                  "humanity will still be alive. I hope they remember you.",
        ),
        EdgeReward(
            "TimeExtraction", "SnapEvent",
            delta_progress=STONE_FRACTION,
            beat="Time Stone socketed",
        ),
        EdgeReward(
            "WakandaAssault", "DefensePenetration",
            beat="Black Order / Outriders press Wakanda",
        ),
        EdgeReward(
            "DefensePenetration", "MindExtraction",
            beat="Vision taken; Time Stone undoes destruction",
        ),
        EdgeReward(
            "MindExtraction", "SnapEvent",
            delta_progress=STONE_FRACTION,
            beat="Mind Stone socketed — gauntlet complete on this edge "
                 "in the layered reading",
        ),
        EdgeReward(
            "SnapEvent", "GardenWithdrawal",
            goal_attainment=Fraction(1),
            beat="The Snap — G enacted with a full gauntlet "
                 "('perfectly balanced'). Attainment is booked HERE, not "
                 "at the last socket: capability != enactment.",
            quote="Perfectly balanced, as all things should be.",
        ),
        EdgeReward(
            "GardenWithdrawal", "RemediationBattle",
            lock_in=Fraction(1),
            beat="Destroys the stones to make the cull irreversible",
            quote="I used the stones to destroy the stones. It nearly "
                  "killed me. But the work is done. It always will be.",
        ),
    ]
    return {(e.source, e.target): e for e in rows}


def canon_offender_path() -> list[tuple[str, str]]:
    """Film-order walk used to accumulate R (Power already held)."""
    return [
        ("CampaignInitiation", "StatesmanIntercept"),
        ("StatesmanIntercept", "LokiCoercion"),
        ("LokiCoercion", "SpaceExtraction"),
        ("SpaceExtraction", "SnapEvent"),
        ("KnowhereApproach", "CollectorConcealment"),
        ("CollectorConcealment", "RealityExtraction"),
        ("RealityExtraction", "SnapEvent"),
        ("VormirApproach", "GamoraLeverage"),
        ("GamoraLeverage", "SoulExtraction"),
        ("SoulExtraction", "SnapEvent"),
        ("TitanAmbush", "StrangeBargain"),
        ("StrangeBargain", "TimeExtraction"),
        ("TimeExtraction", "SnapEvent"),
        ("WakandaAssault", "DefensePenetration"),
        ("DefensePenetration", "MindExtraction"),
        ("MindExtraction", "SnapEvent"),
        ("SnapEvent", "GardenWithdrawal"),
        ("GardenWithdrawal", "RemediationBattle"),
    ]


def accumulate_rewards(
    path: list[tuple[str, str]] | None = None,
    rewards: dict[tuple[str, str], EdgeReward] | None = None,
    motiv: MotivationProfile = DEFAULT_MOTIVATION,
    *,
    validate_motiv: bool = True,
) -> RewardAccount:
    if validate_motiv:
        validate_motivation_profile(motiv)
    rewards = rewards if rewards is not None else build_edge_rewards()
    path = path if path is not None else canon_offender_path()
    edges: list[EdgeReward] = []
    for key in path:
        if key not in rewards:
            raise KeyError(f"no EdgeReward for {key[0]}->{key[1]}")
        edges.append(rewards[key])
    return RewardAccount(
        progress=sum((e.delta_progress for e in edges), Fraction(0)),
        personal_cost=sum((e.personal_cost for e in edges), Fraction(0)),
        lock_in=sum((e.lock_in for e in edges), Fraction(0)),
        goal_attainment=sum((e.goal_attainment for e in edges), Fraction(0)),
        edges=tuple(edges),
        motiv=motiv,
    )


def validate_rewards_against_machine(m: StateMachine | None = None) -> None:
    """Every rewarded edge must exist on the machine; not every edge needs R."""
    from .campaign import build_machine

    m = m if m is not None else build_machine()
    known = {(t.source, t.target) for t in m.transitions}
    for key in build_edge_rewards():
        if key not in known:
            raise ValueError(f"reward on missing edge {key}")


def defender_leverage_notes() -> list[tuple[str, str]]:
    """What a guardian coalition should read off Thanos's R channels."""
    return [
        (
            "contact / early stones",
            "G is fixed; denying one stone only reprices the path. Hit "
            "before the gauntlet is full — same lesson as Strange's first-node "
            "failure mass.",
        ),
        (
            "Vormir / attachment",
            "Only edge with personal_cost < 0. He will still pay it if Soul "
            "is required for G. Leverage is scarce: you need an alternative "
            "completing path for him to refuse, or you exploit the grief "
            "after the fact (he is slower, not stopped).",
        ),
        (
            "Titan / instrumental bargains",
            "Stark-spare is payment for Time Stone, not a second goal. Do "
            "not plan on his respect. Bargains that advance G will be taken.",
        ),
        (
            "capability ≠ enactment (the Wakanda window)",
            "progress=1 does not mean the harm happened: goal_attainment "
            "stays 0 until the Snap edge. The gap between last socket and "
            "enactment is the final interdiction window — thin in canon "
            "(seconds), but nonzero, and the only window where denial "
            "still prevents rather than merely reprices.",
        ),
        (
            "Snap → Garden / lock_in",
            "After enactment, R shifts to irreversibility. Denial is too "
            "late; only remediation (reverse the completed harm) remains — "
            "exactly the Endgame shape.",
        ),
        (
            "Next titan with a similar R shape",
            "If a later villain keeps (fixed G, stone-like means, "
            "attachment cost, lock_in maintenance), reuse this map: contest "
            "means early, treat attachment costs as costly-not-vetoes, never "
            "trust instrumental mercy, budget for remediation if lock_in "
            "lands. Doom-class threats can share the *shape* even when lore "
            "and powers differ.",
        ),
    ]


def reward_report() -> str:
    """Human-readable motivation + channel ledger for the canon path."""
    motiv = DEFAULT_MOTIVATION
    acct = accumulate_rewards()
    lines = [
        "THANOS REWARD REPORT — motivation & multi-channel R",
        "=" * 66,
        f"G: {motiv.goal.statement}",
        f"Means: {motiv.goal.means}",
        "",
        "Statement of purpose (selected public lines):",
    ]
    for q in motiv.quotes:
        lines.append(f'  [{q.film} / {q.beat}]')
        lines.append(f'    "{q.text}"')
    lines.append("")
    lines.append(
        f"Preference weights: progress={motiv.w_progress}, "
        f"personal_cost={motiv.w_personal_cost}, lock_in={motiv.w_lock_in}, "
        f"goal_attainment={motiv.w_goal_attainment}"
    )
    lines.append("")
    lines.append("Canon path — edges where channels move:")
    for e in acct.edges:
        if (e.delta_progress or e.personal_cost or e.lock_in
                or e.goal_attainment or e.quote):
            bits = []
            if e.delta_progress:
                bits.append(f"Δprogress={e.delta_progress}")
            if e.personal_cost:
                bits.append(f"personal_cost={e.personal_cost}")
            if e.lock_in:
                bits.append(f"lock_in={e.lock_in}")
            if e.goal_attainment:
                bits.append(f"goal_attainment={e.goal_attainment}")
            bits.append(f"u={e.utility(motiv)}")
            lines.append(f"  {e.source} -> {e.target}: " + ", ".join(bits))
            if e.beat:
                lines.append(f"      {e.beat}")
            if e.quote:
                lines.append(f'      "{e.quote}"')
    lines.append("")
    lines.append(
        f"Cumulative: progress={acct.progress}  "
        f"personal_cost={acct.personal_cost}  "
        f"lock_in={acct.lock_in}  "
        f"goal_attainment={acct.goal_attainment}  "
        f"utility={acct.utility}"
    )
    lines.append("")
    lines.append(
        "Read: stone progress reaches 1 when the Mind Stone sockets — "
        "that is CAPABILITY, not the goal. goal_attainment books at the "
        "Snap itself: a full, unsnapped gauntlet scores progress=1, "
        "attainment=0, and its utility subtotal is strictly below the "
        "Snap's contribution (w_goal > w_progress). personal_cost is "
        "almost entirely Vormir; lock_in is the Garden. Full-path "
        "utility stays positive. The Vormir package alone is locally "
        "negative under default grief weight — he takes it because Soul "
        "enables every completing path (without it progress ≤ 5/6). "
        "Channels keep the hurt visible; path-enablement explains the "
        "choice scalar greed cannot."
    )
    lines.append("")
    lines.append("Defender read (for Strange's policy + later coalitions):")
    for where, note in defender_leverage_notes():
        lines.append(f"  [{where}] {note}")
    return "\n".join(lines)


def reward_report_cli() -> None:
    print(reward_report())

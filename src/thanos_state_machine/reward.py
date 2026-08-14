"""Thanos's motivation and reward: multi-channel R along the campaign.

Public canon only (*Infinity War*, *Endgame*). The point of keeping
channels separate — progress toward the cull vs personal cost vs
instrumental bargains — is that a single scalar erases the Gamora beat:
he advances the goal *and* is wounded. Scalar R can rank the edge; it
cannot narrate why the ranking hurt.
"""

from __future__ import annotations

from dataclasses import dataclass

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
    # Instrumental subgoal on the path to G (not a competing terminal goal).
    means: str = (
        "Assemble all six Infinity Stones, enact the Snap, then destroy "
        "the stones so the outcome cannot be undone."
    )


@dataclass(frozen=True)
class MotivationProfile:
    """What the films give us as motive structure — not a psych eval."""

    goal: ThanosGoal
    quotes: tuple[PurposeQuote, ...]
    # Preferences over reward channels when collapsing to a ranking.
    # Progress dominates; personal cost is felt but does not veto destiny.
    w_progress: float = 1.0
    w_personal_cost: float = 0.20  # cost already ≤ 0
    w_lock_in: float = 0.50        # maintenance / irreversibility


DEFAULT_MOTIVATION = MotivationProfile(
    goal=ThanosGoal(),
    quotes=THANOS_PURPOSE_QUOTES,
)


# ---------------------------------------------------------------------------
# Multi-channel edge rewards
# ---------------------------------------------------------------------------

# Six stones; Power is exogenous (pre-s0), so the machine starts at 1/6.
STONE_FRACTION = 1.0 / 6.0


@dataclass(frozen=True)
class EdgeReward:
    """Immediate reward on a transition, split by channel.

    ``delta_progress`` — movement toward G (stone socket, Snap, etc.).
    ``personal_cost`` — grief / attachment loss (≤ 0); Vormir.
    ``lock_in`` — making a completed goal harder to reverse (Garden).
    """

    source: str
    target: str
    delta_progress: float = 0.0
    personal_cost: float = 0.0
    lock_in: float = 0.0
    beat: str = ""
    quote: str = ""

    def utility(self, motiv: MotivationProfile = DEFAULT_MOTIVATION) -> float:
        """Scalar ranking under Thanos's stated preference weights."""
        return (
            motiv.w_progress * self.delta_progress
            + motiv.w_personal_cost * self.personal_cost
            + motiv.w_lock_in * self.lock_in
        )


@dataclass(frozen=True)
class RewardAccount:
    """Cumulative channels along a path."""

    progress: float
    personal_cost: float
    lock_in: float
    edges: tuple[EdgeReward, ...]

    @property
    def utility(self) -> float:
        return sum(e.utility() for e in self.edges)

    def as_dict(self) -> dict[str, float]:
        return {
            "progress": self.progress,
            "personal_cost": self.personal_cost,
            "lock_in": self.lock_in,
            "utility": self.utility,
        }


def build_edge_rewards() -> dict[tuple[str, str], EdgeReward]:
    """Canon-labeled rewards for offender-relevant edges.

    Guardian remediation edges are omitted (not Thanos's R). Extractions
    that only socket a stone get +STONE_FRACTION progress. The Snap pushes
    progress to completion (remaining mass). Vormir alone carries personal
    cost. The Titan bargain notes Stark spared as *payment*, not mercy as
    terminal value.
    """
    rows: list[EdgeReward] = [
        EdgeReward(
            "CampaignInitiation", "StatesmanIntercept",
            delta_progress=STONE_FRACTION,
            beat="Power Stone already held (Xandar, exogenous); campaign opens at 1/6",
        ),
        # Space
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
        # Reality
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
        # Soul — the load-bearing motivation beat
        EdgeReward(
            "VormirApproach", "GamoraLeverage",
            beat="brings Gamora; Red Skull names the price",
        ),
        EdgeReward(
            "GamoraLeverage", "SoulExtraction",
            personal_cost=-1.0,
            beat="sacrifices Gamora — goal advances only on the next edge; "
                 "grief is booked here",
            quote="I ignored my destiny once. I cannot do that again. "
                  "Even for you. I'm sorry, Gamora.",
        ),
        EdgeReward(
            "SoulExtraction", "SnapEvent",
            delta_progress=STONE_FRACTION,
            personal_cost=0.0,  # cost already taken on the sacrifice edge
            beat="Soul Stone socketed; mourning deferred",
            quote="Today, I lost more than you can know. But now is no "
                  "time to mourn.",
        ),
        # Time — Stark spared as instrumental bargain
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
        # Mind
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
        # Campaign spine after full set
        EdgeReward(
            "SnapEvent", "GardenWithdrawal",
            delta_progress=0.0,  # stones already at 1.0; this edge *enacts* G
            beat="The Snap — G enacted with a full gauntlet "
                 "('perfectly balanced')",
            quote="Perfectly balanced, as all things should be.",
        ),
        EdgeReward(
            "GardenWithdrawal", "RemediationBattle",
            # Offender half of this edge is stone destruction; heist/reverse
            # are guardian. We still book lock_in for the destruction intent.
            lock_in=1.0,
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
) -> RewardAccount:
    rewards = rewards if rewards is not None else build_edge_rewards()
    path = path if path is not None else canon_offender_path()
    edges: list[EdgeReward] = []
    for key in path:
        if key not in rewards:
            raise KeyError(f"no EdgeReward for {key[0]}->{key[1]}")
        edges.append(rewards[key])
    return RewardAccount(
        progress=sum(e.delta_progress for e in edges),
        personal_cost=sum(e.personal_cost for e in edges),
        lock_in=sum(e.lock_in for e in edges),
        edges=tuple(edges),
    )


def validate_rewards_against_machine(m: StateMachine | None = None) -> None:
    """Every rewarded edge must exist on the machine; not every edge needs R."""
    from .campaign import build_machine

    m = m if m is not None else build_machine()
    known = {(t.source, t.target) for t in m.transitions}
    for key in build_edge_rewards():
        if key not in known:
            raise ValueError(f"reward on missing edge {key}")


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
        f"personal_cost={motiv.w_personal_cost}, lock_in={motiv.w_lock_in}"
    )
    lines.append("")
    lines.append("Canon path — edges where channels move:")
    for e in acct.edges:
        if e.delta_progress or e.personal_cost or e.lock_in or e.quote:
            bits = []
            if e.delta_progress:
                bits.append(f"Δprogress={e.delta_progress:+.4f}")
            if e.personal_cost:
                bits.append(f"personal_cost={e.personal_cost:+.2f}")
            if e.lock_in:
                bits.append(f"lock_in={e.lock_in:+.2f}")
            bits.append(f"u={e.utility():+.4f}")
            lines.append(f"  {e.source} -> {e.target}: " + ", ".join(bits))
            if e.beat:
                lines.append(f"      {e.beat}")
            if e.quote:
                lines.append(f'      "{e.quote}"')
    lines.append("")
    lines.append(
        f"Cumulative: progress={acct.progress:.4f}  "
        f"personal_cost={acct.personal_cost:.2f}  "
        f"lock_in={acct.lock_in:.2f}  "
        f"utility={acct.utility:.4f}"
    )
    lines.append("")
    lines.append(
        "Read: stone progress reaches 1.0 when the Mind Stone sockets; "
        "the Snap *enacts* G; personal_cost is almost entirely Vormir; "
        "lock_in is the Garden. Full-path utility stays positive. The "
        "Vormir package alone is locally negative under default grief "
        "weight — he takes it because Soul enables every completing path "
        "(without it progress ≤ 5/6). Channels keep the hurt visible; "
        "path-enablement explains the choice scalar greed cannot."
    )
    return "\n".join(lines)


def reward_report_cli() -> None:
    print(reward_report())

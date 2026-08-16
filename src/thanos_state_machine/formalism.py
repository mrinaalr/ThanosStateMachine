"""M = (S, A, T, R_G, s0, F) as one executable object.

``machine.py`` gives the *ontology* view: a labelled edge list that mirrors
``graphs/thanos_campaign.ttl``. That view is deliberately loose — it is a
picture of the campaign, not a machine you can run. Three things it does not
do, and which a tuple shipped in a real case has to:

1. **T is not a function.** ``StateMachine.transitions`` is a list of edges,
   three of which carry no action label at all, so ``T(s, a)`` is undefined
   even in principle.
2. **A is not state-indexed.** There is no ``A(s)``, so "A grows along the
   trajectory" (FORMALISM §4.2) is prose rather than a computable guard.
3. **R_G is not in the tuple.** Rewards live in ``reward.py``, keyed by edge
   pairs, with nothing binding them to the machine.

The consequence is visible without running anything: ``KnowhereApproach``,
``VormirApproach``, ``TitanAmbush`` and ``WakandaAssault`` have no incoming
edge, so they are unreachable from s0, and ``canon_offender_path()`` is a
hand-listed sequence of edges with four discontinuities — not a walk. The
picture is right; it just is not yet a machine.

This module closes the gap with the standard product construction.

Definitions
-----------
Let ``X`` be the finite set of stones, |X| = 6, and ``N`` the finite set of
campaign *positions*. A state pairs a position with the *keyring* of stones
socketed so far::

    S ⊆ N × 2^X,        s = (n, K)

``A = A_off ⊎ A_aff ⊎ A_int`` is partitioned by ``ActionKind`` (offender,
affordance, guardian intervention). Affordances carry a precondition map
``req : A_aff ⇀ X``; an edge labelled with affordance ``a`` is admissible at
``(n, K)`` only if ``req(a) ∈ K``. This is what makes A state-indexed::

    A(s) = { a ∈ A : T(s, a) is defined }

``T : S × A ⇀ S`` is a *partial deterministic* function. Each edge has one
**driving action** (the argument of T) plus **co-labels** — the supporting
affordances the ontology view already records on that edge. Both driver and
co-labels are gated, so an edge is admissible only if every capability it
invokes is in hand.

``R_G : dom(T) → ℚ⁴`` is the multi-channel reward
``(Δprogress, personal_cost, lock_in, goal_attainment)`` of ``reward.py``.
The ``EdgeReward`` objects are *reused*, not copied: every rewarded edge here
declares which ``build_edge_rewards()`` entry it inherits, so there is one
ledger and ``tests/test_formalism.py`` pins the totals to
``accumulate_rewards()``. Scalar utility is ``U_w(s,a) = ⟨w, R_G(s,a)⟩`` with
``w`` from ``MotivationProfile``.

``s0 = (CampaignInitiation, ∅)``. ``F`` maps terminal states to
``Polarity``: ``(SnapEvent, X) ↦ completed`` and
``(CampaignRemediated, ∅) ↦ remediated``. The first is terminal-*capable*:
the realized 2018–2023 composite trajectory passes through it, exactly as
``campaign.build_machine()`` already asserts.

What the factoring buys
-----------------------
The old machine used ``SnapEvent`` for two jobs — the socket target for all
five stone layers, and the harm state. Splitting the accumulator
(``GauntletStaging``) from the enactment (``SnapEvent``) is the same
capability-vs-enactment distinction v1.2.0 drew in the reward channels, now
drawn in S. It makes three statements testable rather than rhetorical
(see ``tuple_report()`` and ``tests/test_formalism.py``):

* the campaign admits exactly six affordance-consistent acquisition orders;
* every one of them has the same return, so re-ordering acquisitions is
  worth nothing to the offender (Law 4, on the offender's own ledger);
* ``(GauntletStaging, X)`` — progress = 1, attainment = 0 — lies on every
  complete trajectory and is the last state at which denial still prevents.
"""

from __future__ import annotations

import random
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from fractions import Fraction

from .exploitation import (
    EdgeBenefit,
    ExploitationVerdict,
    classify_campaign_edges,
    trajectory_verdict,
)
from .machine import Action, ActionKind, Polarity
from .reward import (
    DEFAULT_MOTIVATION,
    EdgeReward,
    MotivationProfile,
    RewardAccount,
    ThanosGoal,
    build_edge_rewards,
)

# ---------------------------------------------------------------------------
# X — the stone set, in canon acquisition order (used for display only)
# ---------------------------------------------------------------------------

STONES: tuple[str, ...] = ("power", "space", "reality", "soul", "time", "mind")
_STONE_RANK = {s: i for i, s in enumerate(STONES)}
_STONE_ABBR = {
    "power": "P", "space": "Sp", "reality": "R",
    "soul": "So", "time": "T", "mind": "M",
}

#: ``req`` — the precondition map on affordances. ``a_power_stone`` is
#: deliberately absent: the Power Stone is exogenous (Xandar, off-screen) and
#: its action is the *grant* edge, not a use of a held capability.
AFFORDANCE_REQUIRES: Mapping[str, str] = {
    "a_space_skip": "space",
    "a_reality_warp": "reality",
    "a_time_reverse": "time",
}

# Campaign positions that are not part of a stone layer.
CAMPAIGN_INITIATION = "CampaignInitiation"
GAUNTLET_STAGING = "GauntletStaging"
SNAP_EVENT = "SnapEvent"
GARDEN_WITHDRAWAL = "GardenWithdrawal"
REMEDIATION_BATTLE = "RemediationBattle"
CAMPAIGN_REMEDIATED = "CampaignRemediated"


# ---------------------------------------------------------------------------
# S — factored states
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CampaignState:
    """s = (position, keyring). The keyring is the socketed stone set K."""

    position: str
    keyring: frozenset[str] = frozenset()

    @property
    def stones(self) -> tuple[str, ...]:
        """Held stones in canon order."""
        return tuple(sorted(self.keyring, key=_STONE_RANK.__getitem__))

    @property
    def progress(self) -> Fraction:
        """Capability: |K| / 6. Not the goal — see ``goal_attainment``."""
        return Fraction(len(self.keyring), len(STONES))

    @property
    def label(self) -> str:
        held = "+".join(_STONE_ABBR[s] for s in self.stones) or "-"
        return f"{self.position}[{held}]"

    def with_stone(self, stone: str) -> CampaignState:
        return CampaignState(self.position, self.keyring | {stone})

    def at(self, position: str) -> CampaignState:
        return CampaignState(position, self.keyring)

    def __str__(self) -> str:  # pragma: no cover - display only
        return self.label


@dataclass(frozen=True)
class TupleEdge:
    """One entry of T, with the R_G row it carries.

    ``action`` is the driving action — the second argument of ``T(s, a)``.
    ``co_labels`` are the supporting affordances the ontology view records on
    the corresponding edge; they are gated too, so they constrain
    admissibility without being selectable.
    """

    source: CampaignState
    action: str
    target: CampaignState
    co_labels: tuple[str, ...] = ()
    trigger: str = ""
    #: key into ``build_edge_rewards()`` / ``classify_campaign_edges()``
    canon_edge: tuple[str, str] | None = None
    reward: EdgeReward | None = None

    @property
    def labels(self) -> tuple[str, ...]:
        """Driver plus co-labels — every capability this edge invokes."""
        return (self.action, *self.co_labels)

    def channels(self) -> dict[str, Fraction]:
        r = self.reward
        if r is None:
            return {"progress": Fraction(0), "personal_cost": Fraction(0),
                    "lock_in": Fraction(0), "goal_attainment": Fraction(0)}
        return {"progress": r.delta_progress, "personal_cost": r.personal_cost,
                "lock_in": r.lock_in, "goal_attainment": r.goal_attainment}

    def utility(self, motiv: MotivationProfile = DEFAULT_MOTIVATION) -> Fraction:
        return self.reward.utility(motiv) if self.reward else Fraction(0)


@dataclass(frozen=True)
class CampaignTrajectory:
    """σ = (s0, a0, s1, ..., a_{T-1}, s_T) with s_T ∈ F."""

    edges: tuple[TupleEdge, ...]
    polarity: Polarity

    @property
    def states(self) -> tuple[CampaignState, ...]:
        if not self.edges:
            return ()
        return (*(e.source for e in self.edges), self.edges[-1].target)

    @property
    def actions(self) -> tuple[str, ...]:
        return tuple(e.action for e in self.edges)

    @property
    def acquisition_order(self) -> tuple[str, ...]:
        """Stones in the order they were socketed."""
        order: list[str] = []
        for e in self.edges:
            gained = e.target.keyring - e.source.keyring
            order.extend(sorted(gained, key=_STONE_RANK.__getitem__))
        return tuple(order)

    def account(
        self, motiv: MotivationProfile = DEFAULT_MOTIVATION
    ) -> RewardAccount:
        """Cumulative R_G over σ, as the same ``RewardAccount`` reward.py uses."""
        rewarded = tuple(e.reward for e in self.edges if e.reward is not None)
        return RewardAccount(
            progress=sum((r.delta_progress for r in rewarded), Fraction(0)),
            personal_cost=sum((r.personal_cost for r in rewarded), Fraction(0)),
            lock_in=sum((r.lock_in for r in rewarded), Fraction(0)),
            goal_attainment=sum(
                (r.goal_attainment for r in rewarded), Fraction(0)
            ),
            edges=rewarded,
            motiv=motiv,
        )

    def ledger(
        self, motiv: MotivationProfile = DEFAULT_MOTIVATION
    ) -> list[dict[str, object]]:
        """Per-transition reward and the running cumulative after it."""
        run = {"progress": Fraction(0), "personal_cost": Fraction(0),
               "lock_in": Fraction(0), "goal_attainment": Fraction(0)}
        util = Fraction(0)
        rows: list[dict[str, object]] = []
        for i, e in enumerate(self.edges):
            ch = e.channels()
            for k, v in ch.items():
                run[k] += v
            util += e.utility(motiv)
            rows.append({
                "step": i,
                "edge": e,
                "channels": dict(ch),
                "utility": e.utility(motiv),
                "cumulative": dict(run),
                "cumulative_utility": util,
            })
        return rows


# ---------------------------------------------------------------------------
# M — the tuple itself
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OffenseMachine:
    """M = (S, A, T, R_G, s0, F).

    The *generic* goal-dependent offense/harm machine — the parent that
    FORMALISM §5 argues the ESM specializes by adding the extraction
    predicate. Nothing in this class knows what exploitation is; that
    question is answered over a trajectory, by ``exploitation.py``.
    """

    states: tuple[CampaignState, ...]                  # S
    actions: Mapping[str, Action]                      # A
    edges: tuple[TupleEdge, ...]                       # T (as its graph)
    initial: CampaignState                             # s0
    terminals: Mapping[CampaignState, Polarity]        # F
    goal: ThanosGoal
    motivation: MotivationProfile = DEFAULT_MOTIVATION
    requires: Mapping[str, str] = field(
        default_factory=lambda: dict(AFFORDANCE_REQUIRES)
    )

    # -- T ------------------------------------------------------------------

    def _index(self) -> dict[tuple[CampaignState, str], TupleEdge]:
        return {(e.source, e.action): e for e in self.edges}

    def successors(self, s: CampaignState) -> tuple[TupleEdge, ...]:
        return tuple(e for e in self.edges if e.source == s)

    def admissible_actions(self, s: CampaignState) -> tuple[Action, ...]:
        """A(s) — actions for which T(s, ·) is defined, in edge order."""
        return tuple(self.actions[e.action] for e in self.successors(s))

    def offender_actions(self, s: CampaignState) -> tuple[Action, ...]:
        """A(s) minus guardian interventions."""
        return tuple(
            a for a in self.admissible_actions(s)
            if a.kind is not ActionKind.INTERVENTION
        )

    def transition(self, s: CampaignState, a: str) -> CampaignState:
        """T(s, a). Raises ``KeyError`` where T is undefined."""
        edge = self._index().get((s, a))
        if edge is None:
            raise KeyError(f"T undefined at ({s.label}, {a})")
        return edge.target

    def enabled(self, s: CampaignState, labels: tuple[str, ...]) -> bool:
        """Are every affordance in ``labels`` unlocked at ``s``?"""
        return all(
            self.requires[lb] in s.keyring
            for lb in labels if lb in self.requires
        )

    # -- F ------------------------------------------------------------------

    def is_terminal(self, s: CampaignState) -> bool:
        return s in self.terminals

    def is_absorbing(self, s: CampaignState) -> bool:
        return not self.successors(s)

    # -- walking ------------------------------------------------------------

    def walk(self, actions: list[str]) -> CampaignTrajectory:
        """Follow a fixed action sequence from s0."""
        idx = self._index()
        s = self.initial
        taken: list[TupleEdge] = []
        for a in actions:
            edge = idx.get((s, a))
            if edge is None:
                raise KeyError(f"T undefined at ({s.label}, {a})")
            taken.append(edge)
            s = edge.target
        return CampaignTrajectory(
            tuple(taken), self.terminals.get(s, Polarity.DISRUPTED)
        )

    def trajectories(self) -> Iterator[CampaignTrajectory]:
        """Every complete s0 → absorbing-terminal path. The state graph is a
        DAG (K grows monotonically until the one edge that empties it), so
        this terminates."""

        def walk(s: CampaignState, acc: list[TupleEdge]) -> Iterator[CampaignTrajectory]:
            succ = self.successors(s)
            if not succ:
                if s in self.terminals:
                    yield CampaignTrajectory(tuple(acc), self.terminals[s])
                return
            for e in succ:
                yield from walk(e.target, [*acc, e])

        yield from walk(self.initial, [])

    def sample_trajectory(self, rng: random.Random) -> CampaignTrajectory:
        """One rollout under the uniform-over-A(s) offender policy.

        The offender side is deterministic given an acquisition order, so
        this samples an *order*, not an outcome. See ``tuple_report()``:
        the return is invariant, so the Monte Carlo has zero variance —
        all the uncertainty in this campaign lives on the guardian side.
        """
        s = self.initial
        taken: list[TupleEdge] = []
        while True:
            succ = self.successors(s)
            if not succ:
                break
            e = rng.choice(list(succ))
            taken.append(e)
            s = e.target
        return CampaignTrajectory(
            tuple(taken), self.terminals.get(s, Polarity.DISRUPTED)
        )

    def canon_trajectory(self) -> CampaignTrajectory:
        """The realized film trajectory: space → reality → soul → time → mind."""
        return next(
            t for t in self.trajectories()
            if t.acquisition_order == STONES
        )

    # -- analysis -----------------------------------------------------------

    def necessary_states(self) -> tuple[CampaignState, ...]:
        """States on *every* complete trajectory — mandatory interdiction
        points. A guardian that can act at one of these is guaranteed a
        window regardless of the order the offender picks."""
        paths = [set(t.states) for t in self.trajectories()]
        if not paths:
            return ()
        common = set.intersection(*paths)
        return tuple(sorted(common, key=lambda s: (s.position, len(s.keyring))))

    def enactment_window(self) -> tuple[CampaignState, ...]:
        """States with full capability and zero attainment: progress = 1 and
        no outgoing edge has yet booked ``goal_attainment``."""
        return tuple(
            s for s in self.states
            if s.progress == 1
            and any(
                e.reward is not None and e.reward.goal_attainment > 0
                for e in self.successors(s)
            )
        )

    def goal_realizing_edge(self) -> TupleEdge:
        """The unique edge on which G is enacted (``goal_attainment`` > 0)."""
        booked = [
            e for e in self.edges
            if e.reward is not None and e.reward.goal_attainment > 0
        ]
        if len(booked) != 1:
            raise ValueError(f"expected exactly one enactment edge, got {len(booked)}")
        return booked[0]

    def verdict(self) -> ExploitationVerdict:
        """Run the SEP predicate over this machine's goal-realizing edge.

        The predicate is not part of M — that is the point of FORMALISM §5.
        It is applied *to* a trajectory of M, and here it returns ``False``.
        """
        goal_edge = self.goal_realizing_edge()
        assert goal_edge.canon_edge is not None
        return trajectory_verdict(goal_edge.canon_edge, classify_campaign_edges())

    def benefit_of(self, edge: TupleEdge) -> EdgeBenefit | None:
        if edge.canon_edge is None:
            return None
        return classify_campaign_edges().get(edge.canon_edge)

    # -- integrity ----------------------------------------------------------

    def validate(self) -> None:
        """Everything a tuple has to satisfy before anyone builds on it."""
        known = set(self.states)
        seen: set[tuple[CampaignState, str]] = set()
        for e in self.edges:
            if e.source not in known or e.target not in known:
                raise ValueError(f"dangling edge {e.source.label}->{e.target.label}")
            for lb in e.labels:
                if lb not in self.actions:
                    raise ValueError(f"unknown action {lb!r} on {e.source.label}")
            key = (e.source, e.action)
            if key in seen:
                raise ValueError(
                    f"T is not a function: ({e.source.label}, {e.action}) "
                    "has two targets"
                )
            seen.add(key)
            if not self.enabled(e.source, e.labels):
                missing = sorted(
                    self.requires[lb] for lb in e.labels
                    if lb in self.requires and self.requires[lb] not in e.source.keyring
                )
                raise ValueError(
                    f"edge {e.source.label}-{e.action}->{e.target.label} "
                    f"invokes unavailable affordance(s): {missing}"
                )
        if self.initial not in known:
            raise ValueError("s0 not in S")
        for s in self.terminals:
            if s not in known:
                raise ValueError(f"terminal {s.label} not in S")
        unreachable = known - self.reachable()
        if unreachable:
            raise ValueError(
                "unreachable states: "
                + ", ".join(sorted(s.label for s in unreachable))
            )

    def reachable(self) -> set[CampaignState]:
        seen = {self.initial}
        stack = [self.initial]
        while stack:
            s = stack.pop()
            for e in self.successors(s):
                if e.target not in seen:
                    seen.add(e.target)
                    stack.append(e.target)
        return seen

    # -- export -------------------------------------------------------------

    def to_dict(self) -> dict[str, object]:
        """JSON-ready form of the whole tuple — the shippable artifact."""
        return {
            "tuple": "M = (S, A, T, R_G, s0, F)",
            "goal": {
                "id": self.goal.id,
                "statement": self.goal.statement,
                "means": self.goal.means,
            },
            "stones": list(STONES),
            "S": [
                {"label": s.label, "position": s.position,
                 "keyring": list(s.stones), "progress": str(s.progress)}
                for s in self.states
            ],
            "A": [
                {"name": a.name, "kind": a.kind.value,
                 "description": a.description,
                 "requires": self.requires.get(a.name)}
                for a in self.actions.values()
            ],
            "T": [
                {"source": e.source.label, "action": e.action,
                 "target": e.target.label, "co_labels": list(e.co_labels),
                 "trigger": e.trigger, "canon_edge": list(e.canon_edge) if e.canon_edge else None,
                 "R_G": {k: str(v) for k, v in e.channels().items()},
                 "utility": str(e.utility(self.motivation))}
                for e in self.edges
            ],
            "R_G": {
                "channels": ["progress", "personal_cost", "lock_in",
                             "goal_attainment"],
                "weights": {
                    "progress": str(self.motivation.w_progress),
                    "personal_cost": str(self.motivation.w_personal_cost),
                    "lock_in": str(self.motivation.w_lock_in),
                    "goal_attainment": str(self.motivation.w_goal_attainment),
                },
            },
            "s0": self.initial.label,
            "F": [
                {"state": s.label, "polarity": p.value}
                for s, p in self.terminals.items()
            ],
            "canon_trajectory": [
                {"source": e.source.label, "action": e.action,
                 "target": e.target.label,
                 "R_G": {k: str(v) for k, v in e.channels().items()}}
                for e in self.canon_trajectory().edges
            ],
        }


# ---------------------------------------------------------------------------
# The Thanos instantiation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StoneLayer:
    """One acquisition sub-trajectory: Approach → Coercion → Extraction."""

    stone: str
    approach: str
    coercion: str
    extraction: str
    #: labels the ontology view puts on approach→coercion
    approach_labels: tuple[str, ...]
    #: labels the ontology view puts on coercion→extraction
    coercion_labels: tuple[str, ...]
    #: labels the ontology view puts on extraction→SnapEvent (the socket)
    socket_labels: tuple[str, ...]
    beat: str

    @property
    def coercion_driver(self) -> str:
        """The offender action that drives conditioning on this layer."""
        return self.coercion_labels[0]


def stone_layers() -> tuple[StoneLayer, ...]:
    """The five layers, with labels carried over from ``build_machine()``.

    ``tests/test_formalism.py`` asserts label parity edge for edge, so the
    ontology view and the tuple cannot drift apart.
    """
    return (
        StoneLayer(
            "space", "StatesmanIntercept", "LokiCoercion", "SpaceExtraction",
            ("a_fleet", "a_power_stone", "a_black_order"),
            ("a_hostage_leverage",), (),
            "Sanctuary II takes the Statesman; Loki yields the Tesseract",
        ),
        StoneLayer(
            "reality", "KnowhereApproach", "CollectorConcealment",
            "RealityExtraction",
            ("a_space_skip",), ("a_deception",), (),
            "Knowhere; the Collector's staged vault",
        ),
        StoneLayer(
            "soul", "VormirApproach", "GamoraLeverage", "SoulExtraction",
            ("a_space_skip",), ("a_hostage_leverage", "a_reality_warp"),
            ("a_sacrifice_rite",),
            "Vormir; a soul for the Soul Stone",
        ),
        StoneLayer(
            "time", "TitanAmbush", "StrangeBargain", "TimeExtraction",
            ("a_space_skip",), ("a_hostage_leverage",), (),
            "Titan; the Time Stone traded for Stark's life",
        ),
        StoneLayer(
            "mind", "WakandaAssault", "DefensePenetration", "MindExtraction",
            ("a_space_skip", "a_fleet", "a_black_order"),
            ("a_fleet",), ("a_time_reverse",),
            "Wakanda; the stone cut from Vision's head",
        ),
    )


def build_actions() -> dict[str, Action]:
    """A — the full action space.

    The fourteen actions of ``build_machine()`` plus the three the ontology
    view left implicit. They are additions, not inventions: without them the
    socket edges, the approach→coercion edges and the withdrawal edge carry
    no label, and ``T(s, a)`` cannot be a function.

    Affordances appear only where canon *exercises* them — Thanos never uses
    the Soul or Mind Stones' own powers, so no ``a_soul_*`` / ``a_mind_*``
    action exists. That is the AfH discipline: an affordance enters A when
    it is misused, not when it is possessed.
    """
    rows = [
        # -- offender -------------------------------------------------------
        # a_seek_<stone> is the flattening of a parameterized action
        # ``seek(x)``: which acquisition layer to open next. Without the
        # parameter T is not a function — holding {power, space} both the
        # reality and the time layer are reachable by the same travel
        # affordance (``a_space_skip``), so the affordance alone does not
        # determine the successor. This is also the offender's only real
        # decision: A(s) at a staging state is exactly the set of stones he
        # can go after right now.
        *[
            Action(f"a_seek_{lay.stone}", ActionKind.OFFENDER,
                   f"open the {lay.stone} acquisition layer — {lay.beat}")
            for lay in stone_layers()
        ],
        Action("a_fleet", ActionKind.OFFENDER,
               "Sanctuary II / Outrider armies"),
        Action("a_black_order", ActionKind.OFFENDER,
               "delegated acquisition (Children of Thanos)"),
        Action("a_engage", ActionKind.OFFENDER,
               "make contact with the holder and take control of the scene "
               "(contact -> conditioning)"),
        Action("a_hostage_leverage", ActionKind.OFFENDER,
               "coerce stone-holder via a hostage (Thor->Loki, Tony->Strange, "
               "Gamora->Soul)"),
        Action("a_deception", ActionKind.OFFENDER,
               "staged scene / concealment (Knowhere illusion)"),
        Action("a_sacrifice_rite", ActionKind.OFFENDER,
               "Vormir exchange: a soul for the Soul Stone"),
        Action("a_socket", ActionKind.OFFENDER,
               "mount an acquired stone in the gauntlet (capability accrual)"),
        Action("a_snap", ActionKind.OFFENDER,
               "terminal harm event: erase half of all life"),
        Action("a_withdraw", ActionKind.OFFENDER,
               "retire to the Garden once G is enacted (maintenance)"),
        Action("a_stone_destruction", ActionKind.OFFENDER,
               "destroy the stones to make the harm irreversible"),
        # -- affordances ----------------------------------------------------
        Action("a_power_stone", ActionKind.AFFORDANCE,
               "acquired pre-s0 (Xandar, exogenous)"),
        Action("a_space_skip", ActionKind.AFFORDANCE,
               "portal arrival anywhere (Space Stone)"),
        Action("a_reality_warp", ActionKind.AFFORDANCE,
               "rewrite local reality (Reality Stone)"),
        Action("a_time_reverse", ActionKind.AFFORDANCE,
               "rewind events (Time Stone)"),
        # -- guardian interventions ----------------------------------------
        Action("a_time_heist", ActionKind.INTERVENTION,
               "guardian remediation: quantum-tunnel retrieval of past stones"),
        Action("a_reverse_snap", ActionKind.INTERVENTION,
               "Hulk snap: restore the erased"),
        Action("a_counter_snap", ActionKind.INTERVENTION,
               "Stark snap: erase the 2014 invasion force"),
    ]
    return {a.name: a for a in rows}


#: Where each tuple edge takes its R_G row from. Two notes on the mapping:
#:
#: * The opening Δprogress (the exogenous Power Stone) rides the
#:   ``a_power_stone`` grant edge rather than the first approach edge; the
#:   ledger row's own beat text — "Power Stone already held (Xandar,
#:   exogenous); campaign opens at 1/6" — describes that edge, not the other.
#: * ``goal_attainment`` rides the edge that *enacts* the Snap, which in the
#:   factored machine is the edge **into** ``SnapEvent``. In the ontology
#:   view, where ``SnapEvent`` doubles as the socket target, the same row
#:   sits on ``SnapEvent -> GardenWithdrawal``.
#:
#: Totals are unchanged either way, and ``test_reward_parity_with_ledger``
#: pins them to ``accumulate_rewards()``.
_OPENING_REWARD = ("CampaignInitiation", "StatesmanIntercept")
_ENACTMENT_REWARD = ("SnapEvent", "GardenWithdrawal")
_LOCK_IN_REWARD = ("GardenWithdrawal", "RemediationBattle")


def build_thanos_tuple(
    motivation: MotivationProfile = DEFAULT_MOTIVATION,
) -> OffenseMachine:
    """The Thanos tuple: M = (S, A, T, R_G, s0, F), validated and walkable."""
    actions = build_actions()
    rewards = build_edge_rewards()
    layers = stone_layers()

    states: set[CampaignState] = set()
    edges: list[TupleEdge] = []

    def add(source: CampaignState, action: str, target: CampaignState,
            co_labels: tuple[str, ...] = (), trigger: str = "",
            canon_edge: tuple[str, str] | None = None) -> None:
        states.add(source)
        states.add(target)
        edges.append(TupleEdge(
            source=source, action=action, target=target,
            co_labels=co_labels, trigger=trigger, canon_edge=canon_edge,
            reward=rewards.get(canon_edge) if canon_edge else None,
        ))

    s0 = CampaignState(CAMPAIGN_INITIATION, frozenset())

    # s0 --a_power_stone--> staging{power}: Xandar is exogenous and off-screen;
    # the campaign opens holding one stone.
    add(s0, "a_power_stone",
        CampaignState(GAUNTLET_STAGING, frozenset({"power"})),
        trigger="Xandar complete (exogenous)", canon_edge=_OPENING_REWARD)

    def gating_ok(layer: StoneLayer, K: frozenset[str]) -> bool:
        """Can this layer be opened holding K? Every affordance the layer
        invokes on any of its edges must already be unlocked."""
        needed = {
            AFFORDANCE_REQUIRES[lb]
            for lb in (*layer.approach_labels, *layer.coercion_labels,
                       *layer.socket_labels)
            if lb in AFFORDANCE_REQUIRES
        }
        arrival = "a_space_skip" if "space" in K else "a_fleet"
        if arrival in AFFORDANCE_REQUIRES:
            needed.add(AFFORDANCE_REQUIRES[arrival])
        return layer.stone not in K and needed <= K

    # Breadth-first over keyrings: from each staging state, open any layer
    # whose affordances are already unlocked.
    frontier = [frozenset({"power"})]
    seen_keyrings: set[frozenset[str]] = {frozenset({"power"})}
    while frontier:
        K = frontier.pop()
        staging = CampaignState(GAUNTLET_STAGING, K)
        states.add(staging)
        for layer in layers:
            if not gating_ok(layer, K):
                continue
            arrival = "a_space_skip" if "space" in K else "a_fleet"
            approach = CampaignState(layer.approach, K)
            coercion = CampaignState(layer.coercion, K)
            extraction = CampaignState(layer.extraction, K)
            add(staging, f"a_seek_{layer.stone}", approach,
                co_labels=(arrival,), trigger=layer.beat)
            add(approach, "a_engage", coercion,
                co_labels=layer.approach_labels,
                canon_edge=(layer.approach, layer.coercion))
            add(coercion, layer.coercion_driver, extraction,
                co_labels=tuple(layer.coercion_labels[1:]),
                canon_edge=(layer.coercion, layer.extraction))
            nxt = K | {layer.stone}
            add(extraction, "a_socket",
                CampaignState(GAUNTLET_STAGING, nxt),
                co_labels=layer.socket_labels,
                trigger="stone socketed into gauntlet",
                canon_edge=(layer.extraction, "SnapEvent"))
            if nxt not in seen_keyrings:
                seen_keyrings.add(nxt)
                frontier.append(nxt)

    full = frozenset(STONES)
    staging_full = CampaignState(GAUNTLET_STAGING, full)
    snap = CampaignState(SNAP_EVENT, full)
    garden = CampaignState(GARDEN_WITHDRAWAL, full)
    # The stones are destroyed at the Garden: the one edge on which the
    # keyring shrinks, and it is the edge that buys lock-in. Capability is
    # spent to make the outcome irreversible.
    battle = CampaignState(REMEDIATION_BATTLE, frozenset())
    remediated = CampaignState(CAMPAIGN_REMEDIATED, frozenset())

    add(staging_full, "a_snap", snap,
        trigger="gauntlet complete; G enacted", canon_edge=_ENACTMENT_REWARD)
    add(snap, "a_withdraw", garden, trigger="the work is done")
    add(garden, "a_stone_destruction", battle,
        co_labels=("a_time_heist", "a_reverse_snap"),
        trigger="guardian remediation, five years later",
        canon_edge=_LOCK_IN_REWARD)
    add(battle, "a_counter_snap", remediated)

    m = OffenseMachine(
        states=tuple(sorted(states, key=lambda s: (s.position, len(s.keyring), s.label))),
        actions=actions,
        edges=tuple(edges),
        initial=s0,
        terminals={snap: Polarity.COMPLETED, remediated: Polarity.REMEDIATED},
        goal=motivation.goal,
        motivation=motivation,
    )
    m.validate()
    return m


# ---------------------------------------------------------------------------
# Parity with the ontology view and the reward ledger
# ---------------------------------------------------------------------------

def validate_against_machine(m: OffenseMachine | None = None) -> None:
    """Every canon edge the tuple claims must exist in ``build_machine()``,
    with the same labels. Guards against the two views drifting."""
    from .campaign import build_machine

    m = m if m is not None else build_thanos_tuple()
    onto = build_machine()
    onto_labels = {(t.source, t.target): set(t.actions) for t in onto.transitions}
    for e in m.edges:
        if e.canon_edge is None:
            continue
        if e.canon_edge not in onto_labels:
            raise ValueError(f"tuple edge claims unknown canon edge {e.canon_edge}")
        # The ontology edge's labels must all be accounted for by the tuple
        # edge (driver or co-label). a_engage / a_socket / a_withdraw are the
        # tuple's own additions and are allowed to be extra.
        onto_set = onto_labels[e.canon_edge]
        extra = onto_set - set(e.labels)
        if extra:
            raise ValueError(
                f"tuple edge {e.source.label}-{e.action}->{e.target.label} "
                f"drops ontology labels {sorted(extra)}"
            )
    missing = set(onto.states) - {s.position for s in m.states}
    if missing:
        raise ValueError(f"ontology states absent from the tuple: {sorted(missing)}")


def validate_against_ledger(m: OffenseMachine | None = None) -> None:
    """The canon trajectory's cumulative R_G must equal ``accumulate_rewards()``
    channel for channel. The tuple re-attaches two rows; it must not change
    a number."""
    from .reward import accumulate_rewards

    m = m if m is not None else build_thanos_tuple()
    got = m.canon_trajectory().account(m.motivation)
    want = accumulate_rewards(motiv=m.motivation)
    for ch in ("progress", "personal_cost", "lock_in", "goal_attainment"):
        if getattr(got, ch) != getattr(want, ch):
            raise ValueError(
                f"{ch}: tuple {getattr(got, ch)} != ledger {getattr(want, ch)}"
            )
    if got.utility != want.utility:
        raise ValueError(f"utility: tuple {got.utility} != ledger {want.utility}")


# ---------------------------------------------------------------------------
# The shippable report
# ---------------------------------------------------------------------------

def _fmt(v: Fraction) -> str:
    return str(v)


def _channel_bits(ch: Mapping[str, Fraction]) -> str:
    live = [f"{k}={_fmt(v)}" for k, v in ch.items() if v]
    return ", ".join(live) if live else "-"


def tuple_report(m: OffenseMachine | None = None) -> str:
    """The full specification: S, A, T, R_G, s0, F, and the realized run."""
    m = m if m is not None else build_thanos_tuple()
    motiv = m.motivation
    canon = m.canon_trajectory()
    all_traj = list(m.trajectories())
    L: list[str] = []

    def rule(title: str) -> None:
        L.append("")
        L.append(title)
        L.append("=" * 74)

    L.append("THANOS TUPLE — M = (S, A, T, R_G, s0, F)")
    L.append("=" * 74)
    L.append("A zero-sensitivity instantiation of the offense/harm formalism.")
    L.append("Canon scope: Infinity War + Endgame. No non-public parameters.")
    L.append("")
    L.append(f"G  : {m.goal.statement}")
    L.append(f"     means — {m.goal.means}")
    L.append("")
    L.append("s = (position, K) where K is the set of stones socketed so far.")
    L.append("T : S x A -> S is partial and deterministic; an edge is admissible")
    L.append("only if every affordance it invokes is already in K.")

    rule("S — states")
    by_pos: dict[str, list[CampaignState]] = {}
    for s in m.states:
        by_pos.setdefault(s.position, []).append(s)
    L.append(f"|S| = {len(m.states)} over {len(by_pos)} positions "
             f"(position x reachable keyring)")
    L.append("")
    for pos, ss in by_pos.items():
        keys = ", ".join(sorted(s.label.split("[", 1)[1][:-1] for s in ss))
        L.append(f"  {pos:<22} x{len(ss):<3} K in {{{keys}}}")

    rule("A — action space")
    for kind in (ActionKind.OFFENDER, ActionKind.AFFORDANCE, ActionKind.INTERVENTION):
        rows = [a for a in m.actions.values() if a.kind is kind]
        L.append(f"{kind.value} ({len(rows)}):")
        for a in rows:
            req = m.requires.get(a.name)
            gate = f"  [requires {req}]" if req else ""
            L.append(f"  {a.name:<22} {a.description}{gate}")
        L.append("")
    L.append("A is state-indexed: A(s) = {a : T(s,a) defined}. Affordance gating")
    L.append("makes the growth of A along the trajectory computable, e.g.")
    for probe in (m.initial,
                  CampaignState(GAUNTLET_STAGING, frozenset({"power"})),
                  CampaignState(GAUNTLET_STAGING, frozenset({"power", "space"}))):
        names = ", ".join(a.name for a in m.admissible_actions(probe)) or "-"
        L.append(f"  A({probe.label}) = {{{names}}}")

    rule("T — transition function")
    L.append(f"|T| = {len(m.edges)} transitions. Grouped by source position:")
    L.append("")
    order: list[str] = []
    groups: dict[str, list[TupleEdge]] = {}
    for e in m.edges:
        if e.source.position not in groups:
            groups[e.source.position] = []
            order.append(e.source.position)
        groups[e.source.position].append(e)
    for pos in order:
        L.append(f"  from {pos}:")
        rows = sorted(groups[pos], key=lambda e: (len(e.source.keyring), e.action))
        for e in rows:
            co = f"  +{'+'.join(e.co_labels)}" if e.co_labels else ""
            L.append(f"    T({e.source.label}, {e.action}) = {e.target.label}{co}")

    rule("R_G — reward")
    L.append("Channels: progress (capability), personal_cost, lock_in,")
    L.append("goal_attainment (enactment). U = <w, R_G> with")
    L.append(f"  w = (progress={motiv.w_progress}, personal_cost={motiv.w_personal_cost}, "
             f"lock_in={motiv.w_lock_in}, goal_attainment={motiv.w_goal_attainment})")
    L.append("w_goal_attainment > w_progress, so enactment strictly dominates any")
    L.append("capability subtotal: a full unsnapped gauntlet is not the goal.")

    rule("s0 and F")
    L.append(f"  s0 = {m.initial.label}")
    for s, p in m.terminals.items():
        note = ""
        if m.successors(s):
            note = "   (terminal-capable; the composite trajectory continues through it)"
        L.append(f"  F  ∋ {s.label:<28} polarity={p.value}{note}")

    rule("s0 -> F — the realized trajectory (the film)")
    L.append("Every transition taken, its reward, and the running total.")
    L.append("")
    width = max(len(s.label) for s in canon.states)
    head = (f"{'#':>2}  {'state':<{width}} {'action':<20} {'R_G on edge':<22} "
            f"{'cum. U':>7}")
    L.append(head)
    L.append("-" * len(head))
    for row in canon.ledger(motiv):
        e = row["edge"]
        assert isinstance(e, TupleEdge)
        ch = row["channels"]
        assert isinstance(ch, dict)
        L.append(f"{row['step']:>2}  {e.source.label:<{width}} {e.action:<20} "
                 f"{_channel_bits(ch):<22} {str(row['cumulative_utility']):>7}")
    L.append(f"    {canon.states[-1].label:<{width}} {'(terminal)':<20}")
    L.append("")
    acct = canon.account(motiv)
    L.append(f"Cumulative R_G: progress={acct.progress}  "
             f"personal_cost={acct.personal_cost}  lock_in={acct.lock_in}  "
             f"goal_attainment={acct.goal_attainment}")
    L.append(f"Return U(sigma) = {acct.utility} = {float(acct.utility):.2f}   "
             f"terminal polarity = {canon.polarity.value}")
    L.append("")
    L.append("Beats on the edges that move a channel:")
    for e in canon.edges:
        if e.reward is not None and any(e.channels().values()):
            L.append(f"  {e.source.label} -{e.action}-> {e.target.label}")
            L.append(f"      {e.reward.beat}")

    rule("Experiments over the tuple")
    orders = sorted(t.acquisition_order for t in all_traj)
    returns = {t.account(motiv).utility for t in all_traj}
    L.append(f"1. Acquisition orders admitted by affordance gating: {len(orders)}")
    for o in orders:
        mark = "  <- canon" if o == STONES else ""
        L.append(f"     {' -> '.join(o)}{mark}")
    L.append("   Space is forced first (every other approach is labelled")
    L.append("   a_space_skip in canon); reality precedes soul (Vormir coercion")
    L.append("   invokes a_reality_warp); time precedes mind (the Wakanda socket")
    L.append("   invokes a_time_reverse). Those three constraints, and nothing")
    L.append("   else, generate the lattice.")
    L.append("")
    shown = ", ".join(str(u) for u in sorted(returns))
    L.append(f"2. Return invariance: {len(returns)} distinct return(s) across all "
             f"{len(all_traj)} trajectories -> U = {shown}")
    L.append("   Re-ordering acquisitions is worth exactly nothing to the")
    L.append("   offender. Denying a *sequence* is not denying anything — the")
    L.append("   offender-side reading of affordance displacement (Law 4).")
    L.append("")
    nec = m.necessary_states()
    L.append(f"3. Necessary states (on every complete trajectory): {len(nec)}")
    for s in nec:
        L.append(f"     {s.label}")
    L.append("   These are the mandatory interdiction points: a guardian who can")
    L.append("   act at one of them gets a window whatever order the offender")
    L.append("   picks. The whole space layer is here, and it is early — the")
    L.append("   tuple's version of the contact-primacy argument.")
    L.append("")
    win = m.enactment_window()
    L.append(f"4. Enactment window: {len(win)} state(s)")
    for s in win:
        L.append(f"     {s.label}  progress={s.progress}, goal_attainment still 0")
    L.append("   Capability complete, goal not attained. It lies on every")
    L.append("   trajectory and it is the last state at which denial *prevents*")
    L.append("   rather than reprices. After the next edge, only remediation.")
    L.append("")
    L.append("5. Monte Carlo. The offender side has no chance transitions: T is")
    L.append("   deterministic, so sampling A(s) uniformly samples an acquisition")
    L.append("   order and nothing else — and by (2) every order returns the same")
    L.append("   U. Offender-side MC therefore has zero variance by construction.")
    L.append("   That is the finding, not a limitation: all the uncertainty in")
    L.append("   this campaign is guardian-side, which is where strange_search()")
    L.append("   samples (11 nodes, 16 leaves, P(win|uniform) = 1/14,000,605).")
    L.append("   The two objects answer different questions and stay separate.")

    rule("The predicate — is this trajectory exploitation?")
    v = m.verdict()
    ge = m.goal_realizing_edge()
    L.append("The predicate is NOT part of M. M is a goal-dependent offense/harm")
    L.append("machine; exploitation is a test applied to its trajectories.")
    L.append("")
    L.append(f"  goal-realizing edge : {ge.source.label} -{ge.action}-> {ge.target.label}")
    L.append(f"  benefit source      : {v.goal_edge_kind.value}")
    L.append(f"  EXPLOITATION        : {v.is_exploitation_trajectory}")
    L.append("")
    L.append(f"  {v.rationale}")
    L.append("")
    L.append("  Victim-sourced sub-patterns on the same trajectory:")
    for e in v.sourced_edges:
        L.append(f"    {e.source} -> {e.target}  [{e.victim}]")
    L.append("")
    L.append("  So: a fully specified tuple, a real trajectory, a real predicate,")
    L.append("  and a negative verdict. This is the worked example of an")
    L.append("  offense/harm machine that is NOT an ESM — the parent case the")
    L.append("  ESM specializes. See docs/FORMALISM.md §5-§6.")

    return "\n".join(L)


def tuple_report_cli() -> None:
    print(tuple_report())


if __name__ == "__main__":
    tuple_report_cli()

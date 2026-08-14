"""Generic offense/harm state-machine primitives.

Deliberately mirrors the CaseNoesis tuple M = (S, A, T, R_G, s0, F) —
the parent offense/harm formalism from which the exploitation-state-
machine (ESM) specialization adds the SEP extraction predicate (see
docs/FORMALISM.md §5). Includes the layered-trajectory extension: a
campaign is one harm event composed of multiple offense sub-trajectories.

Note: ``Phase.EXPLOITATION`` is Cornish crime-script backbone vocabulary
(contact → conditioning → exploitation → maintenance), not the SEP
"exploitation" predicate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Phase(str, Enum):
    """Backbone phases (CaseNoesis Law 2 vocabulary)."""

    INITIAL_CONTACT = "InitialContactPhase"
    CONDITIONING = "ConditioningPhase"
    EXPLOITATION = "ExploitationPhase"
    MAINTENANCE = "MaintenancePhase"


class Polarity(str, Enum):
    """Terminal polarity of a trajectory.

    CaseNoesis's traj:terminalPolarity is binary {completed, disrupted}.
    This campaign forces a third value: the harm event completes and is
    then reversed. See docs/ONTOLOGY.md.
    """

    COMPLETED = "completed"
    DISRUPTED = "disrupted"
    REMEDIATED = "remediated"  # completed, then reversed post-hoc


class ActionKind(str, Enum):
    OFFENDER = "offender_action"
    AFFORDANCE = "affordance"  # capability the environment (or a prior
    #                            acquisition) makes available
    INTERVENTION = "guardian_intervention"


@dataclass(frozen=True)
class Action:
    name: str
    kind: ActionKind
    description: str = ""


@dataclass(frozen=True)
class State:
    name: str
    phase: Phase | None = None  # None for exogenous / meta states
    layer: str | None = None  # which offense sub-trajectory this state
    #                           belongs to (layered extension)


@dataclass(frozen=True)
class Transition:
    source: str
    target: str
    actions: tuple[str, ...] = ()  # action names labelling the edge
    trigger: str = ""


@dataclass
class StateMachine:
    """Directed machine over offense phases."""

    states: dict[str, State] = field(default_factory=dict)
    actions: dict[str, Action] = field(default_factory=dict)
    transitions: list[Transition] = field(default_factory=list)
    initial: str = ""
    terminals: dict[str, Polarity] = field(default_factory=dict)

    def add_state(self, state: State) -> None:
        self.states[state.name] = state

    def add_action(self, action: Action) -> None:
        self.actions[action.name] = action

    def add_transition(self, transition: Transition) -> None:
        for a in transition.actions:
            if a not in self.actions:
                raise ValueError(f"unknown action {a!r} on edge "
                                 f"{transition.source}->{transition.target}")
        self.transitions.append(transition)

    def successors(self, state: str) -> list[Transition]:
        return [t for t in self.transitions if t.source == state]

    def validate(self) -> None:
        for t in self.transitions:
            if t.source not in self.states or t.target not in self.states:
                raise ValueError(f"dangling edge {t.source}->{t.target}")
        if self.initial not in self.states:
            raise ValueError("initial state not in S")
        for s in self.terminals:
            if s not in self.states:
                raise ValueError(f"terminal {s} not in S")

    def layers(self) -> set[str]:
        return {s.layer for s in self.states.values() if s.layer}


@dataclass
class TrajectoryStep:
    state: str
    transition: Transition | None  # edge taken to leave `state` (None at end)


@dataclass
class Trajectory:
    """A realized path sigma(L) = (s0, ..., sT) through the machine."""

    steps: list[TrajectoryStep]
    polarity: Polarity

    @property
    def states(self) -> list[str]:
        return [s.state for s in self.steps]

    def phases(self, machine: StateMachine) -> list[Phase]:
        out = []
        for s in self.steps:
            phase = machine.states[s.state].phase
            if phase is not None and (not out or out[-1] is not phase):
                out.append(phase)
        return out

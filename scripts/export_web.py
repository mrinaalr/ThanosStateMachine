"""Export web/public/data/* from the Python ESM for the static sandbox.

Regenerate before building the Vite app (CI does this on Pages deploy).
"""

from __future__ import annotations

import json
import shutil
from fractions import Fraction
from pathlib import Path

from thanos_state_machine import __version__
from thanos_state_machine.campaign import (
    STRANGE_FUTURES,
    ChanceNode,
    ChoiceNode,
    GuardianPolicy,
    analytic_win_probability,
    build_decision_tree,
    build_machine,
    guardian_offender_anchors,
    winning_line,
)
from thanos_state_machine.exploitation import campaign_verdict, classify_campaign_edges
from thanos_state_machine.search import failure_modes, interdiction_leverage

# Keep unlockedBy in sync with scripts/export_ttl.py
UNLOCKED_BY = {
    "a_space_skip": "SpaceExtraction",
    "a_reality_warp": "RealityExtraction",
    "a_time_reverse": "TimeExtraction",
}

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "public" / "data"
TTL_SRC = ROOT / "graphs" / "thanos_campaign.ttl"


def _frac(f: Fraction) -> dict:
    return {
        "n": f.numerator,
        "d": f.denominator,
        "approx": float(f),
        "label": f"{f.numerator}/{f.denominator}",
    }


def export_machine() -> dict:
    m = build_machine()
    edge_map = classify_campaign_edges()
    verdict = campaign_verdict()
    return {
        "initial": m.initial,
        "states": [
            {
                "id": s.name,
                "phase": s.phase.value if s.phase else None,
                "layer": s.layer,
                "terminal": m.terminals[s.name].value if s.name in m.terminals else None,
            }
            for s in m.states.values()
        ],
        "actions": [
            {
                "id": a.name,
                "kind": a.kind.value,
                "description": a.description,
                "unlockedBy": UNLOCKED_BY.get(a.name),
            }
            for a in m.actions.values()
        ],
        "transitions": [
            {
                "source": t.source,
                "target": t.target,
                "actions": list(t.actions),
                "trigger": t.trigger,
                "benefitKind": (
                    edge_map[(t.source, t.target)].kind.value
                    if (t.source, t.target) in edge_map
                    else None
                ),
            }
            for t in m.transitions
        ],
        "exploitation": {
            "isExploitation": verdict.is_exploitation_trajectory,
            "goalEdge": list(verdict.goal_edge),
            "goalEdgeKind": verdict.goal_edge_kind.value,
            "rationale": verdict.rationale,
            "note": (
                "SEP verdict: the Snap is destructive harm, not exploitation — "
                "victims are targets of elimination, not sources of benefit."
            ),
        },
    }


def export_tree() -> dict:
    tree = build_decision_tree()
    p_uni = analytic_win_probability(tree, GuardianPolicy.UNIFORM)
    p_opt = analytic_win_probability(tree, GuardianPolicy.OPTIMAL)
    anchors = {a.node: {
        "offenderStates": list(a.offender_states),
        "offenderEdges": [list(e) for e in a.offender_edges],
        "note": a.note,
    } for a in guardian_offender_anchors()}

    nodes = []
    for node in tree:
        if isinstance(node, ChoiceNode):
            nodes.append({
                "name": node.name,
                "kind": "choice",
                "branches": [
                    {
                        "label": b.label,
                        "outcome": b.outcome,
                        "description": b.description,
                        "surviving": b.outcome == "continue",
                    }
                    for b in node.branches
                ],
                "anchor": anchors.get(node.name),
            })
        else:
            assert isinstance(node, ChanceNode)
            nodes.append({
                "name": node.name,
                "kind": "chance",
                "pContinue": _frac(node.p_continue),
                "continueLabel": node.continue_label,
                "failDescription": node.fail_description,
                "anchor": anchors.get(node.name),
            })

    lev_u = interdiction_leverage(tree, GuardianPolicy.UNIFORM)
    lev_o = interdiction_leverage(tree, GuardianPolicy.OPTIMAL)

    return {
        "futures": STRANGE_FUTURES,
        "pWinUniform": _frac(p_uni),
        "pWinOptimal": _frac(p_opt),
        "winningLine": [{"node": n, "label": lab} for n, lab in winning_line(tree)],
        "nodes": nodes,
        "failureModes": [
            {
                "node": fm.node,
                "branch": fm.branch,
                "description": fm.description,
                "massUniform": _frac(fm.mass_uniform),
            }
            for fm in sorted(failure_modes(tree), key=lambda f: -f.mass_uniform)
        ],
        "leverage": {
            "uniform": [
                {
                    "node": L.node,
                    "kind": L.node_kind,
                    "reach": _frac(L.reach_mass),
                    "loss": _frac(L.loss_mass),
                    "continue": _frac(L.continue_mass),
                }
                for L in lev_u
            ],
            "optimal": [
                {
                    "node": L.node,
                    "kind": L.node_kind,
                    "reach": _frac(L.reach_mass),
                    "loss": _frac(L.loss_mass),
                    "continue": _frac(L.continue_mass),
                }
                for L in lev_o
            ],
        },
        "monteCarlo": {
            "seed": 42,
            "samples": STRANGE_FUTURES,
            "observedWins": 1,
            "note": (
                "Full enumeration with seed 42 observes exactly one win — "
                "matching the calibrated uniform measure."
            ),
        },
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    machine = export_machine()
    tree = export_tree()
    meta = {
        "version": __version__,
        "title": "ThanosStateMachine",
        "subtitle": "Zero-sensitivity CaseNoesis ESM sandbox",
        "quote": (
            "I went forward in time to view alternate futures. To see all the "
            "possible outcomes of the coming conflict."
        ),
        "attribution": "Doctor Strange — Avengers: Infinity War",
        "canon": ["Avengers: Infinity War (2018)", "Avengers: Endgame (2019)"],
        "research": {
            "program": "On the Mechanics of Exploitation / CaseNoesis",
            "role": (
                "Public fictional case record for training and demos — "
                "show the vocabulary here, then show what CaseLinker holds "
                "that must stay closed."
            ),
        },
    }

    (OUT / "machine.json").write_text(json.dumps(machine, indent=2) + "\n")
    (OUT / "tree.json").write_text(json.dumps(tree, indent=2) + "\n")
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    if TTL_SRC.exists():
        shutil.copy2(TTL_SRC, OUT / "thanos_campaign.ttl")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

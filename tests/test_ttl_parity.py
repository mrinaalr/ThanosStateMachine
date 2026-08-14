"""TTL ↔ build_machine() structural parity.

The ontology twin is hand-curated for research commentary, but its
from/to edges and action set must stay aligned with the Python machine.
"""

from __future__ import annotations

import re
from pathlib import Path

from thanos_state_machine.campaign import build_machine

TTL_PATH = Path(__file__).resolve().parents[1] / "graphs" / "thanos_campaign.ttl"
NS = "https://github.com/mrinaalr/ThanosStateMachine#"


def _local(uri_or_curie: str) -> str:
    uri_or_curie = uri_or_curie.strip().rstrip(" ;,.")
    if uri_or_curie.startswith("tsm:"):
        return uri_or_curie[4:]
    if uri_or_curie.startswith("<") and uri_or_curie.endswith(">"):
        uri_or_curie = uri_or_curie[1:-1]
    if uri_or_curie.startswith(NS):
        return uri_or_curie[len(NS):]
    return uri_or_curie.split("#")[-1]


def parse_ttl_graph(text: str) -> tuple[set[str], set[str], set[tuple[str, str]], set[str]]:
    """Return (states, actions, edges, enacted_actions) from a light parse.

    Good enough for this file's Turtle subset; not a general RDF parser.
    """
    states = set(re.findall(r"tsm:(\w+)\s+a\s+traj:State\b", text))
    actions = set(re.findall(r"tsm:(\w+)\s+a\s+traj:Action\b", text))

    edges: set[tuple[str, str]] = set()
    enacted: set[str] = set()
    # Split on transition subjects: tsm:t-... a traj:Transition
    blocks = re.split(r"(?=tsm:t-[\w-]+\s+a\s+traj:Transition)", text)
    for block in blocks:
        if "traj:Transition" not in block:
            continue
        frm = re.search(r"traj:fromState\s+(tsm:\w+)", block)
        to = re.search(r"traj:toState\s+(tsm:\w+)", block)
        if frm and to:
            edges.add((_local(frm.group(1)), _local(to.group(1))))
        for m in re.finditer(r"traj:enactsAction\s+([^;]+)", block):
            for curie in re.findall(r"tsm:\w+", m.group(1)):
                enacted.add(_local(curie))
    return states, actions, edges, enacted


def test_ttl_states_and_actions_cover_machine():
    text = TTL_PATH.read_text()
    ttl_states, ttl_actions, ttl_edges, ttl_enacted = parse_ttl_graph(text)
    m = build_machine()

    assert ttl_states == set(m.states)
    assert ttl_actions == set(m.actions)

    py_edges = {(t.source, t.target) for t in m.transitions}
    assert ttl_edges == py_edges

    py_enacted = {a for t in m.transitions for a in t.actions}
    assert ttl_enacted == py_enacted


def test_export_ttl_roundtrip_matches_checked_in_graph():
    """Checked-in TTL must be the exporter output (no silent hand drift)."""
    import sys

    sys.path.insert(0, str(TTL_PATH.parents[1] / "scripts"))
    from export_ttl import to_ttl  # type: ignore

    assert to_ttl() == TTL_PATH.read_text()


def test_unlocked_by_marks_dynamic_affordances():
    text = TTL_PATH.read_text()
    assert "tsm:a_reality_warp" in text and "tsm:unlockedBy tsm:RealityExtraction" in text
    assert "tsm:a_time_reverse" in text and "tsm:unlockedBy tsm:TimeExtraction" in text
    assert "tsm:a_space_skip" in text and "tsm:unlockedBy tsm:SpaceExtraction" in text

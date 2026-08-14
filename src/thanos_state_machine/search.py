"""Exact analysis of the guardian decision problem.

``strange_report()`` is the headline: exact win probabilities under
uniform and optimal play, the unique winning line, and every distinct
failure mode with its probability mass. No sampling here — this is the
dynamic-programming view of what Strange did on Titan.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .campaign import (
    ChanceNode,
    ChoiceNode,
    Node,
    STRANGE_FUTURES,
    analytic_win_probability,
    build_decision_tree,
    winning_line,
)


@dataclass(frozen=True)
class FailureMode:
    node: str
    branch: str
    description: str
    mass_uniform: Fraction  # probability mass under uniform guardian play


def failure_modes(tree: list[Node] | None = None) -> list[FailureMode]:
    """Every distinct way the future is lost, with exact mass.

    Masses plus the win probability sum to 1 (checked in tests).
    """
    tree = tree if tree is not None else build_decision_tree()
    out: list[FailureMode] = []
    reach = Fraction(1)  # probability of having survived to the current node
    for node in tree:
        if isinstance(node, ChoiceNode):
            per_branch = reach * Fraction(1, len(node.branches))
            for b in node.branches:
                if b.outcome != "continue":
                    out.append(FailureMode(node.name, b.label, b.description,
                                           per_branch))
            reach = per_branch  # exactly one continue branch
        else:
            out.append(FailureMode(node.name, "chance_fails",
                                   node.fail_description,
                                   reach * (1 - node.p_continue)))
            reach *= node.p_continue
    return out


def strange_report() -> str:
    tree = build_decision_tree()
    p_uni = analytic_win_probability(tree, "uniform")
    p_opt = analytic_win_probability(tree, "optimal")
    lines = [
        "STRANGE REPORT — exact analysis of the guardian decision problem",
        "=" * 66,
        f"futures examined (measure denominator): {STRANGE_FUTURES:,}",
        f"P(win | uniform guardian policy) = {p_uni} "
        f"(~1 in {int(round(1 / float(p_uni))):,})",
        f"P(win | optimal guardian policy) = {p_opt} "
        f"(~1 in {int(round(1 / float(p_opt))):,})",
        "",
        "The winning line (there is exactly one):",
    ]
    for node, label in winning_line(tree):
        lines.append(f"  {node:24s} -> {label}")
    lines.append("")
    lines.append("Failure modes under uniform play (mass, most likely first):")
    for fm in sorted(failure_modes(tree), key=lambda f: -f.mass_uniform):
        lines.append(f"  {float(fm.mass_uniform):.6f}  {fm.node}:{fm.branch}"
                     f" — {fm.description}")
    total = sum((f.mass_uniform for f in failure_modes(tree)), Fraction(0))
    lines.append("")
    lines.append(f"mass check: losses {float(total):.9f} + win {float(p_uni):.9f}"
                 f" = {float(total + p_uni):.9f}")
    return "\n".join(lines)


def strange_report_cli() -> None:
    print(strange_report())


if __name__ == "__main__":
    strange_report_cli()

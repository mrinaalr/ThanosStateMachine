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
    STRANGE_FUTURES,
    ChoiceNode,
    GuardianPolicy,
    Node,
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


@dataclass(frozen=True)
class NodeLeverage:
    """Probability mass at a guardian tree node under a policy."""

    node: str
    node_kind: str  # "choice" | "chance"
    reach_mass: Fraction       # P(reach this node)
    loss_mass: Fraction        # P(terminate in loss at this node)
    continue_mass: Fraction    # P(survive past this node)


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


def interdiction_leverage(
    tree: list[Node] | None = None,
    policy: GuardianPolicy | str = GuardianPolicy.UNIFORM,
) -> list[NodeLeverage]:
    """Per-node probability mass: reach, loss-at-node, and survival.

    Under uniform play, ``loss_mass`` at early choice nodes dominates —
    the Bellman-side argument for contact-phase intervention
    (FORMALISM §4). Under optimal play, all choice-node ``loss_mass``
    is zero; only chance nodes retain stochastic loss.
    """
    tree = tree if tree is not None else build_decision_tree()
    if isinstance(policy, str):
        policy = GuardianPolicy(policy)
    out: list[NodeLeverage] = []
    reach = Fraction(1)
    for node in tree:
        if isinstance(node, ChoiceNode):
            if policy is GuardianPolicy.UNIFORM:
                per = reach * Fraction(1, len(node.branches))
                loss = reach - per
                out.append(NodeLeverage(node.name, "choice", reach, loss, per))
                reach = per
            else:
                out.append(NodeLeverage(node.name, "choice", reach,
                                        Fraction(0), reach))
        else:
            cont = reach * node.p_continue
            loss = reach - cont
            out.append(NodeLeverage(node.name, "chance", reach, loss, cont))
            reach = cont
    return out


def absorbing_outcome_count(tree: list[Node] | None = None) -> int:
    """Distinct absorbing outcomes: failure modes + the single win leaf."""
    tree = tree if tree is not None else build_decision_tree()
    return len(failure_modes(tree)) + 1


def strange_report() -> str:
    tree = build_decision_tree()
    p_uni = analytic_win_probability(tree, GuardianPolicy.UNIFORM)
    p_opt = analytic_win_probability(tree, GuardianPolicy.OPTIMAL)
    modes = failure_modes(tree)
    lines = [
        "STRANGE REPORT — exact analysis of the guardian decision problem",
        "=" * 66,
        f"futures examined (measure denominator): {STRANGE_FUTURES:,}",
        f"absorbing outcomes (loss modes + win): {absorbing_outcome_count(tree)}",
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
    lines.append("Interdiction leverage under uniform play (loss mass):")
    for lev in sorted(interdiction_leverage(tree), key=lambda lev: -lev.loss_mass):
        if lev.loss_mass:
            lines.append(f"  {float(lev.loss_mass):.6f}  {lev.node}"
                         f" ({lev.node_kind})")
    lines.append("")
    lines.append("Failure modes under uniform play (mass, most likely first):")
    for fm in sorted(modes, key=lambda f: -f.mass_uniform):
        lines.append(f"  {float(fm.mass_uniform):.6f}  {fm.node}:{fm.branch}"
                     f" — {fm.description}")
    total = sum((f.mass_uniform for f in modes), Fraction(0))
    lines.append("")
    lines.append(f"mass check: losses {float(total):.9f} + win {float(p_uni):.9f}"
                 f" = {float(total + p_uni):.9f}")
    return "\n".join(lines)


def strange_report_cli() -> None:
    print(strange_report())


if __name__ == "__main__":
    strange_report_cli()

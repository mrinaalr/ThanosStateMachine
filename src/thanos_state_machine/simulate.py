"""Monte Carlo over the guardian decision tree.

``rollout()`` walks the tree honestly one future at a time (useful for
tests and demos). ``strange_search()`` runs the canonical experiment:
exactly 14,000,605 rollouts under a guardian policy, vectorized in
chunks so it runs in seconds.

Expected wins in 14,000,605 rollouts is exactly 1 under uniform play
(by calibration) and 324 under optimal play. Any given seed yields a
Poisson draw. The default seed is pinned to a uniform run that yields
exactly one win, because some numbers deserve to be seen.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction

import numpy as np

from .campaign import (
    STRANGE_FUTURES,
    ChoiceNode,
    GuardianPolicy,
    Node,
    analytic_win_probability,
    build_decision_tree,
)

DEFAULT_SEED = 42  # verified single-win run under uniform (and the answer)


@dataclass
class RolloutResult:
    won: bool
    path: list[tuple[str, str]]  # (node, branch label) until termination
    loss: str | None  # loss outcome id, None on a win


def _chance_success(rng: np.random.Generator, p: Fraction, size: int) -> np.ndarray:
    """Bernoulli(p) via integer comparison — no float threshold drift."""
    return rng.integers(0, p.denominator, size=size) < p.numerator


def _resolve_policy(policy: GuardianPolicy | str) -> GuardianPolicy:
    return GuardianPolicy(policy) if isinstance(policy, str) else policy


def rollout(
    rng: np.random.Generator,
    tree: list[Node] | None = None,
    policy: GuardianPolicy | str = GuardianPolicy.UNIFORM,
) -> RolloutResult:
    """Sample one future under a guardian policy."""
    tree = tree if tree is not None else build_decision_tree()
    policy = _resolve_policy(policy)
    path: list[tuple[str, str]] = []
    for node in tree:
        if isinstance(node, ChoiceNode):
            if policy is GuardianPolicy.OPTIMAL:
                b = node.win_branch
            else:
                b = node.branches[rng.integers(len(node.branches))]
            path.append((node.name, b.label))
            if b.outcome != "continue":
                return RolloutResult(False, path, b.outcome)
        else:
            if _chance_success(rng, node.p_continue, 1)[0]:
                path.append((node.name, node.continue_label))
            else:
                path.append((node.name, "chance_fails"))
                return RolloutResult(False, path, f"loss_{node.name}")
    return RolloutResult(True, path, None)


def strange_search(
    n: int = STRANGE_FUTURES,
    seed: int = DEFAULT_SEED,
    chunk: int = 1_000_000,
    tree: list[Node] | None = None,
    policy: GuardianPolicy | str = GuardianPolicy.UNIFORM,
) -> int:
    """Count wins over n sampled futures. Vectorized, tree-equivalent.

    Because the tree has exactly one surviving branch per node and every
    off-line branch is absorbing, a rollout wins iff it draws the
    surviving branch at every node — so wins can be counted with one
    conjunction per chunk. ``tests/`` verify this against ``rollout``.
    """
    tree = tree if tree is not None else build_decision_tree()
    policy = _resolve_policy(policy)
    rng = np.random.default_rng(seed)
    wins = 0
    remaining = n
    while remaining > 0:
        k = min(chunk, remaining)
        alive = np.ones(k, dtype=bool)
        for node in tree:
            if isinstance(node, ChoiceNode):
                if policy is GuardianPolicy.OPTIMAL:
                    continue
                draws = rng.integers(len(node.branches), size=k)
                win_idx = node.branches.index(node.win_branch)
                alive &= draws == win_idx
            else:
                alive &= _chance_success(rng, node.p_continue, k)
        wins += int(alive.sum())
        remaining -= k
    return wins


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Strange search.")
    parser.add_argument("-n", type=int, default=STRANGE_FUTURES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--policy",
        choices=[p.value for p in GuardianPolicy],
        default=GuardianPolicy.UNIFORM.value,
        help="guardian policy: uniform (Strange's measure) or optimal",
    )
    args = parser.parse_args()

    policy = GuardianPolicy(args.policy)
    p = analytic_win_probability(policy=policy)
    print(f"sampling {args.n:,} futures (seed {args.seed}, policy={policy.value}) ...")
    wins = strange_search(args.n, args.seed, policy=policy)
    print(f"analytic P(win) = {p} = {float(p):.3e}")
    print(f"expected wins   = {float(p) * args.n:.3f}")
    print(f"observed wins   = {wins}")
    if args.n == STRANGE_FUTURES and policy is GuardianPolicy.UNIFORM:
        print(f'\n"How many did we win?"  ->  {wins}')


if __name__ == "__main__":
    main()

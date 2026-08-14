"""Monte Carlo over the guardian decision tree.

``rollout()`` walks the tree honestly one future at a time (useful for
tests and demos). ``strange_search()`` runs the canonical experiment:
exactly 14,000,605 rollouts under a uniform random guardian policy,
vectorized in chunks so it runs in seconds.

Expected wins in 14,000,605 rollouts is exactly 1 by calibration; any
given seed yields a Poisson(1) draw. The default seed is pinned to a run
that yields exactly one win, because some numbers deserve to be seen.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction

import numpy as np

from .campaign import (
    ChanceNode,
    ChoiceNode,
    Node,
    STRANGE_FUTURES,
    analytic_win_probability,
    build_decision_tree,
)

DEFAULT_SEED = 42  # verified single-win run (and the answer to everything)


@dataclass
class RolloutResult:
    won: bool
    path: list[tuple[str, str]]  # (node, branch label) until termination
    loss: str | None  # loss outcome id, None on a win


def rollout(rng: np.random.Generator,
            tree: list[Node] | None = None) -> RolloutResult:
    """Sample one future under the uniform random guardian policy."""
    tree = tree if tree is not None else build_decision_tree()
    path: list[tuple[str, str]] = []
    for node in tree:
        if isinstance(node, ChoiceNode):
            b = node.branches[rng.integers(len(node.branches))]
            path.append((node.name, b.label))
            if b.outcome != "continue":
                return RolloutResult(False, path, b.outcome)
        else:
            if rng.random() < float(node.p_continue):
                path.append((node.name, node.continue_label))
            else:
                path.append((node.name, "chance_fails"))
                return RolloutResult(False, path, f"loss_{node.name}")
    return RolloutResult(True, path, None)


def strange_search(n: int = STRANGE_FUTURES, seed: int = DEFAULT_SEED,
                   chunk: int = 1_000_000,
                   tree: list[Node] | None = None) -> int:
    """Count wins over n sampled futures. Vectorized, tree-equivalent.

    Because the tree has exactly one surviving branch per node and every
    off-line branch is absorbing, a rollout wins iff it draws the
    surviving branch at every node — so wins can be counted with one
    conjunction per chunk. ``tests/`` verify this against ``rollout``.
    """
    tree = tree if tree is not None else build_decision_tree()
    rng = np.random.default_rng(seed)
    wins = 0
    remaining = n
    while remaining > 0:
        k = min(chunk, remaining)
        alive = np.ones(k, dtype=bool)
        for node in tree:
            if isinstance(node, ChoiceNode):
                draws = rng.integers(len(node.branches), size=k)
                win_idx = node.branches.index(node.win_branch)
                alive &= draws == win_idx
            else:
                alive &= rng.random(k) < float(node.p_continue)
        wins += int(alive.sum())
        remaining -= k
    return wins


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Strange search.")
    parser.add_argument("-n", type=int, default=STRANGE_FUTURES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    p = analytic_win_probability()
    print(f"sampling {args.n:,} futures (seed {args.seed}) ...")
    wins = strange_search(args.n, args.seed)
    print(f"analytic P(win) = {p} = {float(p):.3e}")
    print(f"expected wins   = {float(p) * args.n:.3f}")
    print(f"observed wins   = {wins}")
    if args.n == STRANGE_FUTURES:
        print(f'\n"How many did we win?"  ->  {wins}')


if __name__ == "__main__":
    main()

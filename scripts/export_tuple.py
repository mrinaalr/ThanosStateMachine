"""Regenerate graphs/thanos_tuple.json from the tuple definition.

The JSON is the language-neutral form of M = (S, A, T, R_G, s0, F) — the
artifact you hand to a collaborator who is not going to install the package.
Generated, never hand-edited; ``tests/test_formalism.py`` fails on drift.
"""

import json
from pathlib import Path

from thanos_state_machine.formalism import build_thanos_tuple


def to_json() -> str:
    return json.dumps(build_thanos_tuple().to_dict(), indent=2) + "\n"


if __name__ == "__main__":
    target = Path(__file__).resolve().parent.parent / "graphs" / "thanos_tuple.json"
    target.write_text(to_json())
    print(f"wrote {target}")

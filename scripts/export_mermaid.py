"""Regenerate docs/campaign.mermaid from the machine definition."""

from pathlib import Path

from thanos_state_machine.campaign import build_machine
from thanos_state_machine.machine import Polarity

LAYER_ORDER = ["campaign", "space", "reality", "soul", "time", "mind"]


def to_mermaid() -> str:
    m = build_machine()
    lines = ["stateDiagram-v2"]
    for layer in LAYER_ORDER:
        if layer == "campaign":
            continue
        lines.append(f"    state {layer}_stone {{")
        for t in m.transitions:
            s, d = m.states[t.source], m.states[t.target]
            if s.layer == layer and d.layer == layer:
                label = ", ".join(t.actions) if t.actions else ""
                lines.append(f"        {t.source} --> {t.target}"
                             + (f" : {label}" if label else ""))
        lines.append("    }")
    lines.append(f"    [*] --> {m.initial}")
    for t in m.transitions:
        s, d = m.states[t.source], m.states[t.target]
        if s.layer == d.layer and s.layer != "campaign":
            continue
        label = ", ".join(t.actions) if t.actions else t.trigger
        src = f"{s.layer}_stone" if s.layer != "campaign" else t.source
        dst = f"{d.layer}_stone" if d.layer != "campaign" else t.target
        lines.append(f"    {src} --> {dst}" + (f" : {label}" if label else ""))
    for term, pol in m.terminals.items():
        if pol is not Polarity.COMPLETED:  # SnapEvent also continues
            lines.append(f"    {term} --> [*]")
    # de-duplicate cross-layer edges (five extraction->Snap edges collapse)
    seen, out = set(), []
    for line in lines:
        if line in seen and "-->" in line:
            continue
        seen.add(line)
        out.append(line)
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    target = Path(__file__).resolve().parent.parent / "docs" / "campaign.mermaid"
    target.write_text(to_mermaid())
    print(f"wrote {target}")

# Thanos — statement of purpose

Public dialogue only. Films: *Avengers: Infinity War* (2018),
*Avengers: Endgame* (2019). This is the motive record the reward model
treats as given — closer to a complete self-statement than a redacted
charging document, because the films show the interior.

## Goal (G)

**Randomly erase half of all life** so the remainder can live with finite
resources. He calls the terminal state *balance*.

Means on the path to G: obtain all six Infinity Stones → Snap → destroy
the stones so the outcome cannot be reversed.

G does not change when a stone is denied or a fight is lost. Path cost
changes; the goal does not.

## Motive lines (selected)

| Beat | Line |
|---|---|
| Ideology | “This universe is finite. Its resources, finite. If life is left unchecked, life will cease to exist. It needs correction.” |
| Terminal aesthetic | “Perfectly balanced, as all things should be.” |
| Destiny frame | “Dread it. Run from it. Destiny arrives all the same.” |
| Will / cost | “The hardest choices require the strongest wills.” |
| Vormir | “I ignored my destiny once. I cannot do that again. Even for you. I'm sorry, Gamora.” |
| After Vormir | “Today, I lost more than you can know. But now is no time to mourn.” |
| Titan / Stark | “You have my respect, Stark. When I'm done, half of humanity will still be alive. I hope they remember you.” |
| Garden | “I used the stones to destroy the stones. It nearly killed me. But the work is done. It always will be.” |

## What the reward model has to hold

1. **Progress toward G** — each stone socket moves progress; the Snap
   completes it; Garden *locks* it.
2. **Personal cost** — Gamora. The Soul Stone edge advances the campaign
   *and* books grief. If reward is a single number, that simultaneous
   fact disappears.
3. **Instrumental bargain** — Stark is spared on Titan because Strange
   trades the Time Stone for him. Respect is real in the text; the
   ranking is still G. Sparing Stark is not a competing terminal goal.

## Channels (implemented)

```
R_edge = (Δprogress, personal_cost, lock_in)
utility = w_p·Δprogress + w_c·personal_cost + w_ℓ·lock_in
```

Defaults: `w_p=1`, `w_c=0.2`, `w_ℓ=0.5`. Destiny dominates *full-path*
ranking; personal cost remains visible on its own channel.

### Stress finding (Vormir)

Under those weights, the Gamora sacrifice + Soul socket package is
**locally negative**. Thanos still takes it because without Soul, stone
progress caps at 5/6 — G is unreachable. So either:

- grief weight is lower than we set, or
- choice is not local-greedy: edges are taken for **path enablement**,
  not only for immediate utility.

A scalar `R` that only scores the next edge cannot hold the beat cleanly.
Multi-channel R + “required for completing paths” can.

See `thanos_state_machine.reward` and `thanos-reward` CLI.

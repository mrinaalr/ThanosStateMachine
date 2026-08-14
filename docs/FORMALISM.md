# Formalism

The campaign is modeled twice, deliberately: once from the offender side
(the ESM), once from the guardian side (the decision tree). The research
claim being stress-tested is that these are two views of one object —
the offender machine defines the environment; the guardian policy space
is a search over interdiction points on its transitions.

## 1. Offender side: M = (S, A, T, R_G, s0, F)

Following the CaseNoesis exploitation state machine, with the layered
trajectory extension carrying most of the weight:

- **S** — offense-phase states, in two kinds of layer: five per-stone
  offense sub-trajectories (space, reality, soul, time, mind), each with
  the pattern *Approach → Coercion → Extraction*, plus a campaign layer
  (*CampaignInitiation → SnapEvent → GardenWithdrawal → RemediationBattle
  → CampaignRemediated*).
- **A** — offender actions and affordances. The interesting deviation
  from the elder-fraud instantiation: **A is not static.** Each
  extraction unlocks an affordance that labels later transitions
  (Reality defeats Gamora on Vormir; Time reverses the Mind Stone's
  destruction in Wakanda). Affordance accumulation is representable in
  the `traj:` vocabulary but absent from prior instantiations.
- **T** — affordance-labeled transitions, including cross-layer labels
  (a sibling layer's extraction enables this layer's coercion).
- **R_G** — goal-conditioned progress toward the Snap; G = {balance the
  universe}, fixed. Denial branches never modify g, only trajectory cost
  (Law 4 by construction).
- **s0** — CampaignInitiation. Power Stone acquisition (Xandar) is
  exogenous, modeled as a prior activity feeding s0 — exactly as the
  elder scheme models purchased victim lists.
- **F** — {SnapEvent (completed), CampaignRemediated (remediated)}.

## 2. Guardian side: the decision tree Strange searched

An ordered sequence of nodes, one per interdiction opportunity on the
offender machine's transitions. Choice nodes are guardian decisions
(uniform under the "random policy" measure); chance nodes are the
environment. Every branch off the surviving line is absorbing loss.
There is exactly one winning leaf, and it passes **through** SnapEvent —
the win is remediation, not prevention.

| node | kind | branches / p | on the winning line |
|---|---|---|---|
| statesman_response | choice | 3 | Heimdall spends the Bifrost on the warning |
| nidavellir_forge | chance | 1/2 | Stormbreaker is forged |
| knowhere_response | choice | 3 | confrontation; Gamora is taken |
| titan_decision | choice | 3 | Strange trades the Time Stone for Stark |
| wakanda_strike | choice | 2 | Thor aims for the chest |
| garden_ambush | choice | 2 | decapitation; stones confirmed destroyed |
| quantum_rat | chance | 20736/14000605 | the rat frees Lang |
| heist_assignment | choice | 3 | canon team split |
| tesseract_recovery | chance | 1/2 | the 1970 detour works |
| gauntlet_keepaway | chance | 1/4 | the gauntlet stays moving |
| stark_seizure | chance | 1/2 | "I am Iron Man" |

### The load-bearing rat

Calibration rule: all branchings and chance weights are fixed at
natural values first; the one probability canon does not constrain — the
rat opening the quantum van — absorbs the residual so that

P(win | uniform policy) = (1/324) · (1/64) · p_rat = **1/14,000,605** exactly,

giving p_rat = 20736/14000605 ≈ 1/675. Under optimal (Strange) play the
choice factor collapses and P(win) = 324/14,000,605 ≈ **1 in 43,212**:
even perfect decisions leave the outcome hostage to four coin flips and
a rodent. Strange's number is a statement about the *measure over
policies*, not about fate.

The 14,000,605 is a probability denominator, not a leaf count — the tree
has 16 leaves. Strange sampled futures; he did not enumerate leaves.

## 3. The four laws, stress-tested against canon

- **Law 1 (Contact Primacy)** — holds. Every stone layer opens with a
  contact event with the current holder. No extraction occurs without
  one.
- **Law 2 (Backbone Invariance)** — holds, but only under the layered
  reading, and that is a real finding. No single layer contains the full
  backbone: stone layers have contact/conditioning/exploitation but no
  maintenance; the campaign layer's maintenance phase (GardenWithdrawal
  — destroying the stones to make the harm irreversible) has no contact
  phase of its own. Backbone invariance survives **only as a property of
  the composite trajectory**, which sharpens what "complete trajectory"
  must mean in the law's statement.
- **Law 3 (Type Invariance)** — holds. Each new affordance (stone)
  reprices later transitions without changing the exploitation type or
  the goal.
- **Law 4 (Affordance Displacement)** — holds by construction and is
  the reason the tree has its shape: every denial branch (evacuate
  Gamora, destroy the Time Stone) leads to regroup-and-complete, not to
  goal abandonment. Denial is displacement, not defeat — which is
  exactly why the only winning line runs through the harm state.

## 4. What the case adds to the research

1. **Remediation as a terminal polarity.** completed/disrupted is not
   exhaustive: a trajectory can complete and then be reversed. Real
   analogues exist (funds clawed back post-laundering; CSAM distribution
   completed, then seized and delisted). The vocabulary should say so.
2. **Dynamic affordance environments.** A grows along the trajectory.
   Elder-scheme A is static; real offenders also acquire capabilities
   mid-trajectory (a compromised account enables the next contact).
3. **Guardian side as a first-class object.** Kill-chain analysis (AfH
   Q3) becomes computable once the guardian policy space is explicit:
   interdiction leverage per transition is just sensitivity of P(win)
   to the node's parameters.
4. **A caution about optimal-path claims.** Under uniform play the two
   most massive failure modes sit at the *first* node (the warning) —
   66.7% of all futures die at the earliest interdiction point. Early
   transitions dominate outcome mass, which is the Bellman-side argument
   for contact-phase intervention.

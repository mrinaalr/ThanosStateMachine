# Formalism

The campaign is modeled twice, deliberately: once from the offender side
(the ESM), once from the guardian side (the decision tree). The research
claim being stress-tested is that these are two views of one object —
the offender machine defines the environment; the guardian policy space
is a search over interdiction points on its transitions.

## 1. Offender side: M = (S, A, T, R_G, s0, F)

- **S** — offense-phase states: five per-stone sub-trajectories (space,
  reality, soul, time, mind), each *Approach → Coercion → Extraction*,
  plus a campaign layer (*CampaignInitiation → SnapEvent →
  GardenWithdrawal → RemediationBattle → CampaignRemediated*).
- **A** — offender actions and affordances. **A is not static:** each
  extraction unlocks a capability that labels later transitions (Reality
  on Vormir; Time in Wakanda).
- **T** — affordance-labeled transitions, including cross-layer labels.
- **R_G** — multi-channel, goal-conditioned reward (see
  [THANOS_PURPOSE.md](THANOS_PURPOSE.md)). Channels:
  - `Δprogress` toward G (stone sockets; Power exogenous at open) —
    this is *capability*, not the goal,
  - `personal_cost` ≤ 0 (Vormir / Gamora),
  - `lock_in` (Garden stone-destruction),
  - `goal_attainment` (the Snap itself — *enactment*, booked only on
    the `SnapEvent → GardenWithdrawal` edge, and weighted to strictly
    dominate any capability subtotal).
  Scalar utility collapses channels with fixed weights so destiny still
  ranks the path; the Gamora beat is only visible if channels stay
  separate. G itself never rewrites under denial — only path cost does.
- **s0** — CampaignInitiation. Power Stone (Xandar) is exogenous, feeding
  s0.
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
  backbone: stone layers have contact/conditioning/harm execution but no
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
   interdiction leverage per transition is sensitivity of P(win) to the
   node's parameters — implemented as ``interdiction_leverage()`` in
   ``search.py``, with guardian-to-offender anchors in
   ``guardian_offender_anchors()``.
4. **A caution about optimal-path claims.** Under uniform play the two
   most massive failure modes sit at the *first* node (the warning) —
   66.7% of all futures die at the earliest interdiction point. Early
   transitions dominate outcome mass, which is the Bellman-side argument
   for contact-phase intervention.
5. **Capability is not enactment.** `Δprogress` and `goal_attainment`
   are separate channels because they are separate facts. A full,
   unsnapped gauntlet scores `progress = 1, attainment = 0`. The gap
   between the last socket and the Snap is the final window in which
   denial still *prevents* rather than merely reprices — thin in canon,
   but the only one of its kind on the path.
6. **The exploitation predicate.** See §5: this case shows
   "exploitation" is a testable predicate over trajectories, not a name
   for the machine.

## 5. Is this actually exploitation?

Vocabulary: the backbone's third phase is ``HarmExecutionPhase``, not
``ExploitationPhase`` — see [ONTOLOGY.md](ONTOLOGY.md) §5.

Under the definition the research works from (Zwolinski, Ferguson &
Wertheimer, "Exploitation", *SEP*), **no — and that is the finding.**
To exploit is to take unfair advantage: A benefits, at B's expense,
where B is the *source* of the gain. Exploitation is extractive; A
draws benefit *from* B and leaves B worse off than fair treatment would.

The Snap fails that test. Thanos's benefit — "balance" — comes from the
victims' *removal*, not from anything drawn out of them. B's death
*triggers* the benefit; it is not *transferred into* it. Nothing is
extracted; the victims are erased. That is omnicide, not exploitation.
(Compare an arsonist's euphoria at a fire: the benefit causally depends
on the owner's loss, but nothing of the owner's is taken up into it.)

The criterion this yields is computable, and the repo implements it in
`thanos_state_machine.exploitation`:

> Is the victim a **source** of the offender's benefit (extraction),
> or a **target** of its elimination (destructive harm)?

Each edge's classification is **derived** from a stated
``BenefitAnatomy`` (transferred object, preexisting, value survives
victim) via ``derive_benefit_source()`` — not asserted per-edge. The
hard case that pins the rule: the Mind Stone taking kills Vision but is
still extraction (the stone predates him); the Snap kills billions and
is destruction (nothing transfers; benefit *is* absence).

A trajectory is *exploitative* iff its **goal-realizing** benefit is
victim-sourced. Running it on the campaign (`is-it-exploitation`)
returns `False`: the goal-realizing edge (`SnapEvent →
GardenWithdrawal`) is victim-targeted. But all five stone acquisitions
*are* victim-sourced — something is drawn out of a specific holder
(the Tesseract out of Loki, the Soul Stone out of Gamora's life, the
Time Stone out of Strange's bargain, the Mind Stone out of Vision's
head). So the campaign is an offense/harm trajectory that *contains*
exploitation-shaped sub-patterns.

Consequences for the research:

- **"Exploitation" is a predicate, not a label.** Nothing in the tuple
  `M = (S, A, T, R_G, s0, F)` checks whether A extracts unfair benefit
  from B. The machinery is an offense/harm-trajectory formalism;
  exploitation selects a subset of trajectories over it.
- **Backbone specificity.** The backbone appears here even though this
  is *not* exploitation — evidence that Backbone Invariance is a
  property of goal-directed offense generally, not of exploitation
  specifically. That narrows what the law actually claims.
- **A hierarchy, in Cornish's sense.** Crime scripts link
  hierarchically (universal → protoscript → track). The same move fits
  here: a generic goal-dependent offense machine as parent, with the
  ESM as the specialization that adds the extraction predicate.
- **Sorting power.** Source-vs-target cleanly separates
  sweatshop/fraud/CSEA (victim as source) from genocide/omnicide/terror
  (victim as target) — a line worth stating explicitly in the mechanics
  work.

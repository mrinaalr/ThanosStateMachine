# Ontology fit: does this belong in CASE/UCO?

Short answer: no — and that's the finding.

CASE/UCO is a cyber-investigation ontology. Its observable classes
(`uco-observable:*`), identity facets, and forensic provenance patterns
are scoped to real investigations of real digital evidence. A fictional
kinetic campaign has no legitimate claim on any of that vocabulary, and
`graphs/thanos_campaign.ttl` deliberately imports none of it.

What it *does* use is the CaseNoesis `traj:` extension — State,
Transition, `enactsAction`, Trajectory, `terminalPolarity` — plus plain
PROV for sourcing and a small project namespace (`tsm:`). The test this
constitutes: **the trajectory layer is supposed to be domain-agnostic
graph vocabulary. If it can only express real cyber cases, it is less
general than CaseNoesis claims.** Expressing a fully fictional,
non-technological campaign in `traj:` terms, with zero `uco-observable`
imports, is evidence the layering is clean — the trajectory vocabulary
does not secretly depend on its cyber substrate.

## Where it fits cleanly

- States with phase labels and layers; affordance-labeled transitions;
  exogenous prior activities feeding s0 (Xandar = purchased victim
  lists); trajectory instances with terminal states. All direct.
- PROV against films-as-source-documents works exactly like PROV against
  affidavits: the provenance layer is indifferent to whether the source
  narrates reality.

## Where it strains (each strain is research signal)

1. **`terminalPolarity` is binary; canon needs a third value.** The
   2018–2023 composite trajectory reaches the harm state and is then
   reversed. Neither "completed" nor "disrupted" is true of it. The TTL
   asserts `"remediated"` and flags it. Proposal: promote polarity to
   {completed, disrupted, remediated}, where remediated ⊃ completed.
2. **"Affordance" quietly means "technological affordance."** Here the
   affordances are stones, armies, and a sacrifice rite — capabilities,
   not platform features. The vocabulary accepts them without complaint,
   which means `traj:` never formally restricted the term. Decide on
   purpose: either affordance = platform capability (then ψ needs a
   domain axiom) or affordance = any misusable capability (then AfH's
   five are a subclass).
3. **Static A assumption.** Nothing in `traj:` forbids an edge labeled
   by an affordance unlocked in a sibling layer — but nothing marks it
   either. If affordance accumulation matters (it does — compromised
   accounts, laundered funds as working capital), the vocabulary wants
   an `unlockedBy` property linking an affordance to the extraction that
   produced it.
4. **Counterfactual mass has no home.** The 14,000,605 unrealized
   futures are policy-measure statements, not trajectories; RDF should
   hold only realized trajectories plus (maybe) a summary node for the
   policy analysis. Trying to materialize the tree in triples would be a
   category error — worth stating as a modeling norm before someone
   does it to a real corpus.
5. **The backbone's third phase is misnamed upstream.** CaseNoesis
   inherits Cornish's `ExploitationPhase`, where "exploitation" means
   only *the offense is executed*. That collides with the SEP sense —
   the victim as *source* of the offender's benefit — and the collision
   is not harmless: the Snap occupies the third phase, so it reads as
   exploitation by construction, even though it fails the SEP test.
   This repo emits `traj:phaseLabel "HarmExecutionPhase"` instead,
   leaving the backbone neutral and delegating the exploitation
   question to an explicit predicate. **Proposed upstream rename**; note
   this is a deliberate divergence from the current CaseNoesis
   vocabulary, so a consumer matching on the old string will not match
   these graphs.
6. **Multi-agent guardian coalitions.** `traj:` has no first-class
   guardian/roster concept; interventions here are just actions with a
   `guardianIntervention` flag. Fine for one campaign; thin for the
   general kill-chain program, where *who can act at which transition*
   is the whole question. This is probably the next real extension.

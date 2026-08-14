# Security & dual-use considerations

This repo models a fictional adversary (Thanos) *and* a fictional
defender coalition (the Avengers): the adversary reaches the harm state,
and the model searches the defender's policy space for the interventions
that *succeed* — the rare policies that disrupt and ultimately remediate
the harm — while every other policy lets the adversary's trajectory run
to completion (adversary success, i.e. evasion of the defense). That is
a different posture from the offender-centric
exploitation state machine (ESM) in the underlying research, which
models offenders in order to show defenders *where to intervene*. The
difference is worth taking seriously rather than waving away, so this
document states the threat model plainly, locates the one genuine seam,
and fixes the boundary this project will not cross.

It builds directly on the risk analysis in *CaseLinker: 5 Sources, 500
Cases, and Scaling Considerations* (Technical Report #3, April 2026) —
the utility-asymmetry argument, source-bounded risk, and "operational
signal ≈ 0" — and extends that analysis from *aggregation* risk to
*two-sided modeling* risk.

## 1. The concern, stated precisely

The offender-only ESM is defender-facing: it answers *where do offenders
go*, which helps guardians intervene. A two-sided model that includes
the defender adds a new answerable question: *where is the defender
weakest* — i.e., the per-node probability that guardian action fails.
The fear is that an offender could instantiate the framework against
real law enforcement, read off the low-coverage transitions, and route
around them.

This concern is real in principle. The rest of this document argues that
the **risk lives entirely in the defender-side parameters, not in the
framework or its structure**, and that the boundary between "publishable
structure" and "non-publishable parameterization" is bright, statable,
and respected by this repo.

## 2. Why the framework itself carries ~zero operational signal

Three reasons, each an extension of the Scaling report's asymmetry.

**The structure is the offender's own crime script.** The phase backbone
(contact → conditioning → exploitation → maintenance) is Cornish's crime
script — a description of what offenders already do, derived from their
own lived procedure. An offender does not learn their own operation by
reading a state diagram of it. Publishing the *structure* transfers
nothing an active offender does not already possess. ∂U_A/∂(structure)
≈ 0.

**Evasion modeling without data is armchair speculation.** An offender
who instantiates a defender-side ESM from imagination is making the same
mental guesses about enforcement they would make anyway. The framework
does not improve a guess; it only sharpens an *estimate grounded in
data*. Absent the data, U_A is unchanged. This is the mirror of the
Scaling report's "an adversary reading all n = 500 cases derives the
same operational signal as reading 10: approximately zero."

**The asymmetry the defender enjoys is the data, not the math.** In the
real setting the defender holds what the offender does not: cyber-tip
volumes and clearance rates by phase, analyst and officer staffing,
inter-agency handoff latencies, undercover deployment triggers,
detection thresholds. These are the *transition probabilities and
action availabilities of the defender-side ESM.* They are exactly the
"operational signal" that public success narratives lack by
construction. The framework is a container; these values are the
contents; only the contents are sensitive.

## 3. The one genuine seam (and the line this repo draws)

The two-sided model does introduce something the offender-only model did
not: it makes the **defender's per-node failure probability a
first-class, computable object.** An offender-only ESM never asks "how
often does the guardian fail here"; a two-sided ESM must, because that
number is what the search optimizes against.

So the seam is not "modeling defenders." It is **populating the
defender side with real, non-public operational parameters and
publishing the result.** A defender-parameterized ESM is a targeting
map: it ranks interdiction points by weakness. That, and only that,
flips the utility asymmetry from ∂U_A ≈ 0 to ∂U_A > 0.

The boundary this project fixes as a norm:

- **Offender-side ESM — publishable, parameterized.** Built from public,
  redacted enforcement records, it is defender-facing and inherits the
  Scaling report's asymmetry. No change from current practice.
- **Defender-side ESM — publishable as *structure only*.** The phases,
  the action *types*, the graph shape may be shown. The *values* —
  transition probabilities, coverage rates, staffing, latencies,
  thresholds — must not be published when derived from non-public
  operational data. Publish them synthetic, canon-derived, or not at
  all.
- **Never publish a defender-side ESM whose parameters were estimated
  from non-public operational data.** That artifact is an evasion map
  regardless of how it is framed.

## 4. Why ThanosStateMachine is on the safe side of that line

This repo is a deliberate maximum-safety instance of the two-sided model,
which is why it is a suitable place to work out the norm:

- **The defender side is entirely public canon.** The Avengers' roster,
  actions, and "tradecraft" are the script of two films. There is no
  non-public operational parameter anywhere in it, so there is nothing
  to leak. The information asymmetry that protects real defenders is
  *absent here on purpose* — and its absence is exactly what makes the
  case publishable.
- **Every probability is calibrated, not measured.** The node weights
  exist to make P(win) = 1/14,000,605 come out exactly; they are fitted
  to a canon fact, not estimated from data about any real system. They
  transfer to nothing.
- **No real entity is modeled.** There is no jurisdiction, platform,
  agency, victim, or offender in this repo. Mosaic and re-identification
  risk are not merely source-bounded here; they are null.

Net: ThanosStateMachine demonstrates the two-sided formalism at
∂U_A = 0. It is a proof that the *machinery* is safe to publish; it says
nothing about the safety of any particular *parameterization*, which is
governed by the boundary in §3.

## 5. Guidance for extending the underlying research two-sidedly

If the ESM program later models defenders for real (e.g., to reason
about kill-chain coverage), the following keep it on the defender-facing
side of the line:

1. **Separate structure from parameters in publication.** Ship the
   defender graph shape; withhold or synthesize its values.
2. **Prefer sensitivity to point estimates.** "Contact-phase
   interventions dominate outcome mass" is a defender-useful invariant
   that does not hand an offender a coverage table. Publish invariants,
   not the underlying rates.
3. **Treat a defender-parameterized machine as an access-controlled
   artifact,** in the same tier the Scaling report reserves for
   elevated-sensitivity cases — not as a preprint appendix.
4. **Apply the offender-substitution test before release:** would an
   active offender, reading this, learn a *value* (not a structure) that
   improves their evasion estimate over a data-free guess? If yes, it is
   a parameterization, and §3 applies.
5. **Keep the reward asymmetry visible.** In this repo the only winning
   line runs *through* the harm state and ends in remediation, not
   prevention (Law 4: denial is displacement, not defeat). Modeling
   "the offender wins" is not a playbook when the model's lesson is that
   prevention-by-denial fails and interdiction leverage lives at the
   earliest contact phase. Frame two-sided results around that lesson.

## 6. On this repo specifically

Nothing in this repository is derived from, or transferable to, any real
investigation, agency, platform, or person. It is fiction, calibrated to
a fictional fact. Reports of a security concern in the *code* (dependency
issues, etc.) can be raised as normal issues. Concerns about the
*research direction* are the subject of this document and are better
raised with the author directly.

# Research context

This repository is a side project. It exists to stress-test the formal
machinery of an ongoing research program on the mechanics of
technology-mediated exploitation. This document orients a reader —
someone cloning the repo, a collaborator, a committee — on what that
program is and where ThanosStateMachine fits. It contains only public
research framing; nothing operational, and no working numbers from any
real case.

## The program

**Affordances for Harm (AfH).** An empirical study of Internet Crimes
Against Children enforcement records finding that, across platform
generations, offenders reuse a small, stable set of platform
*affordances* — capabilities a medium makes available, independent of
designer intent — and that the resulting harm trajectories are
foreseeable enough to design and police against. It introduces an
affordance → misuse → harm framing and asks where in a trajectory
intervention has the most leverage.
Preprint: https://doi.org/10.5281/zenodo.21347781

**CaseNoesis.** A research platform that ingests public enforcement
records (court filings, press releases), maps them to formal ontologies
(the CASE/UCO cyber-domain stack and a crimes-against-children
extension), and tests whether the AfH framing generalizes beyond child
exploitation to other technology-mediated offenses.
https://casenoesis.up.railway.app/

**Scaling Considerations (Technical Report #3).** A risk analysis of
aggregating public enforcement records, arguing a *utility asymmetry*:
defender value grows with corpus size while adversary value does not,
because public records are successful prosecutions and carry essentially
no operational signal (no failure modes, no tradecraft). This repo's
[SECURITY.md](../SECURITY.md) extends that argument from aggregation
risk to two-sided modeling risk.

## What "On the Mechanics of Exploitation" is doing

Prior work on how offenses unfold is largely *narrative*: crime scripts
and kill-chain models describe the stages an offense passes through,
after the fact. That is useful but limited — a description without
transition structure lets you recount an offense, but not *compute*
which stage is the highest-leverage point to disrupt.

"On the Mechanics of Exploitation" replaces the narrative stage model
with a formal one: an **Exploitation State Machine**,

    M = (S, A, T, R, s0, F)

— states as offense phases, actions as the ways affordances are misused,
transitions as movement between phases, a reward capturing progress
toward the offender's goal, an initial state, and terminal states. On
top of the machine sit three maps — φ (trajectory → exploitation type),
η (type → victim-facing harms), ψ (affordance → harms) — and a set of
candidate invariants (the "laws" and a theorem) stated with explicit
falsification criteria, so the model can be argued *wrong*.

The point of making it a machine rather than a script is exactly the
transition structure: with it you can ask formal questions the narrative
form cannot answer — which phases every trajectory must cross
(chokepoints), where interdiction effort pays off most, and how much a
new technology changes an offender's optimal path versus merely
re-pricing it.

The work aims to:

- **Instantiate the machine across several exploitation domains**
  (e.g. trafficking, fraud, cyber-enabled exploitation), each from
  public case corpora, to test whether structure derived in one domain
  holds in the others.
- **Build a kill-chain × abuse-pattern × technology matrix** that
  organizes, across domains, which technological capabilities are
  misused at which phase to produce which harms.
- **Derive a technology-safety scale** that ranks affordances by the
  risk they introduce at each stage of a trajectory — a design- and
  policy-facing output.

The throughline is a general, falsifiable, defender-facing theory of
technology-mediated harm: not a catalogue of tactics, but a structural
account of exploitation that says where to intervene and why. It is
positioned as the formal successor to AfH.

## Where this repository fits

ThanosStateMachine is a deliberately zero-sensitivity instance of the
same formalism, run on a fully public, fictional "case record" (the
Infinity Saga) with a canon-provided ground truth (one winning outcome
in 14,000,605). Because nothing here is real, it is a safe place to
exercise the machinery and probe its limits. Doing so surfaced several
findings that feed back into the real vocabulary — a needed third
terminal outcome ("remediated": harm completed, then reversed), dynamic
affordance environments (capabilities acquired mid-trajectory), the
observation that the phase backbone holds only on a composite layered
trajectory, and a worked example of why prevention-by-denial fails while
early-phase interdiction dominates. See [docs/FORMALISM.md](FORMALISM.md)
and [docs/ONTOLOGY.md](ONTOLOGY.md).

It is also a low-stakes exercise in agentic software development, built
end-to-end with agentic tooling.

## What this repository is not

Nothing here is derived from, or transferable to, any real
investigation, agency, platform, or person. All probabilities are
calibrated to a fictional fact, not measured from data. The dual-use
boundary this implies — publishable structure versus non-publishable
parameterization — is spelled out in [SECURITY.md](../SECURITY.md).

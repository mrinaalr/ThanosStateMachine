import type { MetaData } from '../types'

type Props = { meta: MetaData }

export function Briefing({ meta }: Props) {
  return (
    <div className="briefing">
      <article>
        <h3>What this sandbox is for</h3>
        <p>
          A zero-sensitivity walkthrough of the CaseNoesis offense/harm state-machine
          vocabulary on a fully public fictional case. Researchers and collaborators can
          click states, read affordances, run SPARQL, and see guardian search —
          without touching real victims, real records, or sensitive material.
        </p>
        <div className="callout">
          Demo order: show the machine here → open CaseLinker on a live case →
          explain what must stay closed (ICAC / sensitive material) and why the
          <em> structure </em> is shareable while the <em> parameterization </em> is not.
        </div>
      </article>

      <article>
        <h3>What you can do in this UI</h3>
        <ul>
          <li>
            <strong>Campaign</strong> — layered stone trajectories, dynamic
            affordances (<code>tsm:unlockedBy</code>), SEP non-exploitation verdict.
          </li>
          <li>
            <strong>Futures</strong> — Strange&apos;s decision tree, uniform vs optimal
            policy, interdiction leverage, Monte Carlo calibration check.
          </li>
          <li>
            <strong>SPARQL</strong> — query the campaign via the{' '}
            <code>traj:</code> trajectories vocabulary; fiction on purpose before
            CaseLinker.
          </li>
        </ul>
      </article>

      <article>
        <h3>Research frame</h3>
        <p>{meta.research.role}</p>
        <p>
          Program: {meta.research.program}. Canon: {meta.canon.join(' · ')}. Package
          version {meta.version}.
        </p>
        <p>
          Deeper reading in-repo:{' '}
          <a href="https://github.com/mrinaalr/ThanosStateMachine/blob/main/docs/RESEARCH_CONTEXT.md">
            RESEARCH_CONTEXT
          </a>
          ,{' '}
          <a href="https://github.com/mrinaalr/ThanosStateMachine/blob/main/docs/FORMALISM.md">
            FORMALISM
          </a>
          ,{' '}
          <a href="https://github.com/mrinaalr/ThanosStateMachine/blob/main/docs/ONTOLOGY.md">
            ONTOLOGY
          </a>
          .
        </p>
      </article>

      <article>
        <h3>How this sandbox informs the research</h3>
        <p>
          The <code>traj:</code> layer is meant to be domain-agnostic — this
          campaign is a stress test of that claim on fiction, not elder-fraud
          or ICAC. Along the way the sandbox motivated the SEP exploitation
          predicate (source vs target of benefit), guardian Monte Carlo and
          exact search over the offender transition space (uniform vs optimal
          policy, interdiction leverage), and the layered affordance machine
          the traj: graph exposes to SPARQL.
        </p>
      </article>
    </div>
  )
}

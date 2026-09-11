import { lazy, Suspense, useEffect, useState } from 'react'
import { loadSandbox } from './data'
import type { MachineData, MetaData, TabId, TreeData } from './types'
import { CampaignGraph } from './components/CampaignGraph'
import { FuturesPanel } from './components/FuturesPanel'
import { Briefing } from './components/Briefing'

const SparqlLab = lazy(() =>
  import('./components/SparqlLab').then((m) => ({ default: m.SparqlLab })),
)

const TABS: { id: TabId; label: string }[] = [
  { id: 'campaign', label: 'Campaign' },
  { id: 'futures', label: 'Futures' },
  { id: 'sparql', label: 'SPARQL' },
  { id: 'briefing', label: 'Briefing' },
]

export default function App() {
  const [tab, setTab] = useState<TabId>('campaign')
  const [machine, setMachine] = useState<MachineData | null>(null)
  const [tree, setTree] = useState<TreeData | null>(null)
  const [meta, setMeta] = useState<MetaData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void loadSandbox()
      .then((data) => {
        setMachine(data.machine)
        setTree(data.tree)
        setMeta(data.meta)
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : String(e))
      })
  }, [])

  if (error) {
    return <div className="error-box">Failed to load sandbox · {error}</div>
  }

  if (!machine || !tree || !meta) {
    return <div className="loading">Initializing trajectory sandbox…</div>
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            Thanos<span>State</span>Machine
          </div>
          <div className="brand-sub">{meta.subtitle}</div>
        </div>
        <nav className="top-links" aria-label="Repository">
          <a href="https://github.com/mrinaalr/ThanosStateMachine">GitHub</a>
          <a href="https://github.com/mrinaalr/ThanosStateMachine/blob/main/docs/FORMALISM.md">
            Formalism
          </a>
          <a href="https://casenoesis.up.railway.app/">CaseNoesis</a>
        </nav>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <h1>
            Destiny arrives.
            <br />
            <em>Exactly one</em> future wins.
          </h1>
          <p className="hero-lede">
            Walk Thanos&apos;s layered offense/harm machine, search the Avengers&apos;
            guardian policy space, and SPARQL the <code>traj:</code> graph —
            a public training playground over a fully observable Infinity Saga
            case graph.
          </p>
        </div>
        <aside className="measure" aria-label="Strange's measure">
          <div className="measure-label">Strange&apos;s measure</div>
          <div className="measure-num">
            <span>1</span> / {tree.futures.toLocaleString()}
          </div>
          <p className="measure-note">
            Calibrated, not measured. Optimal play still leaves five chance nodes —
            including the rat.
          </p>
        </aside>
      </section>

      <div className="tabs" role="tablist" aria-label="Sandbox views">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            className="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <section className="panel" role="tabpanel">
        <div className="panel-head">
          <h2>
            {tab === 'campaign' && 'Offender campaign graph'}
            {tab === 'futures' && 'Guardian decision search'}
            {tab === 'sparql' && 'SPARQL lab'}
            {tab === 'briefing' && 'Researcher briefing'}
          </h2>
          <p>
            {tab === 'campaign' &&
              'Click a state. Edges carry offender actions, affordances, and interventions.'}
            {tab === 'futures' &&
              'Uniform vs optimal policy over the 14,000,605-future tree.'}
            {tab === 'sparql' &&
              'Query the campaign via the traj: trajectories vocabulary.'}
            {tab === 'briefing' &&
              'How to use this with researchers and collaborators before CaseLinker.'}
          </p>
        </div>

        {tab === 'campaign' && <CampaignGraph machine={machine} />}
        {tab === 'futures' && <FuturesPanel tree={tree} />}
        {tab === 'sparql' && (
          <Suspense fallback={<div className="loading">Loading SPARQL engine…</div>}>
            <SparqlLab />
          </Suspense>
        )}
        {tab === 'briefing' && <Briefing meta={meta} />}
      </section>

      <p className="quote">
        “{meta.quote}”
        <cite>{meta.attribution}</cite>
      </p>
    </div>
  )
}

import { useState } from 'react'
import { QUERY_PRESETS, runSparql, type SparqlBinding } from '../sparql'

export function SparqlLab() {
  const [query, setQuery] = useState(QUERY_PRESETS[0].sparql)
  const [activePreset, setActivePreset] = useState(QUERY_PRESETS[0].id)
  const [columns, setColumns] = useState<string[]>([])
  const [rows, setRows] = useState<SparqlBinding[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [ran, setRan] = useState(false)

  async function execute(q: string = query) {
    setBusy(true)
    setError(null)
    try {
      const result = await runSparql(q)
      setColumns(result.columns)
      setRows(result.rows)
      setRan(true)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setColumns([])
      setRows([])
      setRan(true)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <p
        style={{
          margin: '0 0 1rem',
          color: 'var(--muted)',
          fontSize: '0.95rem',
          maxWidth: '46rem',
        }}
      >
        Query the campaign via the <code>traj:</code> trajectories vocabulary.
        Fiction on purpose: practice the graph vocabulary here before you open
        anything sensitive.
      </p>
      <div className="sparql-layout">
      <div>
        <h3
          style={{
            margin: '0 0 0.55rem',
            fontFamily: 'var(--display)',
            fontSize: '0.9rem',
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
          }}
        >
          Presets
        </h3>
        <div className="preset-list">
          {QUERY_PRESETS.map((p) => (
            <button
              key={p.id}
              type="button"
              className={`preset${activePreset === p.id ? ' active' : ''}`}
              onClick={() => {
                setActivePreset(p.id)
                setQuery(p.sparql)
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <textarea
          className="editor"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setActivePreset('')
          }}
          spellCheck={false}
          aria-label="SPARQL query"
        />
        <div className="actions-row">
          <button
            type="button"
            className="btn"
            disabled={busy}
            onClick={() => void execute()}
          >
            {busy ? 'Querying…' : 'Run SPARQL'}
          </button>
          <button
            type="button"
            className="btn ghost"
            onClick={() => {
              setQuery(QUERY_PRESETS[0].sparql)
              setActivePreset(QUERY_PRESETS[0].id)
            }}
          >
            Reset
          </button>
          <span style={{ color: 'var(--muted)', fontFamily: 'var(--mono)', fontSize: 12 }}>
            Source: graphs/thanos_campaign.ttl · traj: + tsm: · exporter-owned graph
          </span>
        </div>

        {error && <p className="err">{error}</p>}

        {ran && !error && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  {columns.map((c) => (
                    <th key={c}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td colSpan={Math.max(columns.length, 1)}>No bindings</td>
                  </tr>
                ) : (
                  rows.map((row, i) => (
                    <tr key={i}>
                      {columns.map((c) => (
                        <td key={c}>{row[c] ?? ''}</td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
        {ran && !error && (
          <p style={{ marginTop: 8, color: 'var(--muted)', fontFamily: 'var(--mono)', fontSize: 12 }}>
            {rows.length} binding{rows.length === 1 ? '' : 's'}
          </p>
        )}
      </div>
      </div>
    </div>
  )
}

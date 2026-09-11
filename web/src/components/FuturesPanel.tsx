import { useMemo, useState } from 'react'
import type { TreeData } from '../types'

type Props = { tree: TreeData }

export function FuturesPanel({ tree }: Props) {
  const [policy, setPolicy] = useState<'uniform' | 'optimal'>('uniform')
  const [active, setActive] = useState(0)

  const leverage = tree.leverage[policy]
  const maxLoss = Math.max(...leverage.map((l) => l.loss.approx), 1e-12)
  const pWin = policy === 'uniform' ? tree.pWinUniform : tree.pWinOptimal

  const winLabels = useMemo(
    () => Object.fromEntries(tree.winningLine.map((w) => [w.node, w.label])),
    [tree.winningLine],
  )

  return (
    <div>
      <div className="stats">
        <div className="stat">
          <div className="k">Futures (Strange)</div>
          <div className="v gold">{tree.futures.toLocaleString()}</div>
        </div>
        <div className="stat">
          <div className="k">P(win | {policy})</div>
          <div className="v">{pWin.label}</div>
        </div>
        <div className="stat">
          <div className="k">MC seed 42 wins</div>
          <div className="v ok">
            {tree.monteCarlo.observedWins} / {tree.monteCarlo.samples.toLocaleString()}
          </div>
        </div>
      </div>

      <div className="panel-head" style={{ marginBottom: '0.85rem' }}>
        <p>
          Toggle policy to see how perfect play collapses choice-node loss mass onto
          chance — the rat still holds the line hostage.
        </p>
        <div className="policy-toggle" role="group" aria-label="Guardian policy">
          <button
            type="button"
            aria-pressed={policy === 'uniform'}
            onClick={() => setPolicy('uniform')}
          >
            Uniform
          </button>
          <button
            type="button"
            aria-pressed={policy === 'optimal'}
            onClick={() => setPolicy('optimal')}
          >
            Optimal
          </button>
        </div>
      </div>

      <div className="grid-2">
        <div className="panel" style={{ padding: 0, border: 0, background: 'transparent' }}>
          <h3
            style={{
              margin: '0 0 0.65rem',
              fontFamily: 'var(--display)',
              fontSize: '0.95rem',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
            }}
          >
            Winning line
          </h3>
          <div className="timeline">
            {tree.nodes.map((node, i) => {
              const label =
                node.kind === 'choice'
                  ? winLabels[node.name]
                  : node.continueLabel
              const desc =
                node.kind === 'choice'
                  ? node.branches?.find((b) => b.surviving)?.description
                  : `p_continue = ${node.pContinue?.label}`
              return (
                <button
                  key={node.name}
                  type="button"
                  className={`step${active === i ? ' active' : ''}`}
                  style={{ cursor: 'pointer', textAlign: 'left', width: '100%' }}
                  onClick={() => setActive(i)}
                >
                  <div className="step-idx">{String(i + 1).padStart(2, '0')}</div>
                  <div>
                    <h4>
                      {node.name}{' '}
                      <span style={{ color: 'var(--muted)' }}>· {node.kind}</span>
                    </h4>
                    <p>
                      <strong style={{ color: 'var(--gold-hot)' }}>{label}</strong>
                      {desc ? ` — ${desc}` : ''}
                    </p>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        <div className="side-card">
          <div className="kv">
            <h3>Interdiction leverage ({policy})</h3>
            <p style={{ margin: 0, color: 'var(--muted)', fontSize: 14 }}>
              Loss mass at each node. Under uniform play, early contact dominates.
              Under optimal play, only chance remains.
            </p>
            <div className="bars" style={{ marginTop: 10 }}>
              {leverage
                .filter((l) => l.loss.approx > 0 || policy === 'optimal')
                .sort((a, b) => b.loss.approx - a.loss.approx)
                .map((l) => (
                  <div className="bar-row" key={l.node}>
                    <div className="name" title={l.node}>
                      {l.node}
                    </div>
                    <div className="bar-track">
                      <div
                        className={`bar-fill${l.kind === 'chance' ? ' chance' : ''}`}
                        style={{
                          width: `${Math.max(2, (l.loss.approx / maxLoss) * 100)}%`,
                        }}
                      />
                    </div>
                    <div className="bar-val">
                      {(l.loss.approx * 100).toFixed(l.loss.approx < 0.01 ? 3 : 1)}%
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div className="kv">
            <h3>Top failure modes</h3>
            <div className="bars">
              {tree.failureModes.slice(0, 6).map((fm) => (
                <div key={`${fm.node}:${fm.branch}`} className="bar-row">
                  <div className="name" title={`${fm.node}:${fm.branch}`}>
                    {fm.branch}
                  </div>
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{
                        width: `${Math.max(2, fm.massUniform.approx * 100)}%`,
                      }}
                    />
                  </div>
                  <div className="bar-val">
                    {(fm.massUniform.approx * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
            <p style={{ margin: '8px 0 0', color: 'var(--muted)', fontSize: 13 }}>
              {tree.monteCarlo.note}
            </p>
          </div>

          {tree.nodes[active]?.anchor?.note && (
            <div className="kv">
              <h3>Offender anchor</h3>
              <p style={{ margin: 0, fontSize: 14 }}>
                {tree.nodes[active].anchor?.note}
              </p>
              {(tree.nodes[active].anchor?.offenderStates.length ?? 0) > 0 && (
                <div className="chip-row" style={{ marginTop: 8 }}>
                  {tree.nodes[active].anchor?.offenderStates.map((s) => (
                    <span key={s} className="chip">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

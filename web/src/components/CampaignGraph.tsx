import { useMemo, useState } from 'react'
import type { MachineData, MachineState } from '../types'

const LAYER_COLOR: Record<string, string> = {
  campaign: '#d4b45a',
  space: '#4aa3e8',
  reality: '#e05555',
  soul: '#e6b84d',
  time: '#5cbf7a',
  mind: '#e8d24a',
}

type Props = {
  machine: MachineData
}

type Pos = { x: number; y: number }

function layout(states: MachineState[]): Record<string, Pos> {
  const byLayer: Record<string, MachineState[]> = {}
  for (const s of states) {
    const layer = s.layer ?? 'campaign'
    ;(byLayer[layer] ??= []).push(s)
  }

  const order = ['campaign', 'space', 'reality', 'soul', 'time', 'mind']
  const pos: Record<string, Pos> = {}
  const colX = [40, 220, 400, 580]
  const phaseCol = (phase: string | null, id: string) => {
    if (id === 'CampaignInitiation') return 0
    if (id === 'SnapEvent') return 2
    if (id === 'GardenWithdrawal') return 2
    if (id === 'RemediationBattle') return 3
    if (id === 'CampaignRemediated') return 3
    if (phase === 'InitialContactPhase') return 0
    if (phase === 'ConditioningPhase') return 1
    if (phase === 'HarmExecutionPhase') return 2
    if (phase === 'MaintenancePhase') return 2
    return 1
  }

  order.forEach((layer, li) => {
    const row = byLayer[layer] ?? []
    const yBase = 40 + li * 88
    row.forEach((s) => {
      pos[s.id] = { x: colX[phaseCol(s.phase, s.id)], y: yBase }
    })
  })

  // Snap sits as the spine hub — nudge campaign terminals
  if (pos.SnapEvent) pos.SnapEvent = { x: 400, y: 40 }
  if (pos.GardenWithdrawal) pos.GardenWithdrawal = { x: 520, y: 40 }
  if (pos.RemediationBattle) pos.RemediationBattle = { x: 640, y: 40 }
  if (pos.CampaignRemediated) pos.CampaignRemediated = { x: 760, y: 40 }
  if (pos.CampaignInitiation) pos.CampaignInitiation = { x: 40, y: 40 }

  return pos
}

export function CampaignGraph({ machine }: Props) {
  const [selected, setSelected] = useState<string>(machine.initial)
  const pos = useMemo(() => layout(machine.states), [machine.states])
  const stateMap = useMemo(
    () => Object.fromEntries(machine.states.map((s) => [s.id, s])),
    [machine.states],
  )
  const actionMap = useMemo(
    () => Object.fromEntries(machine.actions.map((a) => [a.id, a])),
    [machine.actions],
  )

  const sel = stateMap[selected]
  const outEdges = machine.transitions.filter((t) => t.source === selected)
  const inEdges = machine.transitions.filter((t) => t.target === selected)
  const affordances = machine.actions.filter((a) => a.kind === 'affordance')

  return (
    <div className="grid-2">
      <div>
        <div className="graph-wrap">
          <svg className="graph-svg" viewBox="0 0 900 560">
            {machine.transitions.map((t) => {
              const a = pos[t.source]
              const b = pos[t.target]
              if (!a || !b) return null
              const hasAff = t.actions.some(
                (id) => actionMap[id]?.kind === 'affordance',
              )
              const hasInt = t.actions.some(
                (id) => actionMap[id]?.kind === 'guardian_intervention',
              )
              const cls = hasInt
                ? 'edge intervention'
                : hasAff
                  ? 'edge affordance'
                  : 'edge'
              const x1 = a.x + 70
              const y1 = a.y + 18
              const x2 = b.x
              const y2 = b.y + 18
              const midX = (x1 + x2) / 2
              return (
                <path
                  key={`${t.source}-${t.target}`}
                  className={cls}
                  d={`M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`}
                />
              )
            })}
            {machine.states.map((s) => {
              const p = pos[s.id]
              if (!p) return null
              const stroke = LAYER_COLOR[s.layer ?? 'campaign']
              return (
                <g
                  key={s.id}
                  className={`node${selected === s.id ? ' selected' : ''}`}
                  transform={`translate(${p.x}, ${p.y})`}
                  onClick={() => setSelected(s.id)}
                >
                  <rect
                    width="140"
                    height="36"
                    rx="2"
                    style={{ stroke }}
                  />
                  <text x="8" y="15">
                    {s.id}
                  </text>
                  <text className="phase" x="8" y="28">
                    {(s.phase ?? s.terminal ?? s.layer ?? 'meta').replace(
                      /Phase$/,
                      '',
                    )}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
        <div className="legend">
          {Object.entries(LAYER_COLOR).map(([layer, color]) => (
            <span key={layer} className="layer-pill">
              <span className="dot" style={{ background: color }} />
              {layer}
            </span>
          ))}
          <span>gold dashed = affordance-labelled edge</span>
          <span>green = guardian intervention</span>
        </div>
      </div>

      <div className="side-card">
        <div className="kv">
          <h3>{sel?.id ?? '—'}</h3>
          <dl>
            <dt>Layer</dt>
            <dd>
              <span className="layer-pill">
                <span className={`dot ${sel?.layer ?? 'campaign'}`} />
                {sel?.layer ?? '—'}
              </span>
            </dd>
            <dt>Phase</dt>
            <dd>{sel?.phase ?? 'exogenous / meta'}</dd>
            <dt>Terminal</dt>
            <dd>{sel?.terminal ?? 'no'}</dd>
          </dl>
        </div>

        <div className="kv">
          <h3>Inbound</h3>
          {inEdges.length === 0 ? (
            <p style={{ margin: 0, color: 'var(--muted)' }}>Initial state</p>
          ) : (
            inEdges.map((e) => (
              <div key={`${e.source}-${e.target}`} style={{ marginBottom: 8 }}>
                <button
                  className="btn ghost"
                  style={{ padding: '0.25rem 0.5rem' }}
                  onClick={() => setSelected(e.source)}
                >
                  ← {e.source}
                </button>
                <div className="chip-row" style={{ marginTop: 6 }}>
                  {e.actions.map((a) => (
                    <span key={a} className={`chip ${actionMap[a]?.kind ?? ''}`}>
                      {a}
                    </span>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="kv">
          <h3>Outbound</h3>
          {outEdges.length === 0 ? (
            <p style={{ margin: 0, color: 'var(--muted)' }}>No successors</p>
          ) : (
            outEdges.map((e) => (
              <div key={`${e.source}-${e.target}`} style={{ marginBottom: 8 }}>
                <button
                  className="btn ghost"
                  style={{ padding: '0.25rem 0.5rem' }}
                  onClick={() => setSelected(e.target)}
                >
                  → {e.target}
                </button>
                {e.trigger && (
                  <p style={{ margin: '4px 0 0', color: 'var(--muted)', fontSize: 14 }}>
                    {e.trigger}
                  </p>
                )}
                <div className="chip-row" style={{ marginTop: 6 }}>
                  {e.actions.map((a) => (
                    <span key={a} className={`chip ${actionMap[a]?.kind ?? ''}`}>
                      {a}
                    </span>
                  ))}
                  {e.benefitKind && (
                    <span className="chip">{e.benefitKind}</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="kv">
          <h3>Dynamic affordances</h3>
          <p style={{ margin: 0, color: 'var(--muted)', fontSize: 14 }}>
            Acquisitions unlock later-edge capabilities — the layered
            extension CaseNoesis stress-tests here.
          </p>
          <div className="chip-row" style={{ marginTop: 8 }}>
            {affordances.map((a) => (
              <span key={a.id} className="chip affordance" title={a.description}>
                {a.id}
                {a.unlockedBy ? ` ← ${a.unlockedBy}` : ''}
              </span>
            ))}
          </div>
        </div>

        <div className="kv">
          <h3>SEP verdict</h3>
          <p style={{ margin: 0 }}>
            <strong style={{ color: machine.exploitation.isExploitation ? 'var(--danger)' : 'var(--ok)' }}>
              {machine.exploitation.isExploitation ? 'Exploitation' : 'Not exploitation'}
            </strong>
          </p>
          <p style={{ margin: '6px 0 0', color: 'var(--muted)', fontSize: 14 }}>
            {machine.exploitation.note}
          </p>
        </div>
      </div>
    </div>
  )
}

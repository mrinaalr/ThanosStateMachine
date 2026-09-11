import { QueryEngine } from '@comunica/query-sparql'
import { ttlUrl } from './data'

const PREFIXES = `PREFIX traj: <https://casenoesis.org/ontology/trajectory#>
PREFIX tsm:  <https://github.com/mrinaalr/ThanosStateMachine#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
`

export const QUERY_PRESETS: { id: string; label: string; sparql: string }[] = [
  {
    id: 'affordances',
    label: 'Affordances Thanos unlocked',
    sparql: `${PREFIXES}
SELECT ?action ?label ?unlockedBy WHERE {
  ?action a traj:Action ;
          tsm:affordance true ;
          rdfs:label ?label .
  OPTIONAL { ?action tsm:unlockedBy ?unlockedBy }
}
ORDER BY ?action`,
  },
  {
    id: 'harm-phase',
    label: 'Harm-execution states',
    sparql: `${PREFIXES}
SELECT ?state ?layer WHERE {
  ?state a traj:State ;
         traj:phaseLabel "HarmExecutionPhase" .
  OPTIONAL { ?state traj:layer ?layer }
}
ORDER BY ?layer ?state`,
  },
  {
    id: 'layers',
    label: 'States by stone layer',
    sparql: `${PREFIXES}
SELECT ?layer (COUNT(?state) AS ?n) WHERE {
  ?state a traj:State ; traj:layer ?layer .
}
GROUP BY ?layer
ORDER BY DESC(?n)`,
  },
  {
    id: 'interventions',
    label: 'Guardian interventions',
    sparql: `${PREFIXES}
SELECT ?action ?label WHERE {
  ?action a traj:Action ;
          tsm:guardianIntervention true ;
          rdfs:label ?label .
}
ORDER BY ?action`,
  },
  {
    id: 'trajectories',
    label: 'Terminal polarities',
    sparql: `${PREFIXES}
SELECT ?traj ?label ?polarity ?terminal WHERE {
  ?traj a traj:Trajectory ;
        rdfs:label ?label ;
        traj:terminalPolarity ?polarity ;
        traj:terminalState ?terminal .
}
ORDER BY ?traj`,
  },
  {
    id: 'edges-from-snap',
    label: 'Edges out of SnapEvent',
    sparql: `${PREFIXES}
SELECT ?edge ?to ?trigger WHERE {
  ?edge a traj:Transition ;
        traj:fromState tsm:SnapEvent ;
        traj:toState ?to .
  OPTIONAL { ?edge traj:trigger ?trigger }
}`,
  },
]

let engine: QueryEngine | null = null
let ttlCache: string | null = null

function getEngine() {
  if (!engine) engine = new QueryEngine()
  return engine
}

async function loadTtl(): Promise<string> {
  if (ttlCache) return ttlCache
  const res = await fetch(ttlUrl())
  if (!res.ok) throw new Error(`Failed to fetch TTL (${res.status})`)
  ttlCache = await res.text()
  return ttlCache
}

export type SparqlBinding = Record<string, string>

export async function runSparql(query: string): Promise<{
  columns: string[]
  rows: SparqlBinding[]
}> {
  const ttl = await loadTtl()
  const result = await getEngine().queryBindings(query, {
    sources: [
      {
        type: 'serialized',
        value: ttl,
        mediaType: 'text/turtle',
        baseIRI: 'https://github.com/mrinaalr/ThanosStateMachine#',
      },
    ],
  })

  const rows: SparqlBinding[] = []
  const colSet = new Set<string>()

  for await (const binding of result) {
    const row: SparqlBinding = {}
    for (const [key, term] of binding) {
      const k = key.value
      colSet.add(k)
      row[k] = shorten(term.value)
    }
    rows.push(row)
  }

  return { columns: [...colSet], rows }
}

function shorten(v: string): string {
  return v
    .replace('https://github.com/mrinaalr/ThanosStateMachine#', 'tsm:')
    .replace('https://casenoesis.org/ontology/trajectory#', 'traj:')
    .replace('http://www.w3.org/ns/prov#', 'prov:')
    .replace('http://www.w3.org/2000/01/rdf-schema#', 'rdfs:')
}

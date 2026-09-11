export type Frac = {
  n: number
  d: number
  approx: number
  label: string
}

export type MachineState = {
  id: string
  phase: string | null
  layer: string | null
  terminal: string | null
}

export type MachineAction = {
  id: string
  kind: string
  description: string
  unlockedBy: string | null
}

export type MachineTransition = {
  source: string
  target: string
  actions: string[]
  trigger: string
  benefitKind: string | null
}

export type MachineData = {
  initial: string
  states: MachineState[]
  actions: MachineAction[]
  transitions: MachineTransition[]
  exploitation: {
    isExploitation: boolean
    goalEdge: string[]
    goalEdgeKind: string
    rationale: string
    note: string
  }
}

export type TreeBranch = {
  label: string
  outcome: string
  description: string
  surviving: boolean
}

export type TreeNode = {
  name: string
  kind: 'choice' | 'chance'
  branches?: TreeBranch[]
  pContinue?: Frac
  continueLabel?: string
  failDescription?: string
  anchor?: {
    offenderStates: string[]
    offenderEdges: string[][]
    note: string
  } | null
}

export type TreeData = {
  futures: number
  pWinUniform: Frac
  pWinOptimal: Frac
  winningLine: { node: string; label: string }[]
  nodes: TreeNode[]
  failureModes: {
    node: string
    branch: string
    description: string
    massUniform: Frac
  }[]
  leverage: {
    uniform: {
      node: string
      kind: string
      reach: Frac
      loss: Frac
      continue: Frac
    }[]
    optimal: {
      node: string
      kind: string
      reach: Frac
      loss: Frac
      continue: Frac
    }[]
  }
  monteCarlo: {
    seed: number
    samples: number
    observedWins: number
    note: string
  }
}

export type MetaData = {
  version: string
  title: string
  subtitle: string
  quote: string
  attribution: string
  canon: string[]
  research: { program: string; role: string }
}

export type TabId = 'campaign' | 'futures' | 'sparql' | 'briefing'

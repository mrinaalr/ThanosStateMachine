import type { MachineData, MetaData, TreeData } from './types'

const base = import.meta.env.BASE_URL

async function loadJson<T>(name: string): Promise<T> {
  const res = await fetch(`${base}data/${name}`)
  if (!res.ok) throw new Error(`Failed to load ${name}: ${res.status}`)
  return res.json() as Promise<T>
}

export async function loadSandbox() {
  const [machine, tree, meta] = await Promise.all([
    loadJson<MachineData>('machine.json'),
    loadJson<TreeData>('tree.json'),
    loadJson<MetaData>('meta.json'),
  ])
  return { machine, tree, meta }
}

export function ttlUrl() {
  return `${base}data/thanos_campaign.ttl`
}

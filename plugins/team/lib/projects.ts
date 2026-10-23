// Keeps team sessions inside projects the user already has in the OpenCode sidebar.
// OpenCode maps a git checkout (a linked worktree included) to its repo's project, but every directory outside a
// git checkout becomes a project of its own, so a scratch folder would add a permanent entry to the sidebar.
import { git } from "./close.ts"
import { orchestratorOf } from "./store.ts"

export type Placement = { directory: string; scratch?: string }

export async function isGitCheckout(dir: string): Promise<boolean> {
  const inside = await git(dir, "rev-parse", "--is-inside-work-tree")
  return inside.ok && inside.out === "true"
}

export async function placeSession(team: string, requested: string): Promise<Placement> {
  if (await isGitCheckout(requested)) return { directory: requested }
  const home = (await orchestratorOf(team))?.directory
  if (!home || home === requested || !(await isGitCheckout(home))) return { directory: requested }
  return { directory: home, scratch: requested }
}

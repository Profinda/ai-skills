// Closing a team: inspect what it created (worktrees, branches), say what is safe to remove, remove only that.
// Everything else (databases, containers, processes, directories) is listed with the command the registrant gave.
import { execFile } from "node:child_process"
import { promisify } from "node:util"
import { access } from "node:fs/promises"
import path from "node:path"
import type { Resource } from "./store.ts"

const run = promisify(execFile)

async function git(cwd: string, ...args: string[]): Promise<{ ok: boolean; out: string }> {
  try {
    const { stdout } = await run("git", ["-C", cwd, ...args], { maxBuffer: 8 * 1024 * 1024 })
    return { ok: true, out: stdout.trim() }
  } catch (error: any) {
    return { ok: false, out: String(error?.stderr || error?.message || "").trim() }
  }
}

const exists = (target: string) => access(target).then(() => true, () => false)

export async function linkedWorktreeRepo(dir: string): Promise<string | null> {
  if (!(await exists(dir))) return null
  const gitDir = await git(dir, "rev-parse", "--path-format=absolute", "--git-dir")
  const common = await git(dir, "rev-parse", "--path-format=absolute", "--git-common-dir")
  if (!gitDir.ok || !common.ok || gitDir.out === common.out) return null
  return path.dirname(common.out)
}

export type Verdict = "safe" | "disposable" | "blocked" | "missing"
export type Inspection = { verdict: Verdict; detail: string; branch?: string }

async function pushed(cwd: string, ref: string): Promise<boolean> {
  const containing = await git(cwd, "branch", "-r", "--contains", ref)
  return containing.ok && containing.out.length > 0
}

export async function inspectWorktree(resource: Resource): Promise<Inspection> {
  const dir = resource.ref
  if (!(await exists(dir))) return { verdict: "missing", detail: "directory is gone" }
  const repo = await linkedWorktreeRepo(dir)
  if (!repo) return { verdict: "blocked", detail: "not a linked git worktree (the main checkout is never removed)" }
  const status = await git(dir, "status", "--porcelain")
  const dirty = status.out.split("\n").filter((line) => line && !line.includes(".opencode")).length
  const head = await pushed(dir, "HEAD")
  const branch = (await git(dir, "branch", "--show-current")).out
  const ahead = branch ? Number((await git(dir, "rev-list", "--count", `origin/${branch}..HEAD`)).out || "0") : 0
  const facts = `${dirty} uncommitted file(s), ${head ? "HEAD is on a remote" : "HEAD only exists locally"}${branch ? `, branch ${branch}${ahead ? `, ${ahead} unpushed commit(s)` : ""}` : ""}`
  if (resource.disposable) return { verdict: "disposable", detail: `marked disposable: ${facts}`, branch }
  if (dirty > 0) return { verdict: "blocked", detail: facts, branch }
  if (!head) return { verdict: "blocked", detail: facts, branch }
  return { verdict: "safe", detail: facts, branch }
}

export async function inspectBranch(resource: Resource): Promise<Inspection> {
  const repo = resource.repo
  if (!repo || !(await exists(repo))) return { verdict: "blocked", detail: "repo path missing in the registration" }
  const has = await git(repo, "rev-parse", "--verify", "-q", `refs/heads/${resource.ref}`)
  if (!has.ok) return { verdict: "missing", detail: "branch is gone" }
  const worktrees = await git(repo, "worktree", "list", "--porcelain")
  if (worktrees.out.split("\n").some((line) => line === `branch refs/heads/${resource.ref}`)) {
    return { verdict: "blocked", detail: "still checked out in a worktree (it is removed first when that worktree is registered too)" }
  }
  const onRemote = await pushed(repo, `refs/heads/${resource.ref}`)
  if (resource.disposable) return { verdict: "disposable", detail: `marked disposable, ${onRemote ? "also on a remote" : "local only"}` }
  return onRemote ? { verdict: "safe", detail: "its commits are on a remote" } : { verdict: "blocked", detail: "local commits that exist nowhere else" }
}

// Plain `git worktree remove` refuses a worktree with untracked files, and every team worktree has an untracked
// .opencode/ folder. Callers only get here after inspectWorktree found nothing else uncommitted (or the resource is
// marked disposable), so --force removes nothing of value.
export async function removeWorktree(resource: Resource): Promise<string> {
  const repo = await linkedWorktreeRepo(resource.ref)
  if (!repo) return "skipped (not a linked worktree)"
  const result = await git(repo, "worktree", "remove", "--force", resource.ref)
  return result.ok ? "removed" : `FAILED: ${result.out.slice(0, 200)}`
}

export async function removeBranch(resource: Resource): Promise<string> {
  const result = await git(resource.repo!, "branch", "-D", resource.ref)
  return result.ok ? "deleted" : `FAILED: ${result.out.slice(0, 200)}`
}

export async function dirSize(dir: string): Promise<string> {
  try {
    const { stdout } = await run("du", ["-sh", dir])
    return stdout.split("\t")[0].trim()
  } catch {
    return "?"
  }
}

export { exists }

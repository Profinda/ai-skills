;(function () {
  "use strict"

  const GROUP_ID = "oc-session-notes-chips"
  const POPOVER_ID = "oc-session-notes-popover"
  const POLL_MS = 2000
  const STORAGE_PREFIX = "oc-session-notes:"
  const SYNC_PREFIX = "oc-session-notes-agent-sync:"
  const JIRA_BASE_URL = "https://profinda.atlassian.net/browse/"

  // Theme-matched via the app's own CSS custom properties (confirmed present
  // on this page: bg-deep/bg-base, text-base/text-faint, overlay-hover). Each
  // has a hardcoded fallback so the popover still looks reasonable if a
  // variable name ever changes upstream. Hoisted to module scope so both the
  // static popover skeleton and the dynamically-rendered PR row list share
  // identical styling.
  const THEME = {
    bgSurface: "var(--v2-background-bg-base, #1a1c22)",
    bgInset: "var(--v2-background-bg-deep, #0f1013)",
    textBase: "var(--v2-text-text-base, #e4e6eb)",
    textFaint: "var(--v2-text-text-faint, #9aa0ab)",
    borderColor: "var(--v2-overlay-simple-overlay-hover, rgba(127,127,127,0.18))",
  }
  const inputStyle =
    `width:100%;box-sizing:border-box;background:${THEME.bgInset};border:1px solid ${THEME.borderColor};` +
    `border-radius:6px;color:${THEME.textBase};padding:6px 8px;font:13px/1.4 -apple-system,sans-serif`
  const rowStyle = "display:flex;align-items:center;gap:6px"
  const smallBtnStyle =
    `display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;flex-shrink:0;` +
    `border-radius:6px;color:${THEME.textFaint};text-decoration:none;font-size:13px;border:1px solid ${THEME.borderColor}`
  const fieldLabel = (text) =>
    `<div style="opacity:.6;color:${THEME.textFaint};font-size:11px;text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px">${text}</div>`

  let pollTimer = null
  let contextDead = false

  // When you reload the extension in chrome://extensions, any already-open tab
  // keeps running its OLD content script instance, whose connection to the
  // extension is now dead. Every chrome.storage/runtime call from that stale
  // instance throws "Extension context invalidated." There's no way to recover
  // in-page — the fix is always a hard refresh of the tab — so instead of
  // spamming that error on every poll forever, detect it once and stop cleanly.
  function contextValid() {
    return typeof chrome !== "undefined" && !!chrome.runtime && !!chrome.runtime.id
  }

  function markContextDead() {
    if (contextDead) return
    contextDead = true
    if (pollTimer) clearInterval(pollTimer)
    console.warn(
      "[opencode-session-notes] Extension context invalidated (extension was reloaded). Refresh this tab to reconnect.",
    )
  }

  // document.title reflects the current SESSION's own title in this UI
  // (e.g. "DONE PR Preview environment creation status debug"), not a fixed
  // "OpenCode" string — checking for that substring silently (no errors)
  // fails on every real session, which is exactly what broke chip rendering.
  // The #root div is a stable structural marker regardless of title content.
  function isOpenCodePage() {
    return !!document.getElementById("root")
  }

  // Same-origin requests to the OpenCode V2 server. An `opencode pair` link yields a token, not a cookie: the
  // web UI keeps it in localStorage and sends it as Basic auth (user "opencode"), so we reuse that token.
  function serverPassword() {
    try {
      const origin = location.origin.replace(/\/+$/, "")
      let fallback = null
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (!key || !key.startsWith("opencode.global.dat:server")) continue
        const list = JSON.parse(localStorage.getItem(key) || "null")?.list
        if (!Array.isArray(list)) continue
        for (const entry of list) {
          const http = entry?.http || entry
          if (!http?.password) continue
          if (String(http.url || "").replace(/\/+$/, "") === origin) return http.password
          fallback = fallback || http.password
        }
      }
      return fallback
    } catch {
      return null
    }
  }

  let warnedUnauthorized = false

  async function getJSON(path, init) {
    try {
      const password = serverPassword()
      const headers = { ...(init?.headers || {}), ...(password ? { authorization: `Basic ${btoa(`opencode:${password}`)}` } : {}) }
      const res = await fetch(path, { cache: "no-store", ...init, headers })
      if (!res.ok) {
        if (res.status === 401 && !warnedUnauthorized) {
          warnedUnauthorized = true
          console.warn(
            `[opencode-session-notes] 401 from the OpenCode server (${password ? "stored token rejected" : "no stored token found in localStorage"}). Re-pair this window with \`opencode pair\`.`,
          )
        }
        return null
      }
      return await res.json()
    } catch {
      return null
    }
  }

  function postJSON(path, body) {
    return getJSON(path, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) })
  }

  // The in-app tab strip does not reliably sync window.location on every tab
  // click (it's a "browser inside the browser" UI). Each tab slot carries its
  // own data-tab-key (a full href including the session ID) and a data-active
  // flag, which is the authoritative source for "which session is showing right
  // now" — far more reliable than trusting location.pathname. Fall back to the
  // URL only if no tab strip is present at all (e.g. a bare single-session view).
  function currentSessionId() {
    const activeSlot = document.querySelector('[data-titlebar-tab-slot][data-active="true"]')
    const key = activeSlot?.getAttribute("data-tab-key")
    const fromKey = key?.match(/session\/(ses[^/\s]+)/)
    if (fromKey) return fromKey[1]

    // V2 session URLs are /server/<key>/session/<id>: match the ID itself, not the "session" segment.
    const fromUrl = location.pathname.split("/").find((seg) => /^ses_/.test(seg))
    return fromUrl || null
  }

  async function resolveSessionMeta(sessionId) {
    const res = await getJSON(`/api/session/${encodeURIComponent(sessionId)}`)
    const session = res?.data
    return { directory: session?.location?.directory || null, title: session?.title || null }
  }

  const EMPTY_NOTES = { intent: "", jiraEpic: "", jiraTicket: "", title: "", prUrls: [], localUrl: "", progress: "" }

  function jiraUrl(ticket) {
    return ticket ? `${JIRA_BASE_URL}${encodeURIComponent(ticket)}` : ""
  }

  // Extracts the PR/MR number from a GitHub/GitLab/Bitbucket-style URL so the
  // chip can show "PR#345" instead of a generic "PR" — makes it possible to
  // tell sessions apart at a glance instead of opening each one to check.
  function prNumberFromUrl(url) {
    const match = url.match(/\/(?:pull|pull-requests|merge_requests)\/(\d+)/)
    return match ? match[1] : null
  }

  // A session can span more than one PR (follow-ups, split work, etc.), so
  // prUrls is always an array. Migrates older single-`prUrl` shaped data
  // (both agent-written files and previously-saved chrome.storage entries)
  // transparently, and always dedupes/drops blanks.
  function normalizePrUrls(source) {
    const raw = Array.isArray(source?.prUrls) ? source.prUrls : source?.prUrl ? [source.prUrl] : []
    return Array.from(new Set(raw.map((url) => (url || "").trim()).filter(Boolean)))
  }

  // What used to be a single "Summary" field is split into two: `intent` (the
  // stable WHY — set once early on, rarely changes) and `progress` (the
  // evolving WHAT'S DONE / WHAT'S LEFT / what phase we're in — updated often).
  // Migrates older single-`summary` shaped data (both agent files and
  // previously-saved chrome.storage entries) by treating it as `progress`,
  // since that's what it was already functioning as in practice.
  function normalizeNotes(source) {
    if (!source) return { ...EMPTY_NOTES }
    return {
      ...EMPTY_NOTES,
      ...source,
      prUrls: normalizePrUrls(source),
      progress: source.progress ?? source.summary ?? "",
    }
  }

  function loadNotes(sessionId) {
    if (!contextValid()) {
      markContextDead()
      return Promise.resolve(EMPTY_NOTES)
    }
    return new Promise((resolve) => {
      try {
        chrome.storage.local.get(STORAGE_PREFIX + sessionId, (result) => {
          if (chrome.runtime.lastError) {
            markContextDead()
            resolve(EMPTY_NOTES)
            return
          }
          resolve(normalizeNotes(result[STORAGE_PREFIX + sessionId]))
        })
      } catch {
        markContextDead()
        resolve(EMPTY_NOTES)
      }
    })
  }

  function saveNotes(sessionId, notes) {
    if (!contextValid()) {
      markContextDead()
      return Promise.resolve()
    }
    return new Promise((resolve) => {
      try {
        chrome.storage.local.set({ [STORAGE_PREFIX + sessionId]: notes }, () => {
          if (chrome.runtime.lastError) markContextDead()
          resolve()
        })
      } catch {
        markContextDead()
        resolve()
      }
    })
  }

  // Bridge for agents: chrome.storage is only reachable from inside the browser,
  // so an agent records notes with the `session-notes_set` tool, which the
  // session-notes plugin keeps per session ID (two sessions in the same worktree
  // never contaminate each other). We poll the plugin's RPC and, whenever
  // updatedAt changes, copy the notes into chrome.storage as the new baseline —
  // which you can keep editing normally afterward. The RPC also returns notes a
  // V1 agent wrote to .opencode/session-notes/<id>.json. Skipped entirely while
  // the popover is open so an agent run never clobbers active typing.
  async function fetchAgentMeta(directory, sessionId) {
    const qs = directory ? `?directory=${encodeURIComponent(directory)}` : ""
    const res = await postJSON(`/api/rpc/session-notes/get${qs}`, { input: { sessionID: sessionId } })
    const notes = res?.output?.notes
    return notes && typeof notes === "object" ? notes : null
  }

  function getSyncedAt(sessionId) {
    if (!contextValid()) {
      markContextDead()
      return Promise.resolve(null)
    }
    return new Promise((resolve) => {
      try {
        chrome.storage.local.get(SYNC_PREFIX + sessionId, (r) => {
          if (chrome.runtime.lastError) {
            markContextDead()
            resolve(null)
            return
          }
          resolve(r[SYNC_PREFIX + sessionId] || null)
        })
      } catch {
        markContextDead()
        resolve(null)
      }
    })
  }

  function setSyncedAt(sessionId, updatedAt) {
    if (!contextValid()) {
      markContextDead()
      return Promise.resolve()
    }
    return new Promise((resolve) => {
      try {
        chrome.storage.local.set({ [SYNC_PREFIX + sessionId]: updatedAt }, () => {
          if (chrome.runtime.lastError) markContextDead()
          resolve()
        })
      } catch {
        markContextDead()
        resolve()
      }
    })
  }

  async function maybeSyncFromAgent(sessionId, directory, popoverOpen) {
    if (popoverOpen) return null
    const meta = await fetchAgentMeta(directory, sessionId)
    if (!meta || !meta.updatedAt) return null

    const lastSynced = await getSyncedAt(sessionId)
    if (lastSynced === meta.updatedAt) return null // already applied

    const notes = normalizeNotes(meta)
    await saveNotes(sessionId, notes)
    await setSyncedAt(sessionId, meta.updatedAt)
    return notes
  }

  // Title row is: h1[data-slot="session-title-child"] -> ... -> div.h-12 (row).
  // The row's last child holds the "view context usage" + "more options" buttons.
  //
  // opencode keeps multiple tabs' content mounted simultaneously (a "keep
  // tabs alive" pattern for instant switching), so there can be MULTIPLE
  // [data-slot="session-title-child"] elements in the DOM at once — one per
  // open tab, only one of which is actually visible. A plain querySelector()
  // always grabs the first one in DOM order regardless of which tab is
  // active, silently injecting into the wrong (hidden) tab. Disambiguate by
  // matching the element whose text equals the ACTIVE session's own title
  // (fetched via /api/session/{id}), falling back to the first match only if
  // nothing lines up (e.g. transient state right after a title edit).
  function findAnchors(expectedTitle) {
    const titles = Array.from(document.querySelectorAll('[data-slot="session-title-child"]'))
    if (titles.length === 0) return null
    const match =
      (expectedTitle && titles.find((el) => el.textContent?.trim() === expectedTitle.trim())) || titles[0]
    const row = match.closest('[class*="h-12"]')
    if (!row || row.children.length < 2) return null
    return { row, rightIcons: row.children[row.children.length - 1] }
  }

  function chip(href, label, color) {
    return `<a href="${href}" target="_blank" rel="noopener"
      style="display:inline-flex;align-items:center;gap:3px;font:12px/1 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
             color:${color};text-decoration:none;white-space:nowrap;padding:3px 7px;border-radius:6px;
             background:var(--v2-overlay-simple-overlay-hover, rgba(127,127,127,0.12))">${label} ↗</a>`
  }

  // A plain `id` would be duplicated across the multiple simultaneously-
  // mounted tab rows described above (invalid HTML, and easy to reason about
  // incorrectly) — use a data-attribute scoped per-row instead. Every lookup
  // stays scoped to a specific `row` via querySelector, never global.
  function ensureChipGroup(expectedTitle) {
    const anchors = findAnchors(expectedTitle)
    if (!anchors) return null

    let group = anchors.row.querySelector(`[data-${GROUP_ID}]`)
    if (group) return group

    group = document.createElement("div")
    group.setAttribute(`data-${GROUP_ID}`, "")
    group.style.cssText = "display:flex;align-items:center;gap:6px;flex-shrink:0;margin-right:4px"
    anchors.row.insertBefore(group, anchors.rightIcons)
    return group
  }

  function ensurePopover() {
    let pop = document.getElementById(POPOVER_ID)
    if (pop) return pop

    pop = document.createElement("div")
    pop.id = POPOVER_ID
    pop.style.cssText = [
      "display:none",
      "position:absolute",
      "z-index:2147483647",
      "min-width:420px",
      "max-width:520px",
      "font:13px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif",
      `background:${THEME.bgSurface}`,
      `color:${THEME.textBase}`,
      `border:1px solid ${THEME.borderColor}`,
      "border-radius:10px",
      "box-shadow:0 12px 32px rgba(0,0,0,0.35)",
      "padding:16px 18px",
    ].join(";")

    pop.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:12px">
        <div>${fieldLabel("Worktree")}<div data-field="worktree" style="font-family:ui-monospace,monospace;font-size:11px;opacity:.7;word-break:break-all"></div></div>
        <div>${fieldLabel("Intent — what is this session trying to achieve")}<textarea data-field="intent" rows="3" placeholder="What triggered this session? What's the actual goal?" style="${inputStyle};resize:vertical;font-family:inherit"></textarea></div>
        <div>${fieldLabel("Jira Epic")}<div style="${rowStyle}"><input data-field="jiraEpic" type="text" placeholder="SP-100" style="${inputStyle}"><a data-field="jiraEpicOpen" target="_blank" rel="noopener" style="${smallBtnStyle}">↗</a></div></div>
        <div>${fieldLabel("Jira Ticket")}<div style="${rowStyle}"><input data-field="jiraTicket" type="text" placeholder="SP-123" style="${inputStyle}"><a data-field="jiraTicketOpen" target="_blank" rel="noopener" style="${smallBtnStyle}">↗</a></div></div>
        <div>${fieldLabel("Title")}<div style="${rowStyle}"><input data-field="title" type="text" placeholder="[SP-123] Short description" style="${inputStyle}"><button type="button" data-field="titleCopy" title="Copy into the session title if you like it" style="${smallBtnStyle};cursor:pointer;background:transparent">📋</button></div></div>
        <div>${fieldLabel("Pull Requests")}<div data-field="prUrlsList" style="display:flex;flex-direction:column;gap:6px"></div>
          <button type="button" data-role="add-pr" style="all:unset;cursor:pointer;color:${THEME.textFaint};font-size:11px;margin-top:6px;display:inline-block">+ Add PR</button></div>
        <div>${fieldLabel("Local Preview")}<input data-field="localUrl" type="url" placeholder="http://localhost:3000" style="${inputStyle}"></div>
        <div>${fieldLabel("Progress — what's done, what's left, what phase we're in")}<textarea data-field="progress" rows="10" placeholder="Planning / in review / ready to merge? What's left to do?" style="${inputStyle};min-height:200px;resize:vertical;font-family:inherit"></textarea></div>
        <div style="display:flex;align-items:center;justify-content:space-between">
          <span data-field="status" style="opacity:.5;font-size:11px"></span>
          <button type="button" data-role="save" style="all:unset;cursor:pointer;background:#2f6f4f;color:#eafff2;font-size:12px;padding:5px 12px;border-radius:6px">Save</button>
        </div>
      </div>
    `
    document.body.appendChild(pop)

    const prList = pop.querySelector('[data-field="prUrlsList"]')
    function addPrRow(value) {
      const row = document.createElement("div")
      row.style.cssText = rowStyle
      row.innerHTML = `
        <input data-role="pr-input" type="url" placeholder="https://github.com/org/repo/pull/123" style="${inputStyle}" value="${(value || "").replace(/"/g, "&quot;")}">
        <button type="button" data-role="pr-remove" title="Remove" style="${smallBtnStyle};cursor:pointer;background:transparent">×</button>
      `
      row.querySelector('[data-role="pr-remove"]').addEventListener("click", (e) => {
        e.stopPropagation()
        row.remove()
        if (!prList.querySelector('[data-role="pr-input"]')) addPrRow("")
      })
      prList.appendChild(row)
      return row
    }
    pop._addPrRow = addPrRow

    pop.querySelector('[data-role="add-pr"]').addEventListener("click", (e) => {
      e.stopPropagation()
      addPrRow("").querySelector('[data-role="pr-input"]').focus()
    })

    function syncJiraOpenLink(field) {
      const input = pop.querySelector(`[data-field="${field}"]`)
      const link = pop.querySelector(`[data-field="${field}Open"]`)
      const update = () => {
        const url = jiraUrl(input.value.trim())
        link.href = url || "#"
        link.style.opacity = url ? "1" : ".3"
        link.style.pointerEvents = url ? "auto" : "none"
      }
      input.addEventListener("input", update)
      update()
    }
    syncJiraOpenLink("jiraEpic")
    syncJiraOpenLink("jiraTicket")

    const titleCopyBtn = pop.querySelector('[data-field="titleCopy"]')
    titleCopyBtn.addEventListener("click", async (e) => {
      e.stopPropagation()
      const value = pop.querySelector('[data-field="title"]').value.trim()
      if (!value) return
      try {
        await navigator.clipboard.writeText(value)
        const original = titleCopyBtn.textContent
        titleCopyBtn.textContent = "✓"
        setTimeout(() => {
          if (titleCopyBtn.isConnected) titleCopyBtn.textContent = original
        }, 1200)
      } catch {
        // Clipboard API unavailable — the input is still there to select/copy manually.
      }
    })

    document.addEventListener("click", (e) => {
      if (pop.style.display === "none") return
      if (pop.contains(e.target) || e.target.closest(`[data-${GROUP_ID}] [data-role="info-toggle"]`)) return
      pop.style.display = "none"
    })
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") pop.style.display = "none"
    })

    return pop
  }

  let currentSession = null

  function setFieldValue(pop, field, value) {
    const input = pop.querySelector(`[data-field="${field}"]`)
    input.value = value || ""
    input.dispatchEvent(new Event("input")) // keeps Jira open-link href/state in sync
  }

  async function openPopoverFor(sessionId, anchorEl, worktreeForDisplay) {
    const pop = ensurePopover()
    const notes = await loadNotes(sessionId)

    pop.querySelector('[data-field="worktree"]').textContent = notes.worktree || worktreeForDisplay || "—"
    pop.querySelector('[data-field="intent"]').value = notes.intent || ""
    setFieldValue(pop, "jiraEpic", notes.jiraEpic)
    setFieldValue(pop, "jiraTicket", notes.jiraTicket)
    setFieldValue(pop, "title", notes.title)
    setFieldValue(pop, "localUrl", notes.localUrl)
    pop.querySelector('[data-field="progress"]').value = notes.progress || ""
    pop.querySelector('[data-field="status"]').textContent = ""

    const prList = pop.querySelector('[data-field="prUrlsList"]')
    prList.innerHTML = ""
    const prUrls = notes.prUrls?.length ? notes.prUrls : [""]
    for (const url of prUrls) pop._addPrRow(url)

    const saveBtn = pop.querySelector('[data-role="save"]')
    saveBtn.onclick = async () => {
      const prUrls = Array.from(prList.querySelectorAll('[data-role="pr-input"]'))
        .map((input) => input.value.trim())
        .filter(Boolean)
      const next = {
        intent: pop.querySelector('[data-field="intent"]').value,
        jiraEpic: pop.querySelector('[data-field="jiraEpic"]').value.trim(),
        jiraTicket: pop.querySelector('[data-field="jiraTicket"]').value.trim(),
        title: pop.querySelector('[data-field="title"]').value.trim(),
        prUrls,
        localUrl: pop.querySelector('[data-field="localUrl"]').value.trim(),
        progress: pop.querySelector('[data-field="progress"]').value,
      }
      await saveNotes(sessionId, next)
      const status = pop.querySelector('[data-field="status"]')
      status.textContent = "Saved ✓"
      await renderChips(sessionId)
      setTimeout(() => {
        if (status.isConnected) status.textContent = ""
      }, 1500)
    }

    const rect = anchorEl.getBoundingClientRect()
    pop.style.top = `${rect.bottom + window.scrollY + 6}px`
    pop.style.left = `${Math.max(8, rect.right + window.scrollX - 380)}px`
    pop.style.display = "block"
    pop.querySelector('[data-field="progress"]').focus()
  }

  function togglePopover(sessionId, anchorEl, worktreeForDisplay) {
    const pop = ensurePopover()
    if (pop.style.display !== "none") {
      pop.style.display = "none"
      return
    }
    openPopoverFor(sessionId, anchorEl, worktreeForDisplay)
  }

  async function renderChips(sessionId) {
    const { directory, title: sessionTitle } = await resolveSessionMeta(sessionId)

    const group = ensureChipGroup(sessionTitle)
    if (!group) return

    const pop = document.getElementById(POPOVER_ID)
    const popoverOpen = !!pop && pop.style.display !== "none"
    const synced = await maybeSyncFromAgent(sessionId, directory, popoverOpen)
    const notes = synced || (await loadNotes(sessionId))

    // Branch/worktree come SOLELY from what the agent explicitly reported
    // (notes.branch/notes.worktree, written by session-notes_set after
    // running git in whatever directory it actually worked in) — never from
    // a live /vcs lookup against the session's own default directory. That
    // live lookup has no way to know about a worktree the agent created
    // mid-session, so it would show the wrong branch whenever the agent
    // works somewhere other than where the session started. No fallback:
    // if the agent hasn't reported it yet, show nothing rather than guess.
    const branch = notes.branch || ""
    const worktreeForDisplay = notes.worktree || directory || ""
    const chips = []
    if (branch) {
      chips.push(
        `<span title="${worktreeForDisplay}" style="font:12px/1 -apple-system,sans-serif;` +
          `color:var(--v2-icon-icon-accent, #8ab4f8);padding:3px 2px">⎇ ${branch}</span>`,
      )
    }
    if (notes.jiraTicket) chips.push(chip(jiraUrl(notes.jiraTicket), notes.jiraTicket, "#5aa9e6"))
    for (const prUrl of notes.prUrls || []) {
      const prNumber = prNumberFromUrl(prUrl)
      chips.push(chip(prUrl, prNumber ? `PR#${prNumber}` : "PR", "#7cd992"))
    }
    if (notes.localUrl) chips.push(chip(notes.localUrl, "Preview", "#f0c674"))

    const hasNotes = !!(
      notes.intent ||
      notes.jiraEpic ||
      notes.jiraTicket ||
      notes.prUrls?.length ||
      notes.localUrl ||
      notes.progress
    )
    chips.push(
      `<button type="button" data-role="info-toggle" title="${hasNotes ? "Edit notes" : "Add notes"}" style="all:unset;cursor:pointer;
        display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:999px;
        background:${hasNotes ? "rgba(124,217,146,0.18)" : "var(--v2-overlay-simple-overlay-hover, rgba(127,127,127,0.12))"};
        color:${hasNotes ? "#7cd992" : "var(--v2-text-text-faint, #c7cad1)"};font-size:12px;line-height:1">ⓘ</button>`,
    )
    group.innerHTML = chips.join("")

    const toggleBtn = group.querySelector('[data-role="info-toggle"]')
    toggleBtn?.addEventListener("click", (e) => {
      e.stopPropagation()
      togglePopover(sessionId, toggleBtn, worktreeForDisplay)
    })
  }

  async function refresh() {
    if (contextDead) return
    if (!isOpenCodePage()) return
    const sessionId = currentSessionId()
    if (!sessionId) return

    if (sessionId !== currentSession) {
      currentSession = sessionId
      const pop = ensurePopover()
      pop.style.display = "none" // close popover when switching sessions
    }

    await renderChips(sessionId)
  }

  document.addEventListener(
    "click",
    (e) => {
      if (e.target.closest("[data-titlebar-tab-slot]")) setTimeout(refresh, 50)
    },
    true,
  )

  refresh()
  pollTimer = setInterval(refresh, POLL_MS)
})()

# Preview Environment Reference

All endpoints are on `https://puppetmaster.staging.profinda.io` and require the
`X-Agent-Token: ${PUPPETMASTER_AGENT_TOKEN}` header. None of them need kubectl,
Docker, or AWS credentials — Puppetmaster does all cluster work server-side.

## Endpoints

### `POST /webhooks/provision_preview_environment` — create

| Param | Required | Default | Notes |
|---|---|---|---|
| `api_branch` | Yes | — | API (or Lite API) branch name |
| `hal_branch` | No | `staging` | |
| `aida_branch` | No | `staging` | |
| `ui_branch` | No | — | premiumui branch already deployed by CI (`POST /webhooks/new_ui`). Omit to skip UI wiring entirely. |
| `friendly_name` | No | `api_branch` | Human label — use the Jira key, e.g. `SP-8502` |
| `vertical` | No | `professional_service` | or `system_integrator`, `healthcare` |
| `neo4j_version` | No | `4.4` | or `5.26.29` |
| `size` | No | `xxs` (~100 profiles) | or `xs` (~500), `s` (~1,000), `l` (~10,000) |
| `snapshot` | No | `true` | only for `size=l`: restore from snapshot (fast) vs. generate live (slow) |

Responds `201` with the shared payload below, plus `ui_branch` (the raw input —
not persisted, so it won't reappear on later status polls). Responds `422` with
`{"errors": [...]}` if any branch has no image/deployment yet, or `env_name`
(derived from `friendly_name`) isn't a valid Kubernetes namespace.

### `GET /webhooks/preview_environments/:env_id` — poll status

Use this, not the human-facing `GET /preview_environments/:id` — that route
requires a Google SSO session and rejects `X-Agent-Token` with a redirect, not
JSON. Responds `200` with the shared payload below, or `404` if `env_id` is
unknown (e.g. auto-deleted after 10 days paused).

### `PATCH /webhooks/preview_environments/:env_id/resume` — resume a paused env

Only valid when status is `"paused"`; otherwise `422`. Resuming is async — the
response still shows `"paused"` immediately after a successful `202`. Keep
polling the status endpoint afterward, same as after creation.

## Shared response payload

`provision_preview_environment`, the status endpoint, and `resume` all return
this shape (create also adds `ui_branch`):

```json
{
  "env_id": "...", "name": "preview-b324fb", "friendly_name": "SP-8502",
  "status": "available", "api_branch": "...", "hal_branch": "...", "aida_branch": "...",
  "ui_slug": "sp-8502", "api_url": "https://api-preview-b324fb.staging.profinda.io",
  "hal_url": "https://hal-preview-b324fb.staging.profinda.io",
  "ui_wired_url": "https://sp-8502.multi.profinda-staging.com/index.html?api_endpoint=...&development_domain=...",
  "vertical": "professional_service", "neo4j_version": "4.4", "size": "xxs", "snapshot": true,
  "permanent": false, "pods": { "running": 12, "total": 12, "all_running": true },
  "puppetmaster_url": "https://puppetmaster.staging.profinda.io/preview_environments/..."
}
```

`ui_slug`/`ui_wired_url` are `null` when no `ui_branch` was requested. `pods` can
be `null` transiently (e.g. right after creation, before the namespace exists) —
don't treat `null` as failure, just poll again.

## Status enum

`scheduled_for_creation` → `creation_in_progress` → `available` (or `error`).
Separately: `paused` → `resuming` → `available` (or `error`). Also seen:
`update_in_progress`, `pausing`, `deletion_in_progress`.

## Lifecycle

Every non-permanent environment is auto-paused at **19:00 UTC** daily, and
destroyed after **10 days** paused. If you're reusing a saved `env_id`, always
poll status first — `paused` means resume before use; `error`/`404` means
start over with a fresh create call.

## No-API-PR case (UI-only ticket)

If a ticket only has a premiumui PR, don't provision a Puppetmaster environment
at all — there's no API branch to deploy. Derive the UI URL directly and point
it at standard `staging` (already its default backend, no wiring needed):

1. Take the UI branch name, replace every non-alphanumeric character with `-`,
   lowercase it, truncate to 62 characters.
2. `https://<slug>.multi.profinda-staging.com`

Standard long-lived UI URLs (no preview environment involved):

| Target branch | URL |
|---|---|
| `staging` | `https://staging.multi.profinda-staging.com` |
| `integration` | `https://integration.multi.profinda-staging.com` |
| `uat` | `https://uat.multi.profinda-staging.com` |
| `production` | `https://production.multi.profinda-staging.com` |

## Manually wiring a UI build without `ui_branch`

`ui_wired_url` in the response already does this for you when you pass
`ui_branch` at creation. To point a *different* already-deployed UI build at
this environment afterward (or if you skipped `ui_branch`), open the UI URL and
run in the browser console:

```js
PF.Initializers.customizeConfig({
  environment: 'puppetmaster',
  api_endpoint: 'https://api-<name>.staging.profinda.io',
  development_domain: '<seed_account_domain>.<name>.profinda-staging.com'
})
```

Or use the query-string form Puppetmaster generates: append
`?api_endpoint=<encoded api_url>&development_domain=<encoded development_domain>`
to the UI's `index.html`. `development_domain` isn't in the response payload —
it's `<seed_account_domain>.<name>.profinda-staging.com`, where
`seed_account_domain` is `communities` for every vertical except `healthcare`
(`riverside-health`).

## Known limitations

- **No lookup-by-branch endpoint.** There's no way to ask "does an environment
  already exist for `api_branch=X`?" — every create call makes a new one. Save
  `env_id` somewhere reusable (a Jira comment, your session notes) if you expect
  to come back to the same environment.
- **`ui_branch` requires prior UI CI.** It resolves against `UiDeployment`
  records pushed by premiumui's CircleCI `build_for_multistaging` job — if that
  branch's UI build hasn't run yet, you'll get a `422`, same as a missing
  API/HAL/AIDA image.

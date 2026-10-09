---
name: profinda-preview-environment
description: Provision and monitor ProFinda preview environments — API/HAL/AIDA and optionally a wired UI build — via Puppetmaster's agent API, with no kubectl, Docker, or AWS credentials required. Environments always run on the shared `multistaging` cluster and default to the `staging` branch, but any branch combination can be requested, including `integration`/`uat`/`production` branches. Use when an agent needs a live ProFinda stack to reproduce a bug or test a feature end to end (especially from a sandbox that cannot run docker-compose locally), or when the user mentions "preview environment", "puppetmaster", or a staging environment for a specific branch/Jira ticket.
---

# ProFinda Preview Environments

Puppetmaster (`https://puppetmaster.staging.profinda.io`) provisions full ProFinda
stacks — API (or Lite API), HAL, AIDA, Neo4j, Elasticsearch, Postgres, Redis — as
Kubernetes namespaces on the `multistaging` EKS cluster, plus an optional wired UI
build. Every action below is a plain HTTPS call, so it works from any sandbox.

**"Staging" here is the infrastructure, not the code under test.** Every
environment runs on the same `multistaging` cluster regardless of which branch
you point it at. `hal_branch`/`aida_branch` default to `staging` when omitted,
and that's the right default for most bug repro/feature work — but any branch
is valid for any of `api_branch`/`hal_branch`/`aida_branch`, including
`integration`, `uat`, `production`, or a feature branch, if you specifically
need to reproduce something against that branch's code.

## When to use this

Use it when you need the **real** ProFinda stack — a specific combination of
branches, or the UI talking to a specific API — and can't or don't want to run
`docker-compose` locally (sandboxed session, need the UI too, or testing exactly
what CI built). Don't use it when a local stack already answers the question
faster, or when the ticket has no backend PR (see [REFERENCE.md](REFERENCE.md)
for the UI-only case).

It's a shared cluster: reuse an existing environment for the same branch
combination if you already have its `env_id` (e.g. from a Jira comment or your
own session notes) rather than creating a duplicate.

## Setup

Requires `PUPPETMASTER_AGENT_TOKEN` (1Password → "Puppetmaster Agent API Token")
sent as the `X-Agent-Token` header on every call below.

## Quick start

```bash
# 1. Create (only api_branch is required)
curl -s -X POST "https://puppetmaster.staging.profinda.io/webhooks/provision_preview_environment" \
  -H "X-Agent-Token: ${PUPPETMASTER_AGENT_TOKEN}" -H "Content-Type: application/json" \
  -d '{"api_branch": "feature/SP-1234", "ui_branch": "SP-1234", "friendly_name": "SP-1234"}'
# => 201 { "env_id": "...", "name": "preview-b324fb", "status": "scheduled_for_creation", ... }

# 2. Poll until status is "available" (see Readiness below for what "available" does NOT guarantee)
curl -s "https://puppetmaster.staging.profinda.io/webhooks/preview_environments/<env_id>" \
  -H "X-Agent-Token: ${PUPPETMASTER_AGENT_TOKEN}"

# 3. Once available, smoke-test before trusting it:
curl -sf https://api-preview-b324fb.staging.profinda.io/health   # expect "all good"
```

`ui_branch` is optional — omit it if the ticket doesn't need a dedicated UI build.
Full parameter table, response shape, and the no-API-PR case: [REFERENCE.md](REFERENCE.md).

## The readiness sequence — don't stop at step 1

`status: "available"` means Helm succeeded, **not** that the app has finished
booting or seeding. Work through all four layers before treating the
environment as usable:

| # | Check | Signal |
|---|---|---|
| 1 | Poll status | `status == "available"` (`"error"` = stop and report; `"paused"` = resume first, see [REFERENCE.md](REFERENCE.md)) |
| 2 | Pod counts (from the same response, no kubectl needed) | `pods.all_running == true` |
| 3 | App health | `GET {api_url}/health` and `GET {hal_url}/health` both return `200` |
| 4 | UI reachable (if wired) | `GET {ui_wired_url}` returns `200` |

New environments take 5–20 minutes; resuming a paused one takes 5–25 minutes.
Step 3 alone can add up to ~17 more minutes after step 1 for Rails to finish
seeding — poll steps 1–2 every ~60 seconds, then retry step 3 every ~30 seconds
once `available`. Never report an environment as ready on status alone.

## Signing in to the environment

`ui_wired_url` loads the UI against the preview API. The page redirects to `/users/signin` and drops the query string; the `api_endpoint` and `development_domain` values stay in localStorage, so that is normal.

- The only login with a known password is the seeded account owner `admin@example.net`; its password is the environment's own owner password (a cluster Secret), which you must get from the person or team that provisioned it. Other seeded users have random passwords: sign in as the owner and create or reset them in Admin > Users. Passwords from other staging tenants (including the 1Password "Communities - [Staging]" items) do not work here.
- The sign-in form has only Email and Password. The UI first calls `GET <api_url>/api/v2/accounts/<development_domain>` and takes `full_domain` from the answer (for example `communities.staging.profinda.io`); that value is the `Account` header of the token call and of all later API calls, not the `development_domain`.
- The token call is `POST <api_url>/api/oauth/token` with JSON `grant_type=password`, `client_id`, `username`, `password`. `client_id` is injected at runtime (`window.PF.config.client_id`); the build placeholder is invalid.
- A wrong `Account` header and a wrong `client_id` return the same `401 invalid_password` as a wrong password, so when replaying the call with curl copy both from the UI's own request before blaming the password.

## Paused environments answer 502

Every non-permanent environment is paused daily at 19:00 UTC. A paused namespace only runs an ingress fallback, so all API paths, including OPTIONS and `/health` through the proxy, return an nginx `502`, and the UI shows "temporary issue with our servers" (the CORS error in the console is a side effect). Resume it (`PATCH .../resume`, or the Resume button on `puppetmaster_url`), then wait for the readiness sequence above; confirm with a real call such as the account lookup returning `200`. Keep the `env_id` (the UUID in the `puppetmaster_url`): there is no lookup by name or branch, and the agent API cannot make an environment permanent, which is a setting on the Puppetmaster page.

## Common failures

| Response | Meaning | Action |
|---|---|---|
| `422` on create, "No Docker image found for \<branch\>" | CI for that branch hasn't pushed an image yet | Check CircleCI for that branch, wait, retry — not a request bug |
| `422` on create, "No UI deployment found for ui_branch" | premiumui CI hasn't deployed that branch yet | Check CircleCI for the UI branch, or omit `ui_branch` |
| `401` | Missing/wrong `X-Agent-Token` | Check `PUPPETMASTER_AGENT_TOKEN` |
| `404` on status/resume | Unknown `env_id` | Double check the id; environments paused >10 days are auto-deleted |
| `422` on resume | Status isn't `"paused"` | Only resume when polling shows `"paused"` |

Full endpoint reference, request/response shapes, status enum, and the
no-API-PR / manual UI-wiring cases: [REFERENCE.md](REFERENCE.md).

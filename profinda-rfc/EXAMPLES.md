# Example RFC: 0001 — Adopt URL-Based Versioning for All External APIs

> This is a worked example showing a correctly filled RFC. Skipped sections use "_Skipped by author._"

---

# 0001 — Adopt URL-Based Versioning for All External APIs

> **Summary:** ProFinda's external APIs have no versioning contract, forcing breaking changes
> on partners without warning. This RFC proposes URL-based versioning (`/api/v1/`) as the
> standard across all externally-consumed Rails endpoints to enable safe, predictable evolution
> of the API surface.

---

## Abstract

ProFinda exposes REST APIs consumed by partner integrations and the TypeScript frontend.
Today there is no versioning — breaking changes ship with the next deploy. This RFC proposes
adopting URL-based versioning (`/api/v1/`, `/api/v2/`) as the standard. Primary benefit:
partners can pin to a version and migrate on their own schedule. Primary risk: maintaining
multiple versions in parallel increases maintenance surface. Estimated cost: 2 weeks to
retrofit existing endpoints; low ongoing cost with disciplined deprecation policy.

## Problem

Breaking API changes have caused three partner integration failures in the past six months:
- **March 2026**: renamed `worker_id` → `resource_id` in the Assignments endpoint broke two
  partner integrations simultaneously; 4 hours of emergency support
- **January 2026**: removed `availability.legacy_format` field without notice; one partner
  had to ship a hotfix within 24 hours
- **November 2025**: response envelope restructure broke the Workforce Planning partner's
  nightly sync job

No versioning contract exists. Partners have no way to know when a breaking change is coming
or how to avoid it. The frontend TypeScript codebase is partially insulated by a BFF layer,
but partner integrations are not.

## Solution

Introduce URL-based versioning as the API contract standard:
- All externally-consumed endpoints move under `/api/v1/`
- New breaking changes ship under `/api/v2/` (or higher) without removing the prior version
- Versions are deprecated with a minimum 90-day notice period; deprecation is signalled via
  a `Deprecation` response header and communicated to partners in writing
- Internal-only and BFF endpoints are exempt — versioning applies to partner-facing APIs only

Success measured by: zero unannounced breaking changes to partner integrations in the 12
months following rollout; all partner integrations confirmed pinned to an explicit version
within 60 days.

## Anticipated Difficulties

- **Retrofitting existing endpoints** — existing routes must be namespaced under `/api/v1/`
  without breaking current consumers. Mitigation: add `/api/v1/` routes alongside existing
  routes; deprecate unversioned routes with a 90-day runway; communicate to all partners
  before cutover.
- **Rails routing complexity** — nested versioned namespaces can become messy.
  Mitigation: use Rails `namespace :v1` blocks; establish a routing conventions doc at
  time of implementation.
- **Knowing which endpoints are partner-facing** — no current inventory exists.
  Mitigation: audit as part of implementation; block merge of v1 namespace until audit complete.

## Risks

- Parallel version maintenance could be abandoned under deadline pressure, defeating the purpose.
  Likelihood: medium. Mitigation: make version retirement a product-level decision requiring
  explicit sign-off, not an engineering shortcut.
- Partners ignore the deprecation notice and break anyway at cutover. Likelihood: low with
  90-day window and direct communication. Impact: manageable — same as today but with more notice.

## Previous Examples

- Stripe's API versioning (date-based) is the canonical external example. Their model is more
  complex than we need; URL versioning is simpler and sufficient for our partner count (<10 active).
- GitHub's REST API uses URL versioning (`/v3/`, `/v4/`); well understood by partner developers.
- Internal: we attempted informal "don't break partners" social contracts in 2024. Three
  incidents above prove this does not scale.

## Expert Opinion

_Skipped by author._

## Estimated Costs

- Development / rollout: ~2 weeks (1 senior Rails engineer; routing + audit + partner comms)
- Tooling: none — standard Rails namespacing, no additional gems required
- Reskilling: half-day engineering sync to align on conventions; written routing guide

## Implementation

1. **PoC** — namespace the Assignments endpoint under `/api/v1/`; validate partner can pin to it;
   confirm no regression on unversioned route during transition period
2. **Scale** — audit all partner-facing endpoints; move all under `/api/v1/`; deprecate
   unversioned routes with `Deprecation` header; notify all partners in writing
3. **Enforce** — add PR checklist item: "Is this endpoint partner-facing? Is it under a version
   namespace?"; new endpoints default to current stable version

## Completion & Evaluation

- **30 days**: all partner-facing endpoints under `/api/v1/`; all partners notified; unversioned
  routes returning `Deprecation` header
- **90 days**: all partners confirmed pinned to `/api/v1/`; unversioned routes removed;
  zero breaking change incidents since rollout
- **365 days**: assess whether any partner has needed a `/api/v2/`; review deprecation policy
  based on real usage

## Rollback

Revert: re-expose unversioned routes (they were never removed during transition period, only
deprecated). No data migration required — versioning is routing-layer only.
Trigger: URL versioning causes unforeseen routing conflicts or partner adoption fails despite
90-day window and direct communication.

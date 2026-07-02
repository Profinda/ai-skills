# Example ADR: 0001 — Use PostgreSQL as Primary Write Store for the Workforce Matching Context

> This is a worked example showing a correctly filled ADR. No guide text, no `{...}` placeholders.

---

# 0001 — Use PostgreSQL as Primary Write Store for the Workforce Matching Context

We chose PostgreSQL as the sole write store for the Workforce Matching bounded context.
Neo4j handles relationship traversal for candidate-role matching, but all authoritative
write operations (worker profiles, assignments, availability) are owned by PostgreSQL
to avoid dual-write complexity and to keep our Rails ActiveRecord stack coherent.

---

### Context

The Workforce Matching context manages worker profiles, availability windows, and
assignment records. During initial design we considered co-locating writes in Neo4j
alongside relationship traversal, since the matching algorithm is graph-native.
However, the Rails engineering team has deep PostgreSQL expertise and zero Neo4j
write-path experience. We also have existing compliance obligations around audit
logging that are well-served by PostgreSQL's WAL. Doing nothing (dual-write to both)
was assessed and rejected early: it introduces a consistency window with no clear
owner for conflict resolution.

### Decision

PostgreSQL is the authoritative write store for all Workforce Matching domain objects.
Neo4j is read-only from the perspective of this context — the Rails application
projects denormalised data into Neo4j via background jobs after each write.
This means a future engineer can trust that any mutation goes through ActiveRecord
and the PostgreSQL schema; Neo4j state is always derivative.

### Consequences

- Rails team can use standard ActiveRecord patterns, migrations, and tooling
- Audit log via WAL is available without additional instrumentation
- Compliance requirements (GDPR deletion, field-level history) are met by existing PG tooling
- Neo4j projection lag is accepted: matching results may reflect state up to ~2s old
- Any Neo4j write failure does not corrupt authoritative state — only delays projection
- Background job monitoring is now a critical operational concern (dead jobs → stale graph)
- If the matching algorithm ever requires consistent reads from both stores simultaneously,
  this decision must be revisited (see Follow-up ADRs)

#### Follow-up ADRs

See ADR-0002 — Neo4j Projection Job Failure Handling Strategy

### Alternatives

**Dual-write from Rails to PostgreSQL and Neo4j synchronously**
Attractive because it keeps Neo4j always consistent with PG. Rejected because it
couples request latency to Neo4j write performance and creates a split-brain failure
mode with no clear resolution strategy.

**Neo4j as primary write store with PostgreSQL as reporting replica**
Attractive because it removes the projection job entirely. Rejected because the Rails
team has no Neo4j write-path experience, ActiveRecord ORM support is immature, and
GDPR compliance tooling does not exist for Neo4j in our stack.

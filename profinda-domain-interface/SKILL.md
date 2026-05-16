---
name: profinda-domain-interface
description: ProFinda public API layer for engine data access built on CommonEngine::Domain::Interface. Covers reading, writing, creating, or calling Domain methods. Use when user mentions `Domain::`, `extend CommonEngine::Domain::Interface`, `Proxy`, `Schemas::Scope` or creating a new Domain class.
---

# Domain Interface

## Quick Start

```ruby
# Query — builder chain + result
result = Domain::Things.where(account_id: 1, status: 'active').find_all
result.success?  # => true/false
result.output    # => immutable AR scope

# Single record
result = Domain::Things.where(id: 42).find
result.output!   # => record or raises on failure

# Mutate
Domain::Things.where(account_id: 1, id: [1, 2]).update_all(status: 'archived')

# Custom method
Domain::Things.archive(id: 42, reason: 'obsolete')
```

## Parameter Convention: `:required` and `:optional`

Domain method signatures use `:required` and `:optional` as sentinels — documentation only, stripped at runtime:

```ruby
def where(account_id: :required, id: :optional)
  super
end
```

Actual default values (e.g., `false`, `nil`) pass through as real defaults.

## Calling Domain Methods

```ruby
# Builder chaining
ProfileActivities::Domain::Shortlists
  .where(activity_id: role.id, state: 'pending')
  .not(profile_id: excluded_ids)
  .find_all
  .output

# find / find_by
result = Domain::Things.where(id: 1).find         # error if not found
result = Domain::Things.where(account_id: 1).find_by(status: 'active')  # nil-safe

# create — readonly record
result = Domain::Things.create(account_id: 1, name: 'X', creator_id: 5)

# update_all / delete_all — require prior where()
Domain::Things.where(account_id: 1, id: [1, 2, 3]).update_all(status: 'archived')
Domain::Things.where(account_id: 1, status: 'draft').delete_all

# result access
result.success?   # true/false
result.output     # the data
result.output!    # raises if failed
result.errors     # error hash

# composing inside Domain classes
def complete(activity_id:, completed_by:)
  where(activity_id:).update_all(state: Review::COMPLETE, completed_by:)
end
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Treating `.output` as mutable AR | Output is immutable; mutate through Domain methods only |
| Calling `update_all`/`delete_all` without `where()` | Add scope first: `Domain::X.where(id:).update_all(...)` |
| Passing unknown keys to `where()` | Only whitelisted keys from the Domain's `where` signature are allowed |
| Forgetting `Schemas::Scope` when creating new Domain | Every Domain needs a matching `Schemas::Scope` class |
| Using `.find_all.output.update_all(...)` | Returned scope is immutable; use `Domain::X.where(...).update_all(...)` |
| Not checking `result.success?` before using `.output` | Always check or use `result.output!` to raise on failure |
| Expecting `params[:scope]` in a Create operation | `create` only receives `params: { arguments: }` — no scope |
| Assuming all Domain classes use Interface | Some older domains call Operations directly — check for `extend Interface` first |
| Calling non-proxy methods expecting proxy behaviour | Some methods bypass `super` — check the Domain source |

## More Detail

See [REFERENCE.md](REFERENCE.md) for: architecture diagram, delegation chain, method types, creating a new Domain class (domain module, scope schema, operations), required files table, immutability rules, and safety constraints.

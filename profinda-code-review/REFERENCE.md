# ProFinda Code Review Reference

Detailed checklists for `/profinda-review full` and `/profinda-review fix`.

---

## Engine isolation

- [ ] Engine code does NOT reference main-app constants directly (e.g. `User`, `Profile`, `Account`)
- [ ] Data crossing engine/main-app boundary flows through Domain interfaces or operation parameters
- [ ] New engine-to-engine dependencies go through public Domain methods, not `require` of internal constants

---

## Operations (`Opera::Operation::Base`)

- [ ] Each step is a single-responsibility method
- [ ] Steps call `finish!` or `result.add_error` — never both
- [ ] Schema validation is defined at the top using `Dry::Schema`
- [ ] No business logic inside the schema block
- [ ] Operation does not reach directly into the database — delegates to models/repos
- [ ] Steps do not rescue `StandardError` broadly; rescue specific errors
- [ ] `context` is not used as a dumping ground for unrelated state

---

## Domain interfaces (`CommonEngine::Domain::Interface`)

- [ ] Public methods are defined via `extend CommonEngine::Domain::Interface`
- [ ] Proxy objects are used for cross-engine reads (not raw ActiveRecord relations)
- [ ] `Schemas::Scope` used where filtering is needed
- [ ] No raw SQL in Domain methods; use scopes or Arel
- [ ] New Domain methods have corresponding tests

---

## Actions & controllers

- [ ] Each action has a dedicated `Action` class with `Dry::Schema` validation
- [ ] Controller method is thin: delegates to Action/Operation, renders result
- [ ] Strong params replaced by schema validation — no `params.permit` in new code
- [ ] Auth check (`authorize!` or equivalent policy call) present before any data access

---

## Policies

When a new policy is added:
- [ ] Name added alphabetically to `LIST` in `engines/permissions/app/models/permissions/policy.rb`
- [ ] Feature-flag link added to `PERMISSIONS_RESTRICTED_BY_FEATURES` if applicable
- [ ] Migration uses `Permissions::Domain::Policies.setup_new_one(policy_name: '...', permitted: false)`
- [ ] Migration `down` calls `Permissions::Domain::Policies.delete(policy_name: '...')`
- [ ] Policy added (with `permitted: false`) to `contain_exactly` list in permissions spec
- [ ] Policy added to all three group blocks in `spec/requests/api/v1/saas_admin/accounts/create_spec.rb`

---

## Migrations

- [ ] New column/table has a DB index if used in queries or foreign key constraints
- [ ] Index names do not exceed PostgreSQL's 63-char limit
- [ ] `null: false` added with a default or with backfill before constraint
- [ ] `change` method is reversible; complex migrations use `up`/`down`
- [ ] No application code (model calls, constants) inside migration files

---

## Serializers

- [ ] Only exposes fields required by the API contract
- [ ] No N+1 — associations are eager-loaded at the query layer, not inside the serializer
- [ ] No business logic inside serializer methods

---

## Tests

- [ ] Happy path covered
- [ ] Error/edge paths covered (invalid input, missing auth, record not found)
- [ ] Feature flags created via FactoryBot (`create(:common_engine_feature, ...)`) — never stubbed
- [ ] `let(:feature_enabled) { true }` pattern used; disabled contexts override with `false`
- [ ] No `allow_any_instance_of`, `stub_const`, or global stubs for feature flags
- [ ] Factories used instead of `new`/`create` with inline attributes where a factory exists
- [ ] `described_class` used in unit specs instead of hardcoded class name
- [ ] Shared examples/contexts used for repeated setup (BetterSpecs)
- [ ] No `sleep` or time-dependent assertions without `travel_to`

---

## Locale files

- [ ] When a key is added or removed in one locale file, the same change is made in ALL locale files (`en.yml`, `es-ES.yml`, `fr-CA.yml`, etc.)
- [ ] Values are translated into each locale's language (not just copied from English)

---

## Code style (rubocop-enforced)

- [ ] `# frozen_string_literal: true` at top of every Ruby file
- [ ] Lines ≤ 120 characters
- [ ] Methods ≤ 20 lines (arrays/hashes/heredocs count as one line)
- [ ] Shorthand hash syntax used when key matches variable name: `{ account:, requester: }`
- [ ] No trailing commas in multiline arrays/hashes/arguments
- [ ] `require_relative` for local files; `require` for gems

---

## Security

- [ ] No user-controlled input passed to `eval`, `send`, `constantize`, or raw SQL
- [ ] `params` are validated through schema before use
- [ ] No secrets or credentials in code or spec files
- [ ] Sensitive data not logged
- [ ] File uploads validated for type and size
- [ ] External API calls wrapped in `begin/rescue`

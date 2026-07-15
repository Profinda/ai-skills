# Code Review Reference

Detailed, language-agnostic checklists for `/profinda-review full` and `/profinda-review fix`.
Project-specific additions live in `$REPO/AI_REVIEW.md` and extend or override these defaults.

---

## Bugs

- [ ] No null/nil dereferences on values that may be absent
- [ ] No off-by-one errors in loops, slices, or pagination
- [ ] Conditional logic covers all branches (no implicit fall-through)
- [ ] Error return values are checked, not silently discarded
- [ ] Resources (file handles, DB connections, network sockets) are released in all code paths
- [ ] No infinite loops or missing loop termination conditions
- [ ] Async/concurrent code does not have race conditions or missing synchronisation

---

## Security

- [ ] No user-controlled input passed to `eval`, dynamic dispatch, raw SQL, or shell commands
- [ ] All input validated/sanitised before use
- [ ] Authentication check present before any protected data access
- [ ] Authorisation (permissions/policies) checked, not just authentication
- [ ] No secrets, credentials, or API keys hardcoded in source or test files
- [ ] Sensitive data (PII, tokens) not written to logs
- [ ] File uploads validated for type, size, and safe storage path
- [ ] External HTTP/API calls have timeouts and handle failure gracefully
- [ ] Dependencies with known CVEs are flagged

---

## Typos & misspellings

- [ ] Identifiers (variables, functions, classes, modules) spelled correctly
- [ ] Comments and docstrings spelled correctly
- [ ] User-facing string literals spelled correctly
- [ ] No copy-paste remnants (e.g. wrong module name carried from another file)

---

## Naming & consistency

- [ ] Names follow the project's established conventions (camelCase, snake_case, PascalCase — as applicable)
- [ ] Consistent terminology across changed files (e.g. don't mix `user` / `account` / `member` for the same concept)
- [ ] Boolean names read as predicates (`is_active`, `has_permission`, not `active_status`)
- [ ] Functions named after what they do, not how they do it
- [ ] Constants are `SCREAMING_SNAKE_CASE` (or language equivalent)

---

## Design & architecture

- [ ] Code placed in the correct layer (presentation / business logic / data)
- [ ] No direct coupling between modules that should be isolated
- [ ] No duplicated logic that should be extracted to a shared utility
- [ ] No leaky abstractions (internal implementation details exposed via public API)
- [ ] New abstractions justified — not over-engineered for current requirements

---

## Spec & correctness (JIRA / ticket)

- [ ] Implementation matches the stated requirement/ticket
- [ ] If a JIRA/issue number is identifiable (branch name, commit message, PR description):
  - [ ] Acceptance criteria from the ticket are all addressed
  - [ ] Edge cases mentioned in the ticket are handled
  - [ ] Out-of-scope changes are flagged for discussion
- [ ] No dead code introduced that is not referenced by the new feature

---

## Linting

Detect the active linter config from the repo root before running:

| Language   | Config files to look for                                  | Linter       |
|------------|-----------------------------------------------------------|--------------|
| Ruby       | `.rubocop.yml`                                            | RuboCop      |
| JavaScript | `eslint.config.*`, `.eslintrc.*`                          | ESLint       |
| TypeScript | `eslint.config.*`, `.eslintrc.*`, `biome.json`            | ESLint/Biome |
| Python     | `pyproject.toml` (`[tool.ruff]`/`[tool.flake8]`), `.flake8`, `setup.cfg` | Ruff/Flake8 |

- [ ] No violations of rules enabled in the detected config
- [ ] Formatting rules respected (indentation, line length, trailing whitespace)
- [ ] Import/require ordering follows project convention
- [ ] Unused variables, imports, and dead assignments flagged

---

## Tests

- [ ] Happy path covered
- [ ] Error / edge paths covered (invalid input, missing auth, record not found, empty collection)
- [ ] Tests are isolated — no shared mutable state between cases
- [ ] No `sleep` or wall-clock assertions; use time-travel helpers where available
- [ ] Test names describe behaviour, not implementation (`it "returns 404 when user not found"`, not `it "calls the method"`)
- [ ] No overly broad mocks/stubs that make the test vacuous
- [ ] New public functions/methods have at least one unit test
- [ ] Integration/E2E tests added for new user-facing flows when applicable

---

## AI_REVIEW.md convention

If `AI_REVIEW.md` exists in the repo root:

1. Read the whole file before starting the review.
2. Treat its rules as **first-class** — violations are just as reportable as generic checklist items.
3. Merge its rules into the matching category above, or create an extra **"Project-specific"** section in the output for rules that don't fit elsewhere.
4. If `AI_REVIEW.md` explicitly disables a generic rule, skip that rule for this repo.

### Suggested `AI_REVIEW.md` structure (for teams bootstrapping it)

```markdown
# AI Review Rules — <Project Name>

## Stack
- Language: Ruby 3.3 / Rails 7.2
- Linter: RuboCop (`.rubocop.yml`)
- Test framework: RSpec + FactoryBot

## Architecture rules
- Engine code must not reference main-app constants directly.
- Business logic lives in Operations, not controllers or models.

## Naming conventions
- Services are suffixed `*Service`; operations are suffixed `*Operation`.

## Security additions
- All API endpoints require a signed JWT in `Authorization: Bearer`.

## Disabled generic rules
- Ignore the "Boolean names read as predicates" rule — we use `active` not `is_active`.
```

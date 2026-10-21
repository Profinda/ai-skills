---
name: profinda-write-a-test
description: Rules for writing minimal, behaviour-focused tests — what makes a test good or bad, which tests to skip, and language-specific guides (Ruby/RSpec, TypeScript/Vitest + React Testing Library). Use when writing, adding, reviewing, or deleting tests/specs, fixing bugs test-first, or when user mentions RSpec, Vitest, React Testing Library, specs, test coverage, or `_spec.rb` / `.spec.ts` / `.spec.tsx` files.
---

# Writing Tests

Write the **fewest tests that prove the change works** through its public API. Every test is code to
maintain; a test that doesn't protect real behaviour is a cost, not coverage.

## Workflow

1. Identify the **public behaviour** the change adds or alters (return values, persisted state readable
   through the API, HTTP responses, raised errors, emitted events at system boundaries).
2. List the minimal cases: happy path + edge/invalid cases that the change actually introduces.
3. Check existing specs — extend or reuse before adding. Drop any case already covered.
4. **Ask the user before adding** any spec not on that minimal list (see "Ask first").
5. Load the language guide below and write the specs.
6. Run only the touched spec files; make sure each new test fails without the change.

## Bug fixes: test first

Fix bugs red → green; features follow the workflow above.

1. **Red** — write one test reproducing the bug through the public API. Run it; confirm it fails for
   the reported reason (not a typo or setup error).
2. **Green** — write only enough code to pass it. No speculative fixes or extra features.
3. Run the touched spec files. Refactoring belongs in review, not in the fix.

One bug = one regression test, unless it hides several distinct behaviours.

## Language guides

| Language / framework | Guide |
|---|---|
| Ruby / RSpec | [rspec.md](rspec.md) |
| Ruby / FactoryBot | [factory-bot.md](factory-bot.md) |
| Ruby / Sidekiq jobs | [rspec-sidekiq.md](rspec-sidekiq.md) |
| Ruby / SQL query counts | [rspec-sqlimit.md](rspec-sqlimit.md) |
| TypeScript / Vitest + React Testing Library | [vitest-rtl.md](vitest-rtl.md) |

Always load the matching guide before writing tests in that language. Ruby: always `rspec.md`, plus each
gem guide the spec touches (factories, jobs, query counts). TypeScript front-end: always `vitest-rtl.md`,
and check the repo's `AGENTS.md` for its test helpers and setup.

## Rules

**Test behaviour, not implementation.**
- Exercise the public API only. Never test private methods, instance variables, constants, or internals.
- Don't assert on call counts/order or mock internal collaborators — mock only system boundaries
  (HTTP, external services, time, randomness).
- A pure refactor (no behaviour change) needs **no new tests**; existing ones must pass unchanged.
- Name tests by WHAT happens, not HOW.

**No redundant tests.**
- One behaviour = one test location. Don't re-test the same thing at model, service, and request level.
- Don't test framework/library behaviour (ActiveRecord validations wiring, Rails routing, gem internals).
- Don't add tests for trivial code: attribute readers, delegations, constants, plain config.
- Don't duplicate a case with different but equivalent input.

**Removed code gets removed tests.**
- When deleting functionality, delete its specs. Never add a test proving removed code no longer
  works/exists (e.g. "does not respond to `#old_method`", "route no longer exists").

**No tautologies.** Expected values are independent literals, never recomputed the way the code does.

See [GOOD-AND-BAD.md](GOOD-AND-BAD.md) for examples of each rule.

## Ask first

Before writing a test outside the minimal list, stop and ask the user, stating:
1. the test you want to add, 2. what behaviour it protects, 3. why existing tests don't cover it.

Typical candidates that need approval: extra edge cases not introduced by the change, performance/query
count specs, tests for unchanged code, new shared examples, new spec files for untouched classes.

## Checklist

- [ ] Each test exercises public API and survives an internal refactor
- [ ] No test of private methods, ivars, call counts, or internal mocks
- [ ] No duplicate coverage across layers or cases
- [ ] No tests for removed code or pure refactors
- [ ] Expected values are literals, not recomputed
- [ ] Each new test fails when the change is reverted
- [ ] Any test beyond the minimal list was approved by the user
- [ ] Language guide followed

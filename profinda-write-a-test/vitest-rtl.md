# Vitest + React Testing Library Guide

TypeScript front-end test conventions for Vitest, React Testing Library and user-event.
The general rules in [SKILL.md](SKILL.md) win on conflict — especially "minimal tests" and "ask first".

These are the rules for **new** tests. Existing specs that predate them are grandfathered: don't
migrate them, and don't copy them (see [Patterns you'll see that are not the rule](#patterns-youll-see-that-are-not-the-rule)).

## Contents

- [File standards](#file-standards)
- [Structure](#structure)
- [What to unit test](#what-to-unit-test)
- [Rendering](#rendering)
- [Hooks](#hooks)
- [Queries and assertions](#queries-and-assertions)
- [Interaction](#interaction)
- [Async](#async)
- [Mocking boundaries](#mocking-boundaries)
- [React Query](#react-query)
- [Zustand](#zustand)
- [Fake timers](#fake-timers)
- [Mock cleanup](#mock-cleanup)
- [it.each over near-duplicate tests](#iteach-over-near-duplicate-tests)
- [Patterns you'll see that are not the rule](#patterns-youll-see-that-are-not-the-rule)

## File standards

Name the file after the unit under test: `[UnitName].spec.tsx` for components, `[unit_name].spec.ts`
for hooks and utilities. **Colocate** it next to the source file.

```
// bad: parked in a separate tests folder, away from the code it covers
core/helpers/tests/format_date.spec.ts

// good
core/helpers/format_date.ts
core/helpers/format_date.spec.ts
```

## Structure

One top-level `describe` named after the unit. Nest a `describe` per state or prop configuration.
`it` describes the observable outcome, not the mechanics.

```tsx
// bad
describe("tests for the Avatar component", () => {
  it("works", () => {});
  it("test 2 - calls the handler", () => {});
});

// good
describe("<Avatar />", () => {
  it("renders the user's initials when no image is set", () => {});

  describe("when the image fails to load", () => {
    it("falls back to the initials", () => {});
  });
});
```

## What to unit test

- **Utilities and hooks** — the clearest candidates. They hold logic in isolation.
- **Components with logic of their own** — conditional rendering, derived state, event handling.
- **Not assembly components.** A component that only wires together already-tested children has no
  behaviour of its own; a test for it asserts the composition, breaks on every layout change, and
  protects nothing.

Cover the key behaviours, edge cases and failure paths — not every input permutation. Many tests for
one unit is a sign of over-testing, not thoroughness.

## Rendering

If the repo provides a custom render helper that wires the global providers (query client, router,
theme, app context), use it. Never hand-roll a provider wrapper per test — it drifts from the real
provider tree, so the test stops reflecting the app.

```tsx
// bad: a bespoke provider tree that will rot
const wrapper = ({ children }) => (
  <QueryClientProvider client={new QueryClient()}>
    <BrowserRouter>{children}</BrowserRouter>
  </QueryClientProvider>
);
render(<ProfileCard />, { wrapper });

// good: the repo's helper, which mirrors the real provider tree
renderWithProviders(<ProfileCard />);
```

Plain `render` from `@testing-library/react` is correct for a component that needs no providers.
The repo's `AGENTS.md` names its actual helper, where it lives, and what it supplies — the name
above is a placeholder.

## Hooks

Use `renderHook`, with the provider-aware variant if the repo has one. Wrap state updates in `act`.

A hook's returned values **are** its public API, so asserting on them is testing behaviour, not
implementation — the "don't assert on internal state" rule does not apply here.

```ts
// good
const { result } = renderHook(() => useCounter({ initial: 2 }));

act(() => result.current.increment());

expect(result.current.count).toBe(3);
```

## Queries and assertions

Query the way a user finds things: `getByRole` with an accessible name first, then label text, then
text. Reach for a test id only when nothing else identifies the element.

**No snapshot tests.** A snapshot doesn't say what behaviour it protects, and it gets regenerated
without being read. Assert the specific thing that matters.

```tsx
// bad
const { container } = render(<PriceTag amount={1000} />);
expect(container).toMatchSnapshot();

// good
render(<PriceTag amount={1000} />);
expect(screen.getByText("$1,000.00")).toBeInTheDocument();
```

Assert on what the user sees or the outcome produced — never on CSS classes, DOM structure or
internal state.

```tsx
// bad: couples the test to the stylesheet
expect(container.querySelector(".modal")).toHaveClass("is-open");

// good
expect(screen.getByRole("dialog")).toBeInTheDocument();
```

## Interaction

Use `userEvent`, created per test with `userEvent.setup()`. It fires the full sequence of events a
real interaction produces (pointer, focus, keyboard), so it catches bugs `fireEvent` walks past.

```tsx
// bad: a single synthetic event, no focus or pointer sequence
fireEvent.click(screen.getByRole("button", { name: "Save" }));

// good
const user = userEvent.setup();
await user.click(screen.getByRole("button", { name: "Save" }));
```

`fireEvent` is a last resort, for events `userEvent` cannot express (`scroll`, synthetic drag, a
direct `change` on an input a library controls). Say why in a comment when you use it.

## Async

Prefer, in order: `findBy*` → `waitFor` → never a manual wait.

```tsx
// bad: a timer race dressed up as a test
await new Promise((resolve) => setTimeout(resolve, 100));
expect(screen.getByText("Saved")).toBeInTheDocument();

// bad: waitFor wrapping a query findBy already does
await waitFor(() => expect(screen.getByText("Saved")).toBeInTheDocument());

// good
expect(await screen.findByText("Saved")).toBeInTheDocument();
```

Use `waitFor` only for a condition that isn't "an element appeared" — a mock called, a store
settled, a value recomputed.

Most tests need none of this: if the data is seeded into the query cache up front, the first render
is already the loaded state.

## Mocking boundaries

Mock the **network boundary**, not the unit's own collaborators. In practice that means MSW for HTTP
and seeded cache state for data — not `vi.mock` on the hooks and stores the component uses.

```tsx
// bad: mocks the component's own data hook; the test now proves the mock returns what you typed
vi.mock("./use_engagements", () => ({
  useEngagements: () => ({ data: [{ id: 1, name: "Apollo" }], isLoading: false }),
}));

// good: the real hook runs against a stubbed network
server.use(
  http.get("/api/engagements", () => HttpResponse.json([{ id: 1, name: "Apollo" }]))
);
```

**The one exception:** `vi.mock` on a query hook is acceptable when seeding real data is
disproportionate — a deep response shape needed only to reach one branch, or a hook that fans out to
several endpoints you'd otherwise have to stub individually. Keep it to the hook you're standing in
for, and say why in a comment.

Never mock the unit under test, or any part of the logic the test exists to prove.

```ts
// bad: asserts the mock, not the function
vi.spyOn(pricing, "calculateDiscount").mockReturnValue(80);
expect(pricing.calculateDiscount(100, 0.2)).toBe(80);

// good
expect(calculateDiscount(100, 0.2)).toBe(80);
```

Mocking libraries you don't own (`react-i18next`, routers) is fine where the real thing can't run in
the test environment.

## React Query

Seed the cache rather than mocking the hook that reads it. The component runs its real query, so the
test covers the wiring too.

```tsx
// good: the component's own useQuery resolves straight from the cache
const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
queryClient.setQueryData(["engagements"], [{ id: 1, name: "Apollo" }]);

renderWithProviders(<EngagementList />, { queryClient });
```

If the repo's render helper already seeds a shared client, override only the keys your test needs —
check `AGENTS.md` for how it accepts a custom client.

Loading and error states are the cases where the network boundary earns its keep: stub a pending or
failing response with MSW instead of forcing `isLoading` through a mocked hook.

## Zustand

Set real state on the real store. Mocking the store module replaces the thing you're testing against
with a literal.

```tsx
// bad
vi.mock("./filters_store");

// good
useFiltersStore.setState({ query: "apollo" });
render(<FilterSummary />);
expect(screen.getByText("apollo")).toBeInTheDocument();
```

Check whether the repo resets stores between tests automatically; if it doesn't, reset the state you
set in `afterEach`.

## Fake timers

Only for code whose behaviour *is* time: debounce, throttle, polling, intervals. Everything else
should wait on the DOM, not the clock.

```ts
// good
beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

it("emits once after the debounce window", () => {
  const onChange = vi.fn();
  const { result } = renderHook(() => useDebounced(onChange, 300));

  act(() => {
    result.current("a");
    result.current("ab");
    vi.advanceTimersByTime(300);
  });

  expect(onChange).toHaveBeenCalledExactlyOnceWith("ab");
});
```

With fake timers installed, pass `userEvent.setup({ advanceTimers: vi.advanceTimersByTime })` or
interaction will hang.

## Mock cleanup

Clear mocks between tests so call history can't leak across them.

```ts
afterEach(() => {
  vi.clearAllMocks();
});
```

Use `vi.restoreAllMocks()` instead when you've used `vi.spyOn` and need the original implementations
back.

## it.each over near-duplicate tests

If a test is a copy of its neighbour with one value changed, it's one test with a table — unless the
changed value genuinely exercises a different path.

```ts
// bad
it("shows an error when name is empty", () => {});
it("shows an error when email is empty", () => {});
it("shows an error when phone is empty", () => {});

// good
it.each(["name", "email", "phone"])("shows a required error when %s is empty", async (field) => {
  const user = userEvent.setup();
  render(<ContactForm />);

  await user.click(screen.getByRole("button", { name: "Save" }));

  expect(screen.getByText(`${field} is required`)).toBeInTheDocument();
});
```

## Patterns you'll see that are not the rule

Existing specs predate this guide. These are common in them and must not be copied into new tests:

| Pattern you'll find | Rule that supersedes it |
|---|---|
| `vi.mock` on the component's own query hooks or stores, as the default way to supply data | [Mocking boundaries](#mocking-boundaries) — stub the network or seed the cache |
| `userEvent.click(...)` on the default export, with no `setup()` | [Interaction](#interaction) — `const user = userEvent.setup()` |
| A hand-rolled `QueryClientProvider` / router wrapper per test | [Rendering](#rendering) — use the repo's render helper |
| `fireEvent` for ordinary clicks and typing | [Interaction](#interaction) — `fireEvent` only for events `userEvent` can't express |

Leave them alone unless you're already changing that spec for another reason.

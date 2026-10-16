# RSpec Guide

Ruby test conventions, based on [Better Specs](https://www.betterspecs.org/) plus ProFinda additions.
The general rules in [SKILL.md](SKILL.md) win on conflict — especially "minimal tests" and "ask first".

## Contents

- [Describe methods](#describe-methods)
- [Contexts](#contexts)
- [Short descriptions](#short-descriptions)
- [Single expectation](#single-expectation)
- [Cases to cover](#cases-to-cover)
- [expect syntax, no should](#expect-syntax-no-should)
- [subject](#subject)
- [let and let!](#let-and-let)
- [let instead of def](#let-instead-of-def) (ProFinda)
- [Mocking](#mocking)
- [Create only the data you need](#create-only-the-data-you-need)
- [Factories, not fixtures](#factories-not-fixtures)
- [Readable matchers](#readable-matchers)
- [Shared examples](#shared-examples)
- [Test what you see](#test-what-you-see)
- [Stubbing HTTP](#stubbing-http)
- [Global state and time](#global-state-and-time) (ProFinda)
- [SQL query counts: rspec-sqlimit](#sql-query-counts-rspec-sqlimit) (ProFinda)
- [Sidekiq jobs: rspec-sidekiq](#sidekiq-jobs-rspec-sidekiq) (ProFinda)
- [Hygiene](#hygiene)
- [Tooling](#tooling)

## Describe methods

Use `.method` for class methods, `#method` for instance methods.

```ruby
# bad
describe 'the authenticate method for User' do
describe 'if the user is an admin' do

# good
describe '.authenticate' do
describe '#admin?' do
```

## Contexts

Group conditions in `context`; start descriptions with `when`, `with`, or `without`.

```ruby
# bad
it 'has 200 status code if logged in' do
  expect(response).to have_http_status(:ok)
end
it 'has 401 status code if not logged in' do
  expect(response).to have_http_status(:unauthorized)
end

# good
context 'when logged in' do
  it { is_expected.to have_http_status(:ok) }
end

context 'when logged out' do
  it { is_expected.to have_http_status(:unauthorized) }
end
```

Nest at most 3 levels of `describe` / `context` below the top-level `describe`. Deeper → flatten
conditions into one context (`'when admin and archived'`) or split the file.

```ruby
# bad: 5 levels
describe Project do
  describe '#archive!' do
    context 'when admin' do
      context 'with owner' do
        context 'when completed' do
          context 'with tasks' do

# good
describe Project do
  describe '#archive!' do
    context 'when admin owns a completed project' do
      context 'with tasks' do
```

## Short descriptions

Keep `it` descriptions under ~40 characters. Longer → move the condition into a `context`.

```ruby
# bad
it 'has 422 status code if an unexpected params will be added' do

# good
context 'when not valid' do
  it { is_expected.to have_http_status(:unprocessable_entity) }
end
```

## Single expectation

Isolated unit specs: one behaviour per example.

```ruby
# good (isolated)
it { is_expected.to have_attributes(status: 'active') }
it { is_expected.to be_persisted }
```

Slow, non-isolated specs (DB-heavy, request, end-to-end): several expectations in one example are fine
to avoid repeating expensive setup. Prefer `:aggregate_failures` so all failures are reported.

```ruby
# good (not isolated)
it 'creates the resource', :aggregate_failures do
  expect(response).to have_http_status(:created)
  expect(response.parsed_body['name']).to eq('Alpha')
end
```

## Cases to cover

Cover valid, edge, and invalid cases **that the change introduces** — not every theoretical input. Extra
edge cases on unchanged code need user approval (see SKILL.md "Ask first").

```ruby
# bad: only the happy path of a new destroy action
it 'deletes the resource'

# good
describe 'DELETE /resources/:id' do
  context 'when resource is owned' do
    it { is_expected.to have_http_status(:no_content) }
  end

  context 'when resource is not found' do
    it { is_expected.to have_http_status(:not_found) }
  end

  context 'when resource is not owned' do
    it { is_expected.to have_http_status(:not_found) }
  end
end
```

## expect syntax, no should

Always `expect(...)`; one-liners use `is_expected.to`. Never `should` — neither as syntax nor in
descriptions. Descriptions use third person present tense.

```ruby
# bad
it 'should not change timings' do
  consumption.occur_at.should == valid.occur_at
end
it { should have_http_status(:unprocessable_entity) }

# good
it 'does not change timings' do
  expect(consumption.occur_at).to eq(valid.occur_at)
end
it { is_expected.to have_http_status(:unprocessable_entity) }
```

## subject

DRY repeated targets with `subject`; name it when referenced explicitly.

```ruby
# bad
it { expect(Hero.first.equipment).to include('sword') }

# good
subject(:hero) { Hero.first }

it 'carries a sword' do
  expect(hero.equipment).to include('sword')
end
```

## let and let!

Use `let` instead of instance variables in `before`. `let` is lazy and memoised per example.

```ruby
# bad
before { @resource = create(:device) }
before { @type = Type.find(@resource.type_id) }

it 'sets the type_id field' do
  expect(@resource.type_id).to eq(@type.id)
end

# good
let(:resource) { create(:device) }
let(:type) { Type.find(resource.type_id) }

it 'sets the type_id field' do
  expect(resource.type_id).to eq(type.id)
end
```

Use `let!` only when the record must exist before the action runs (e.g. testing queries/scopes).
Don't use `let!` just to "be safe" — it creates data in every example. A `let!` no example needs is
banned; a `let!` only needed by one context belongs in that context.

```ruby
# bad: eager records nobody needs before the action
let!(:project) { create(:project) }
let!(:owner) { create(:user) }

it 'assigns the owner' do
  project.assign(owner)
  expect(project.owner).to eq(owner)
end

# good: lazy
let(:project) { create(:project) }
let(:owner) { create(:user) }

# good: let! because the scope must see both records
let!(:active) { create(:user, :active) }
let!(:inactive) { create(:user, :inactive) }

it { expect(User.active).to contain_exactly(active) }
```

## let instead of def

ProFinda rule: **never use `def` to create objects** (records, doubles, params, inputs) in a spec. Use
`let` / `let!` / `subject`. `let` is memoised per example, lazy, and overridable per `context`; a `def`
builds a new object on every call and can't be overridden cleanly. This replaces Better Specs' `def update`
pattern.

```ruby
# bad: def builds objects
def project
  create(:project, owner: user)
end

def create_project(status:)
  create(:project, owner: user, status:)
end

it 'archives the project' do
  project.archive!
  expect(project.reload).to be_archived  # `project` called twice → two different records
end

context 'when completed' do
  it 'cannot be archived' do
    expect { create_project(status: 'completed').archive! }.to raise_error(Project::InvalidState)
  end
end

# good: let builds objects, context overrides the input
let(:status) { 'active' }
let(:project) { create(:project, owner: user, status:) }

it 'archives the project' do
  project.archive!
  expect(project.reload).to be_archived
end

context 'when completed' do
  let(:status) { 'completed' }

  it 'cannot be archived' do
    expect { project.archive! }.to raise_error(Project::InvalidState)
  end
end
```

Same for actions and inputs — use `subject` / `let`, not `def`:

```ruby
# bad
def update
  resource.properties = properties
end

def build_params(value)
  { id: resource.id, value: value }
end

it 'raises not found' do
  expect { update }.to raise_error(ActiveRecord::RecordNotFound)
end

# good
subject(:update) { resource.properties = properties }

let(:value) { 'on' }
let(:properties) { { id: resource.id, value: } }

it 'raises not found' do
  expect { update }.to raise_error(ActiveRecord::RecordNotFound)
end

context 'with value off' do
  let(:value) { 'off' }
  # ...
end
```

Logic reused across many spec files belongs in `spec/support` (helpers, matchers, shared contexts) —
not in per-file `def`s.

## Mocking

Don't (over)use mocks. Test real behaviour; stub only system boundaries — external HTTP, third-party
SDKs, time, randomness. Never mock the class under test or its internal collaborators.

```ruby
# bad: mocks internals, asserts on calls
it 'notifies' do
  expect(Notifier).to receive(:call).once
  CompleteProject.call(project)
end

# good: assert on observable outcome
it 'marks the project completed' do
  expect { CompleteProject.call(project) }.to change { project.reload.status }.from('active').to('completed')
end

# good: boundary stubbed
before { stub_request(:post, 'https://hooks.example.com/notify').to_return(status: 200) }
```

For time use `travel_to` / `freeze_time`, never stub `Time` (see "Global state and time").

## Create only the data you need

Create the minimum records the behaviour needs. Needing dozens of records usually means the test is
wrong. Prefer `build` / `build_stubbed` over `create` when persistence isn't part of the behaviour.

```ruby
# bad
before { create_list(:user, 50) }

# good
describe '.top' do
  let!(:best) { create(:user, score: 3) }
  let!(:second) { create(:user, score: 2) }

  before { create(:user, score: 1) }

  it { expect(User.top(2)).to eq([best, second]) }
end
```

## Factories, not fixtures

Use FactoryBot, never fixtures or hand-built records. See [factory-bot.md](factory-bot.md).

## Readable matchers

Use built-in [RSpec matchers](https://rspec.info/features/3-12/rspec-expectations/built-in-matchers/)
over manual comparisons.

```ruby
# bad
lambda { model.save! }.to raise_error(ActiveRecord::RecordInvalid)
expect(list.include?(item)).to be(true)
expect(user.errors[:email].any?).to eq(true)

# good
expect { model.save! }.to raise_error(ActiveRecord::RecordInvalid)
expect(list).to include(item)
expect(user.errors[:email]).to be_present
```

### change: always qualified

Always chain `.by(n)` or `.from(a).to(b)`. Use `change(Model, :count)` for counts. Combine with
`.and` / `not_change` (`RSpec::Matchers.define_negated_matcher :not_change, :change`).

```ruby
# bad: passes on any change
expect { subject }.to change { project.reload.status }
expect { subject }.to change { Project.count }

# good
expect { subject }.to change { project.reload.status }.from('active').to('archived')
expect { subject }.to change(Project, :count).by(1).and not_change(Task, :count)
```

Alternative where the repo has record matchers: `create_record` / `update_record(...).from().to()` (see
"Created and updated records").

### Collections: contents, not size

Use `contain_exactly` (order-independent) or `eq([...])` (order is the behaviour). Not `match_array`,
not size checks.

```ruby
# bad
expect(result.size).to eq(2)
expect(result).to match_array([a, b])

# good
expect(result).to contain_exactly(a, b)
```

### Errors: specific class

Always `raise_error(SpecificClass)`. A bare `raise_error` passes on typos (`NoMethodError`).
`expect { }.not_to raise_error` alone proves nothing — assert the outcome.

```ruby
# bad
expect { subject }.to raise_error
it { expect { subject }.not_to raise_error }

# good
expect { subject }.to raise_error(Project::InvalidState)
it { expect { subject }.to change(Project, :count).by(1) }
```

### Created and updated records

No `Model.last` / `Model.first` — order isn't guaranteed. Use the return value, the response id, or
`find_by`.

```ruby
# bad
subject
expect(Project.last.name).to eq('Alpha')

# good
expect(subject.output.name).to eq('Alpha')
expect(Project.find_by(name: 'Alpha')).to be_present
```

**Alternative** — only if the repo provides record matchers (e.g. api's `CommonEngine` `create_record` /
`update_record`). One block expectation covers the action, the record, and its attributes, and fails on
ambiguity. Without them, use the `find_by` / return-value form above.

```ruby
# good: created record with properties (fails if 2+ records match)
expect { subject }.to create_record(Project).with_properties(name: 'Alpha', account_id: account.id)

# good: nothing created; chain with another expectation
expect { subject }.to not_create_record(Project).and create_record(AuditLog)

# good: updated record, always with from + to
expect { subject }.to update_record(project).from(status: 'active').to(status: 'archived')

# bad: imprecise
expect { subject }.to create_record(Project)
expect { subject }.to update_record(project)
```

### Translations: I18n.t!

Use `I18n.t!` (raises on a missing key) for translated messages. Never `I18n.t` or literal strings.

```ruby
# bad
expect(subject.errors[:name]).to include("can't be blank")
expect(subject.errors[:name]).to include(I18n.t('errors.blank'))

# good
expect(subject.errors[:name]).to include(I18n.t!('errors.blank'))
```

## Shared examples

Use shared examples to remove real duplication of the same behaviour across specs (mostly
request/controller-level). Reuse existing ones first; adding a new shared example needs user approval.

```ruby
# bad: same listing/pagination assertions copy-pasted into every index spec

# good
describe 'GET /devices' do
  let!(:resource) { create(:device, created_from: user.id) }

  it_behaves_like 'a listable resource'
  it_behaves_like 'a paginable resource'
end
```

Don't use shared examples to hide one-off setup — that hurts readability.

## Test what you see

Test models/services deeply and app behaviour through request (or system) specs. Avoid controller
specs and `assigns` — they test implementation. Don't repeat model-level cases at request level; the
request spec checks the API contract (status, response shape, key side effect).

## Stubbing HTTP

Never hit real external services. Stub with WebMock (or VCR where the repo uses it).

```ruby
context 'with unauthorized access' do
  let(:uri) { 'https://api.example.com/types' }

  before { stub_request(:get, uri).to_return(status: 401, body: '{}') }

  it 'raises an auth error' do
    expect { client.types }.to raise_error(Client::Unauthorized)
  end
end
```

## Global state and time

Every example starts from and leaves a clean state.

- **No `before(:all)` / `before(:context)`.** Data and stubs leak between examples. Use `let` / `before`.
- **ENV**: only through a block helper that restores it (e.g. the repo's `with_environment`). Never
  `ENV['X'] =` or `allow(ENV).to receive`.
- **Limits / pagination**: `stub_const` the limit instead of creating many records.
- **Time**: freeze it whenever data depends on day, week, or month boundaries. Use the block form or
  `around`, so time is always restored.
- **No `sleep`**: use time helpers.
- **`let` names never shadow helpers**: no `let(:freeze_time)`, `let(:subject)`, `let(:response)`,
  `let(:params)` in request specs.
- **Notifications**: only `ActiveSupport::Notifications.subscribed(callback, name) { }`, never `subscribe`
  without unsubscribing. Never for SQL — use `exceed_query_limit`.

```ruby
# bad
before(:all) { @account = create(:account) }
before { ENV['FEATURE_X'] = 'on' }
before { create_list(:project, 51) }               # to cross PAGE_SIZE = 50
let(:freeze_time) { Time.zone.local(2026, 1, 5) }  # shadows the helper
it 'expires' do
  travel_to(Time.zone.local(2026, 1, 5))           # never restored outside Rails-typed groups
  sleep 1
end
ActiveSupport::Notifications.subscribe('sql.active_record') { count += 1 }

# good
let(:account) { create(:account) }
around { |example| with_environment('FEATURE_X' => 'on') { example.run } }
before { stub_const('ProjectsQuery::PAGE_SIZE', 1) }
let(:monday) { Time.zone.local(2026, 1, 5) }
around { |example| travel_to(monday) { example.run } }
it 'expires' do
  travel 1.second
end
ActiveSupport::Notifications.subscribed(callback, 'project.archived') { subject }
expect { subject }.not_to exceed_query_limit(1).with(/FROM "projects"/)
```

## SQL query counts: rspec-sqlimit

ProFinda rule: use `rspec-sqlimit`'s `exceed_query_limit` for N+1 and query-count specs. Never count
queries with `ActiveSupport::Notifications` / `sql.active_record`. See [rspec-sqlimit.md](rspec-sqlimit.md).

## Sidekiq jobs: rspec-sidekiq

ProFinda rule: enqueue with `perform_later` (never `perform_async` / `perform_in`); assert with
`rspec-sidekiq` matchers (prefer block form `enqueue_sidekiq_job`), never the `Job.jobs` array. Don't test
`sidekiq_options`. See [rspec-sidekiq.md](rspec-sidekiq.md).

## Hygiene

- No `xit` / `xdescribe` / `xcontext`. Delete the test, or `skip 'reason [SP-XXXX]'` with a ticket.
- No `fit` / `fdescribe` / `:focus` left in committed specs.

```ruby
# bad
xit 'archives the project' do

# good
it 'archives the project' do
  skip 'flaky until HAL stub fixed [SP-1234]'
```

## Tooling

Follow the repo's existing setup (`.rspec`, `spec_helper.rb`, formatters, preloaders). Useful defaults:
`config.expect_with(:rspec) { |c| c.syntax = :expect }` to forbid `should`; run only touched spec files
while iterating (`bundle exec rspec path/to/file_spec.rb:LINE`), full suite before pushing.

# Opera Operations — Reference

> Domain methods are the public API that triggers these operations — see `profinda-domain-interface`.

## Output Pattern

Avoid manipulating `result.output` at the call site. Instead, keep logic inside the operation: use `context` attributes to pass data between steps, and a dedicated `step :output` at the end to set `result.output`.

**Prefer:**
```ruby
# Inside the operation — steps share state via context
context do
  attr_accessor :record
end

step :persist   # sets self.record = Record.create!(...)
step :output    # result.output = record

# Call site stays simple
result = MyModule::Operations::Create.call(params:, dependencies:)
result.output   # => the record
```

**Avoid:**
```ruby
result = MyModule::Operations::Create.call(params:, dependencies:)
record = result.output
record.update!(name: 'patched')  # logic leaking to call site
```

Exceptions exist (e.g. extracting `.output` to pass into a subsequent operation call) but the step-based pattern fits the vast majority of the codebase.

## Avoid Logic in Private Methods

Private methods should be thin helpers only. Business logic belongs in named DSL steps — they appear in `result.executions`, are self-documenting, and halt the pipeline correctly.

**Prefer:**
```ruby
step :validate_quota
step :build_record
step :persist

def validate_quota
  return if account.under_quota?
  result.add_error(:base, I18n.t!('errors.quota_exceeded'))
end

def build_record
  self.record = Record.new(schema_output.slice(:name))
end

def persist
  record.save!
end
```

**Avoid:**
```ruby
step :process

def process
  validate_quota
  build_record
  persist_record
end

private

def validate_quota
  ...
end

def build_record
  ...
end

def persist_record
  ...
end
```

The private version hides steps from `result.executions`, makes error halting harder to reason about, and defeats the purpose of the DSL.

## Operation Structure

```ruby
# frozen_string_literal: true

module ModuleName
  module Operations
    class Create < Opera::Operation::Base
      context do
        attr_accessor :record
        attr_reader :schema_output        # auto-set by validate :schema
        attr_reader :find_template_output # auto-set by operation :find_template
      end

      dependencies do
        attr_reader :account, :requester
        attr_reader :serializer, default: -> { DefaultSerializer }
      end

      params do
        attr_reader :name, :description
      end

      validate :schema
      operation :find_template
      finish_if :already_processed?
      step :authorize
      step :prepare_params
      within :read_from_replica do
        step :load_extra_data
      end
      transaction do
        step :persist
        operation :create_associations
      end
      operation :write_history
      step :broadcast
      success :notify_optional     # non-halting: pipeline continues even if errors added
      benchmark do
        step :compute_summary
      end
      step :output
      always :log_result           # always runs, even on failure or finish!

      def schema
        Schemas::Create.new.call(params)
      end

      def find_template
        SomeDomain::Templates.find(id: schema_output[:template_id])
      end

      def already_processed?
        Record.exists?(external_id: schema_output[:external_id])
      end

      def authorize
        return if Policy.new(requester.user, record).create?
        result.add_error(:base, I18n.t!('errors.not_authorized'))
      end

      def prepare_params
        self.record = Record.new(schema_output.slice(:name, :description))
      end

      def read_from_replica(&block)
        ActiveRecord::Base.connected_to(role: :reading, &block)
      end

      def load_extra_data
        # runs on replica DB
      end

      def persist
        record.save!
      end

      def create_associations
        AssociationDomain.create(record_id: record.id)
      end

      def write_history
        History::Domain.write(event: :created, resource_type: 'Record', resource_id: record.id)
      end

      def broadcast
        CommonEngine::Broadcaster.broadcast(:record_created, record.id, after_commit: true)
      end

      def notify_optional
        # errors here do not halt the pipeline
        ExternalService.notify(record.id)
      end

      def compute_summary
        # timing stored in result.information[:expensive_work]
      end

      def output
        result.output = serializer.new(record).output
      end

      def log_result
        Rails.logger.info("Create result: #{result.success?}")
      end
    end
  end
end
```

## Calling Operations

```ruby
result = MyModule::Operations::Create.call(
  params: { name: 'foo', description: 'bar' },
  dependencies: { account: account, requester: current_profile }
)

result.success?    # => true/false
result.failure?    # => true/false
result.output      # => return value (nil if not set)
result.output!     # => return value OR raises Opera::Operation::Result::OutputError
result.errors      # => { field: ["message"] }
result.failures    # => alias for errors
```

**Prefer `output!` over `output` whenever possible.** Use `output!` when a failure is not an expected outcome (e.g. internal lookups, chaining one operation's result into another). It fails loudly with `Opera::Operation::Result::OutputError` and the underlying errors, instead of silently returning `nil` and causing a cryptic `NoMethodError` downstream. Only use plain `output` when you explicitly handle the failure/`nil` case (typically after checking `result.success?`).

```ruby
# Good — failure is unexpected; fail loudly:
ids = Attributes::Domain::CustomTypes.find_all(params:, account_id:, serializer: nil).output!.map(&:id)

# Good — failure explicitly handled:
result = MyOperation.call(...)
return handle_errors(result.errors) unless result.success?
record = result.output

# Inside an operation:
result.output = value           # set output
result.add_error(:field, msg)   # add single error (halts pipeline after current step)
result.add_errors(hash)         # add multiple errors from hash or Dry errors; format: { field: ["message"] }
result.add_information(hash)    # add metadata (benchmarks, debug info)
result.executions               # array of executed step names (debugging)
```

## Context Auto-Population

`validate`, `operation`, and `operations` automatically store outputs in context:

```ruby
validate :schema          # => schema_output          (validated params hash)
operation :find_record    # => find_record_output      (nested result's output)
operations :create_batch  # => create_batch_output     ([result1.output, ...])
```

Declare readers in the `context` block to access them:

```ruby
context do
  attr_reader :schema_output, :find_record_output, :create_batch_output
end
```

## The `default:` Option

Attributes in `context do`, `dependencies do`, and `params do` blocks accept a `default:` lambda running in the operation instance's scope:

```ruby
context do
  attr_accessor :fields, default: -> { [] }
  attr_reader :template_key, default: -> { schema_output[:template_key] }
  attr_reader :account, default: -> { activity.account }
end

dependencies do
  attr_reader :serializer, default: -> { DefaultSerializer }
  attr_reader :page, default: -> { 1 }
end

params do
  attr_reader :status, default: -> { meta[:status] }
end
```

### When to use `default:` vs step vs private method

| Scenario | Use |
|---|---|
| Optional dependency with sensible fallback | `default:` in `dependencies do` |
| Empty collection to accumulate into | `default:` on `attr_accessor` in `context do` |
| Simple derivation from another attribute (no error handling) | `default:` on `attr_reader` in `context do` |
| Computation that needs `result.add_error` on failure | `step :method` in pipeline |
| Setting multiple context values at once | `step :method` in pipeline |
| Complex multi-line logic or branching | `private` method |
| Helper used only inside other methods | `private` method |

## Early Exit Patterns

```ruby
# Class-level: finish_if (no error, just stops pipeline)
finish_if :already_exists?

def already_exists?
  Record.exists?(key: params[:key])
end

# Inside a step: finish! (MUST be followed by return — it only sets a flag)
def persist
  self.record = Record.find_by(key: params[:key])
  if record
    result.output = record  # set output BEFORE finish!
    finish!
    return                  # required — code below still runs without this
  end
  # ... continue with creation
end
```

## Schema Validation Pattern

```ruby
# schemas/create.rb
class Schemas::Create < CommonEngine::Schema
  option :account_id  # constructor injection for runtime context

  params do
    required(:name).filled(:string)
    optional(:description).maybe(:string)
    required(:template_id).filled(:integer)
  end

  rule(:name).validate(max_size?: 255)
  rule(:template_id).validate(:id?)
end

# In operation:
def schema
  Schemas::Create.new(account_id: account.id).call(params)
end
```

## Nested Operations

**Single** (`operation`): returns one `Opera::Operation::Result`. Output stored in `context[:method_output]`. On failure, errors merge into parent and pipeline halts.

```ruby
operation :find_template

def find_template
  DemandEngine::Domain::Templates.find(id: schema_output[:template_id])
end
```

**Batch** (`operations`): returns `Array<Opera::Operation::Result>`. If ANY fails, all failures merge into parent.

```ruby
operations :create_bookings
def create_bookings
  profile_ids.map { |pid| BookingEngine::Domain::Bookings.import(profile_id: pid, bookings:) }
end
```

**Skip a nested operation** — return a no-op result:

```ruby
def find_booking_category
  return Opera::Operation::Result.new if booking_category_id.blank?
  BookingEngine::Domain::BookingCategories.find(params: { id: booking_category_id })
end
```

## `within`

Wraps nested steps in a custom method that must `yield`. The wrapper runs before the nested steps; break conditions still apply inside.

**Primary use in this codebase:** route read-heavy operations to the replica DB while keeping write steps on the primary.

```ruby
within :read_from_replica do
  operation :fetch_data
  operation :fetch_more_data  # context auto-populated between them
end
step :write_results           # back on primary

# Wrapper method must yield.
# CommonEngine::Operation already defines read_from_replica — inherit from it:
private
def read_from_replica(&block)
  ActiveRecord::Base.connected_to(role: :reading, &block)
end
```

Inherit from `CommonEngine::Operation` instead of `Opera::Operation::Base` to get `read_from_replica` for free.
## Common Patterns

```ruby
# Error handling
result.add_error(:field, I18n.t!('errors.not_found'))   # halts pipeline
result.add_errors(record.errors.messages)               # from AR model
# Note: `return false` does NOT halt — only result.add_error or finish! halts

# History tracking (post-transaction)
History::Domain.write(event: :created, category: :records,
  resource_type: 'Record', resource_id: record.id, account_id: account.id)

# Broadcasting (post-transaction)
CommonEngine::Broadcaster.broadcast(:record_created, record.id, priority: :high, after_commit: true)

# Custom transaction class
class MyOp < Opera::Operation::Base
  configure do |config|
    config.transaction_class = ActiveRecord::Base
  end
end
```

## Testing Operations

```ruby
RSpec.describe MyModule::Operations::Create do
  subject(:result) { described_class.call(params:, dependencies:) }

  let(:account) { create(:account) }
  let(:requester) { create(:profile, account:) }
  let(:params) { { name: 'foo' } }
  let(:dependencies) { { account:, requester: } }

  context 'when params are valid' do
    it 'succeeds' do
      expect(result).to be_success
    end

    it 'returns the created record' do
      expect(result.output).to be_a(Record)
      expect(result.output.name).to eq('foo')
    end
  end

  context 'when not authorized' do
    before { allow_any_instance_of(Policy).to receive(:create?).and_return(false) }

    it 'fails with an error' do
      expect(result).to be_failure
      expect(result.errors[:base]).to include(I18n.t!('errors.not_authorized'))
    end
  end

  context 'when params are invalid' do
    let(:params) { { name: '' } }

    it 'fails with validation errors' do
      expect(result).to be_failure
      expect(result.errors).to have_key(:name)
    end
  end
end
```

Key assertions:
- `result.success?` / `result.failure?` — overall pass/fail
- `result.output` — the return value set by `step :output`
- `result.errors` — `{ field: ["message"] }` hash
- `result.executions` — array of step names run (useful for debugging which steps fired)

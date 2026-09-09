---
name: profinda-opera
description: ProFinda step-based operation DSL built on Opera::Operation::Base. Covers writing, reading, debugging, or modifying operations, schemas, and step pipelines. Use when user mentions `step`, `operation`, `finish!`, `result.add_error`, `Opera::Operation`, or any operation class in this Rails codebase.
---

# Opera Operations

## Quick Start

```ruby
# frozen_string_literal: true

module MyModule
  module Operations
    class Create < Opera::Operation::Base
      context do
        attr_accessor :record
      end

      dependencies do
        attr_reader :account, :requester
      end

      params do
        attr_reader :name
      end

      validate :schema
      step :authorize
      transaction do
        step :persist
      end
      step :output

      def schema
        Schemas::Create.new.call(params)
      end

      def authorize
        return if Policy.new(requester.user).create?

        result.add_error(:base, I18n.t!('errors.not_authorized'))
      end

      def persist
        self.record = Record.create!(schema_output.slice(:name))
      end

      def output
        result.output = record
      end
    end
  end
end

# Call it:
result = MyModule::Operations::Create.call(
  params: { name: 'foo' },
  dependencies: { account:, requester: current_profile }
)
result.success? # => true/false
result.output   # => the record
```

## Key Patterns

- **Output**: avoid manipulating `result.output` at the call site — use context attrs and `step :output` inside the operation instead. See [REFERENCE.md](REFERENCE.md).
- **Private methods**: keep them as thin helpers only — business logic belongs in named DSL steps so steps appear in `result.executions` and halt correctly. See [REFERENCE.md](REFERENCE.md).

## DSL Quick Reference

| DSL Method | Purpose | Halting behavior |
|---|---|---|
| `step :method` | Single step | Halts only if step adds errors or calls `finish!` |
| `validate :method` | Schema validation | Adds errors; halts after step (or after `validate do` block) |
| `transaction do ... end` | DB transaction | Halts + rolls back if any inner step fails |
| `operation :method` | Nested single op | Merges errors, halts on failure |
| `operations :method` | Nested batch ops | Merges all failures, halts if any fail |
| `within :method do ... end` | Custom yielding wrapper | Break conditions apply inside; cannot contain `always` |
| `finish_if :method` | Conditional early exit | Truthy = finish (no error) |
| `success :method` | Non-halting step | Like `step`, but continues despite errors |
| `always :method` | Unconditional step | Runs after all steps even on failure; top-level only |
| `benchmark :label do ... end` | Timed block | Stores timing in `result.information` |

## Standard Pipeline Ordering

```
validate :schema            # 1. Validate input
operation :find_*           # 2. Load required data
finish_if :guard?           # 3. Early exit guards
within :read_replica do
  step :authorize           # 4. Check permissions
end
step :prepare_*             # 5. Normalize/prepare data
transaction do              # 6. Transactional writes
  step :persist
  operation :nested_write
end
operation :write_history    # 7. History tracking (post-transaction)
step :broadcast             # 8. Event broadcasting (post-transaction)
step :audit                 # 9. Audit logging
step :output                # 10. Set result.output (always last)
always :log_info            # 11. Always executes no matter what
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Relying on `return false` to halt a step | Return value ignored; use `result.add_error(:base, msg)` |
| Forgetting `return` after `finish!` | `finish!` only sets a flag; code after it still runs |
| Forgetting `Opera::Operation::Result.new` for skipped nested ops | `operation :x` method MUST return a Result, even when skipping |
| Setting `result.output` after `finish!` | Set output THEN call `finish!` |
| Mutating `params` directly | `params` is frozen; use `schema_output` or `context` |
| Using `context_accessor` (legacy) | Use `context do; attr_accessor :name; end` block syntax |
| Accessing `dependencies[:key]` directly | Declare in `dependencies do; attr_reader :key; end` |
| Manually declaring `attr_reader :schema_output` in context | Unnecessary, auto-created readers for `validate`/`operation`/`operations` outputs |
| `within` wrapper method not yielding | Nested steps silently skipped; wrapper must always `yield` |
| Using `always` inside `within` or `transaction` | `always` is top-level only |
| Using `step` for writing history events | Use `operation` for writing history events |
| Using `.output` when failure is unexpected | Prefer `.output!` — it raises `OutputError` instead of returning `nil` (cryptic downstream errors). Use `.output` only when you handle the `nil`/failure case. See [REFERENCE.md](REFERENCE.md). |

## More Detail

See [REFERENCE.md](REFERENCE.md) for: full operation structure example, calling operations API, context auto-population, `default:` option, early exit patterns, schema validation, nested operations, `within`, testing operations, and common patterns.


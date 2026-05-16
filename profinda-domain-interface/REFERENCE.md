# Domain Interface — Reference

> Operations referenced here follow the Opera DSL — see `profinda-opera`.

## Architecture

```
Domain::Things.where(id: 1).find_all(extra: true)
       │              │           │
       │              │           └─ Result method → validates scope → calls Operations::FindAll
       │              └─ Builder method → returns Proxy, accumulates scope
       └─ Class extending CommonEngine::Domain::Interface
```

**Delegation chain:** `delegate_missing_to :proxy` — `where(...)` delegates to a fresh `Proxy`. Custom methods like `Domain::Things.archive(reason: 'x')` go: Domain module → `delegate_missing_to` → new `Proxy` → `method_missing` → `Operations::Archive`.

**Data flow:** `where(...)` builds scope on `model.all` → result method called → `validate_scope!` checks `Schemas::Scope` → operation resolved as `"#{model.name.pluralize}::Operations::#{method}".constantize` → called with `params: { scope:, arguments: }` → result returned.

### Method Types

| Type | Returns | Examples |
|---|---|---|
| **Builder (Proxy)** | `Proxy` (chainable) | `where`, `not`, `or`, `includes`, `order`, `merge` |
| **Result** | `Opera::Operation::Result` | `find`, `find_by`, `find_all`, `create`, `update_all`, `delete_all` |
| **Custom** | `Opera::Operation::Result` | Any method resolved via `method_missing` to `Operations::<MethodName>` |

**Source:** `engines/common_engine/lib/common_engine/domain/interface.rb`

## Creating a New Domain Class

### 1. Domain Module

```ruby
# engines/my_engine/lib/my_engine/domain/things.rb
module MyEngine
  module Domain
    module Things
      extend CommonEngine::Domain::Interface

      model_name -> { ::MyEngine::Thing }

      class << self
        def where(id: :optional, account_id: :required, status: :optional)
          super
        end

        def find_all(include_stats: :optional)
          super
        end

        def create(account_id:, name:, creator_id:)
          super
        end

        def update_all(name: :optional, status: :optional)
          super
        end

        def delete_all
          super
        end

        # Custom method → resolves to MyEngine::Things::Operations::Archive
        def archive(reason:)
          super
        end
      end
    end
  end
end
```

### 2. Scope Schema (required)

```ruby
# engines/my_engine/app/concepts/my_engine/things/schemas/scope.rb
module MyEngine
  module Things
    module Schemas
      class Scope < CommonEngine::Schema
        params do
          config.validate_keys = true

          optional(:id)
          optional(:account_id).filled
          optional(:status).maybe { str? | array? }
        end

        rule(:id).validate(:id_or_each_id?)
        rule(:account_id).validate(:id?)
      end
    end
  end
end
```

### 3. Operations

Operations receive `params[:scope]` (pre-filtered AR relation) and `params[:arguments]` (extra params). **Exception:** `create` only receives `params: { arguments: }` — no scope.

```ruby
# engines/my_engine/app/concepts/my_engine/things/operations/find_all.rb
module MyEngine
  module Things
    module Operations
      class FindAll < Opera::Operation::Base
        params do
          attr_reader :arguments
        end

        context do
          attr_reader :schema_output
          attr_accessor :scope, default: -> { params[:scope] }
        end

        validate :schema
        step :filter_by_stats
        step :output

        def schema
          Schemas::FindAll.new.call(arguments)
        end

        def filter_by_stats
          return unless schema_output[:include_stats]
          self.scope = scope.with_stats
        end

        def output
          result.output = scope
        end
      end
    end
  end
end
```

## Required Files for a New Domain

| File | Purpose |
|---|---|
| `engines/my_engine/lib/my_engine/domain/things.rb` | Domain class with method signatures |
| `engines/my_engine/app/concepts/my_engine/things/schemas/scope.rb` | Scope validation schema |
| `engines/my_engine/app/concepts/my_engine/things/schemas/find_all.rb` | FindAll argument validation |
| `engines/my_engine/app/concepts/my_engine/things/schemas/create.rb` | Create argument validation |
| `engines/my_engine/app/concepts/my_engine/things/operations/find_all.rb` | FindAll operation |
| `engines/my_engine/app/concepts/my_engine/things/operations/create.rb` | Create operation |
| `engines/my_engine/app/concepts/my_engine/things/operations/update_all.rb` | UpdateAll operation |
| `engines/my_engine/app/concepts/my_engine/things/operations/delete_all.rb` | DeleteAll operation |

## Immutability Rules

- `find_all` output: AR relation with restricted mutation methods — see `ResultWrapper::WHITELISTED_METHODS` for allowed list
- `create` output: record marked `readonly!`
- `unscope` is whitelisted but only `unscope(:order)` is allowed; other args raise `NotAllowedOperation`
- Restricted methods raise `NotAllowedOperation`

## Safety Constraints

- `update_all` raises `DangerousOperation` if called without prior `where()` scope
- `delete_all` raises `DangerousOperation` if called without scope AND without operation arguments
- `where` with unknown attributes raises `ArgumentError` (validated by `Schemas::Scope`)

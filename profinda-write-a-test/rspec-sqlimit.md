# rspec-sqlimit Guide

Use [`rspec-sqlimit`](https://github.com/nepalez/rspec-sqlimit)'s `exceed_query_limit` to guard against
N+1 queries and check query counts. Builds on [rspec.md](rspec.md).

Query-count specs are performance specs. Ask before adding one, unless the change is an N+1 fix.

## Never hand-roll query counters

Never count SQL with `ActiveSupport::Notifications` (`subscribe` or `subscribed`) or custom helpers.

```ruby
# bad
it 'avoids N+1' do
  count = 0
  callback = ->(*) { count += 1 }
  ActiveSupport::Notifications.subscribed(callback, 'sql.active_record') { ProjectsQuery.call }
  expect(count).to be <= 2
end

# good
it 'avoids N+1' do
  expect { ProjectsQuery.call.to_a }.not_to exceed_query_limit(2)
end
```

## Narrow with `.with(regex)`

Count only the queries the test is about. Transaction, schema, and unrelated queries make an unfiltered
limit flaky.

```ruby
# bad: counts BEGIN/COMMIT and every other query
expect { InvitesStats.call(profile) }.not_to exceed_query_limit(3)

# good
expect { InvitesStats.call(profile) }.not_to exceed_query_limit(1).with(/FROM "invites"/)
```

## N+1 checks need at least 2 parents

With one record, a per-row query and a preloaded query both run once, so the spec can't fail. Create at
least 2 parent records, each with its association.

```ruby
# bad: one message → N+1 invisible
let!(:message) { create(:message) }

# good
before { create_list(:message, 2) }

it 'avoids N+1 on authors' do
  expect { MessagesPage.new.to_h }.not_to exceed_query_limit(1).with(/FROM "users"/)
end
```

## Load lazy relations inside the block

A relation that is never loaded runs 0 queries → the spec passes falsely. Call `.to_a`, `.load`, or the
serializer/presenter inside the block.

```ruby
# bad: relation never loaded
expect { ProjectsQuery.call }.not_to exceed_query_limit(2)

# good
expect { ProjectsQuery.call.to_a }.not_to exceed_query_limit(2)
```

## Create data outside the block

Factory inserts inside the block count too. Set data up in `let!` / `before`.

```ruby
# bad
expect { create(:project); ProjectsQuery.call.to_a }.not_to exceed_query_limit(2)

# good
let!(:project) { create(:project) }

it { expect { ProjectsQuery.call.to_a }.not_to exceed_query_limit(2) }
```

## Prove a query is skipped with a limit of 0

```ruby
it 'reuses the preloaded count' do
  expect { coverages }.not_to exceed_query_limit(0).with(/^SELECT COUNT\(\*\) FROM "profiles"/)
end
```

## Describe the outcome, not the number

```ruby
# bad
it 'runs 4 queries' do

# good
it 'avoids N+1 on authors' do
```

# FactoryBot Guide

Build test data with [FactoryBot](https://thoughtbot.github.io/factory_bot/). Builds on
[rspec.md](rspec.md). Pure domain logic should need no factories — test plain Ruby objects directly.

## Factories, not fixtures or manual records

```ruby
# bad
user = User.create(name: 'Genoveffa', surname: 'Piccolina', city: 'Billyville', active: true)

# good
user = create(:user)
```

## Cheapest strategy

`build_stubbed` > `build` > `create`. Use `create` only when the DB is part of the behaviour (queries,
scopes, uniqueness, callbacks on save).

```ruby
# bad: persisting to test a pure method
let(:user) { create(:user, first_name: 'Ann', last_name: 'Lee') }
it { expect(user.full_name).to eq('Ann Lee') }

# good
let(:user) { build_stubbed(:user, first_name: 'Ann', last_name: 'Lee') }
```

## Minimal base factory, variants in traits

The base factory sets only attributes required by validations without defaults. Variants are traits.

```ruby
# bad
factory :user do
  name { 'John' }
  admin { true }
  city { 'London' }
  avatar { ... }
end

# good
factory :user do
  name { 'John' }
  sequence(:email) { "person#{_1}@example.com" }

  trait :admin do
    admin { true }
  end
end
```

## Override only what the test is about

The reader should see why each attribute matters.

```ruby
# bad
let(:user) { create(:user, name: 'X', email: 'x@y.com', city: 'Z', active: false) }

# good
let(:user) { create(:user, :inactive) }
```

## Traits and let, not def helpers

```ruby
# bad
def admin_user
  create(:user, admin: true)
end

# good
let(:admin) { create(:user, :admin) }
```

## Sequences for unique fields

Never pass a literal that can clash with a generated sequence value.

```ruby
# bad: clashes with sequence's first value
create(:user, email: 'person1@example.com')
create(:user)

# good
factory :user do
  sequence(:email) { "person#{_1}@example.com" }
end
```

## Enum traits come free

FactoryBot defines a trait per enum value. Don't write them by hand.

```ruby
# bad
trait :queued do
  status { :queued }
end

# good
build(:task, :queued)
```

## Smallest list that proves it

2 for "many", N+1 for "top N". See [rspec.md](rspec.md) "Create only the data you need".

```ruby
# bad
before { create_list(:user, 50) }

# good
let!(:users) { create_list(:user, 2) }
it { expect(User.active).to contain_exactly(*users) }
```

## has_many: trait with a transient count

```ruby
# bad: loop in the spec
before { 3.times { create(:post, user:) } }

# good
factory :user do
  trait :with_posts do
    transient { posts_count { 2 } }

    after(:create) do |user, evaluator|
      create_list(:post, evaluator.posts_count, user:)
    end
  end
end

let(:user) { create(:user, :with_posts, posts_count: 2) }
```

## Don't create hidden associations

Every association in a factory is created on every `create`. Pass an existing parent instead of letting
each factory build its own.

```ruby
# bad: each post creates its own author, account, and project
let(:posts) { create_list(:post, 2) }

# good
let(:author) { create(:user) }
let(:posts) { create_list(:post, 2, author:) }
```

## Request params from attributes_for

```ruby
# bad
post '/projects', params: { project: { name: 'Alpha', status: 'active', budget: 100 } }

# good
post '/projects', params: { project: attributes_for(:project) }
```

## Linting

`FactoryBot.lint` belongs in a rake/CI task, not `before(:suite)`. Follow the repo's setup.

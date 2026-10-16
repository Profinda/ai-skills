# Good and Bad Tests

Examples in Ruby/RSpec; the rules apply to any language.

## Good: behaviour through the public interface

```ruby
# GOOD: observable behaviour
it 'confirms the order' do
  cart = create(:cart, :with_product)
  result = Checkout.call(cart:, payment_method:)
  expect(result.status).to eq('confirmed')
end
```

Characteristics:

- Tests behaviour callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad: implementation details

```ruby
# BAD: coupled to internal structure
it 'calls PaymentService#process' do
  expect(PaymentService).to receive(:process).with(cart.total)
  Checkout.call(cart:, payment_method:)
end
```

Red flags:

- Mocking internal collaborators
- Testing private methods (`send(:private_method)`) or reading ivars (`instance_variable_get`)
- Asserting on call counts/order
- Test breaks on a refactor that keeps behaviour
- Test name describes HOW, not WHAT
- Verifying through external means instead of the interface

```ruby
# BAD: bypasses interface to verify
it 'saves to database' do
  CreateUser.call(name: 'Alice')
  row = ActiveRecord::Base.connection.select_one("SELECT * FROM users WHERE name = 'Alice'")
  expect(row).to be_present
end

# GOOD: verifies through interface
it 'makes the user retrievable' do
  user = CreateUser.call(name: 'Alice')
  expect(User.find(user.id).name).to eq('Alice')
end
```

## Bad: tautological

```ruby
# BAD: expected value recomputed the way the code computes it
it 'sums line items' do
  items = [{ price: 10 }, { price: 5 }]
  expect(Total.call(items)).to eq(items.sum { _1[:price] })
end

# GOOD: independent literal
it 'sums line items' do
  expect(Total.call([{ price: 10 }, { price: 5 }])).to eq(15)
end
```

## Bad: redundant

```ruby
# BAD: same behaviour already covered by the model spec, re-tested at request level
# spec/models/project_spec.rb
it { is_expected.to validate_presence_of(:name) }
# spec/requests/projects_spec.rb
context 'without name' do
  it 'does not create the project' do ... end
  it 'returns name error' do ... end
  it 'returns blank name error' do ... end   # same case, different input
end

# GOOD: request spec only checks the API contract once
context 'without name' do
  it { is_expected.to have_http_status(:unprocessable_entity) }
end
```

```ruby
# BAD: tests trivial code / the framework
it 'has a name attribute' do
  expect(Project.new(name: 'X').name).to eq('X')
end
it 'delegates #owner_email to owner' do ... end
```

## Bad: testing removed code

```ruby
# Change: removed Project#archive! and its route.

# BAD: proves something no longer exists
it 'does not respond to #archive!' do
  expect(project).not_to respond_to(:archive!)
end
it 'has no archive route' do
  expect(post: '/projects/1/archive').not_to be_routable
end

# GOOD: delete the old #archive! specs. Add nothing.
```

## Bad: tests for a pure refactor

Extracting a private method, renaming a variable, or splitting a class without changing behaviour needs
**no new tests**. Existing behaviour specs must pass unchanged — if they break, they were testing
implementation.

# rspec-sidekiq Guide

Test Sidekiq jobs with [`rspec-sidekiq`](https://github.com/wspurgin/rspec-sidekiq) matchers. Builds on
[rspec.md](rspec.md). The gem uses `Sidekiq::Testing.fake!` by default: jobs go to an in-memory array,
cleared before each example.

## Enqueue with perform_later

ProFinda jobs override enqueuing: always `Job.perform_later(params, wait:, queue:, priority:)`. Never
`perform_async` / `perform_in` — in code or specs (custom cop `ForcePerformLater`).

`perform_later` pushes one hash argument with **string keys**, so matchers compare against
`'key' => value`.

```ruby
# bad
CopySkillsJob.perform_async(role.id)
ReminderJob.perform_in(1.day, invite.id)

# good
CopySkillsJob.perform_later(role_id: role.id)
ReminderJob.perform_later({ invite_id: invite.id }, wait: 1.day)
```

## Two specs, two jobs

- **Caller spec** (service, listener, request): checks the job was **enqueued** with the right arguments.
- **Job spec**: calls `perform` directly and checks the **outcome**.

Don't run the job inside the caller spec — that tests the job twice.

```ruby
# bad: caller spec runs the job and asserts its side effects
it 'copies skills' do
  Sidekiq::Testing.inline! { CloseRole.call(role) }
  expect(profile.reload.skills).to include(skill)
end

# good: caller spec
it 'enqueues the copy job' do
  expect { CloseRole.call(role) }.to enqueue_sidekiq_job(CopySkillsJob).with('role_id' => role.id)
end

# good: job spec
describe CopySkillsJob do
  subject(:perform) { described_class.new.perform('role_id' => role.id) }

  it 'copies role skills to the profile' do
    expect { perform }.to change { profile.reload.skills.count }.by(1)
  end
end
```

`Sidekiq::Testing.inline!` / `drain` only when the behaviour **is** the job chain, as one approved
end-to-end example — never by default.

## Use matchers, not the jobs array

```ruby
# bad
CloseRole.call(role)
expect(CopySkillsJob.jobs.size).to eq(1)
expect(CopySkillsJob.jobs.first['args']).to eq([{ 'role_id' => role.id }])

# good
expect { CloseRole.call(role) }.to enqueue_sidekiq_job(CopySkillsJob).with('role_id' => role.id)
```

## Prefer the block form

`enqueue_sidekiq_job` (block) ties the job to the action. `have_enqueued_sidekiq_job` (state) also matches
jobs enqueued during setup. Use the block form for new specs; the state form is fine where the action
can't be wrapped in a block.

```ruby
# avoid
CloseRole.call(role)
expect(CopySkillsJob).to have_enqueued_sidekiq_job('role_id' => role.id)

# preferred
expect { CloseRole.call(role) }.to enqueue_sidekiq_job(CopySkillsJob).with('role_id' => role.id)
```

## Not enqueued

```ruby
# bad
expect(CopySkillsJob.jobs.size).to eq(0)

# good
expect { CloseRole.call(role) }.not_to enqueue_sidekiq_job(CopySkillsJob)
```

## Scheduled jobs

`perform_later(..., wait:)` → assert with `.in(...)` inside `freeze_time`. Never compare
`jobs.first['at']` by hand.

```ruby
it 'schedules the reminder' do
  freeze_time do
    expect { Remind.call(invite) }.to enqueue_sidekiq_job(ReminderJob).in(1.day)
  end
end
```

## Loose arguments

Use argument matchers instead of digging into `args`.

```ruby
# bad
expect(SyncJob.jobs.first['args'][0]['project_id']).to eq(project.id)

# good
expect { action }.to enqueue_sidekiq_job(SyncJob).with(hash_including('project_id' => project.id))
```

## Don't stub perform_later

The fake queue is already safe. Stubbing it is mocking an internal call.

```ruby
# bad
expect(SyncJob).to receive(:perform_later).with(project_id: project.id)

# good
expect { action }.to enqueue_sidekiq_job(SyncJob).with('project_id' => project.id)
```

## Don't test job config

`sidekiq_options` (queue, retry, backtrace, uniqueness, expiry) is configuration. Don't test it. Queue
names also get a priority suffix from `perform_later`, so don't assert `.on(queue)`.

```ruby
# bad
it { is_expected.to be_processed_in :critical }
it { is_expected.to be_retryable 5 }
it { is_expected.to have_job_options(retry: 5, queue: 'critical') }
expect { action }.to enqueue_sidekiq_job(SyncJob).on('default')
```

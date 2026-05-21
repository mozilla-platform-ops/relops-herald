# RelOps Herald

**Status:** Early POC. Not yet wired to any reporter.

Herald is a GitHub repository and automation system that collects change events
from RelOps and adjacent repositories (ronin, worker-images, fxci-config, infra
code) and produces:

1. Entity-scoped Markdown changelogs (one file per role/profile/module).
2. A central activity log (`activity.md`) — every notable change in one stream.
3. Slack digest notifications (deferred; not in POC).

The goal is to reduce manual cross-repo correlation, improve rollout visibility
where "build" and "go-live" happen in different repos, and provide consistent,
reviewable change notes for day-to-day ops and incident response.

## POC scope

- One source repo: [`mozilla-platform-ops/ronin_puppet`](https://github.com/mozilla-platform-ops/ronin_puppet).
- One output: Markdown changelogs in this repo.
- No Slack notifications yet.
- AI-generated narrative summaries are produced *in the ronin reporter
  workflow* and shipped as part of the event payload (see schema).
- Staging/alpha entities (filename patterns `*_staging.*`, `*alpha*`) are
  excluded.

## Layout

```
schema/
  event.schema.json     # JSON Schema for the change event contract
examples/
  event-example-success.json     # happy-path event
  event-example-ai-failure.json  # AI failed; event still flows with error set
changelogs/
  <entity_type>/<entity_id>.md   # per-entity changelogs (written by Herald)
activity.md             # central activity log (written by Herald)
```

## How it (will) work

1. A merge to ronin's `master` triggers a reporter workflow.
2. The reporter diffs the commit, maps changed files to entities (role /
   profile / module / hiera data), excludes staging/alpha, and calls an AI
   agent to describe the change.
3. The reporter emits a JSON event matching `schema/event.schema.json` via
   GitHub `repository_dispatch` to this repo.
4. A workflow here validates the event, appends entries to the relevant
   per-entity changelog and to `activity.md`, and commits the result back.

If the AI call fails, the event still flows: `ai_summary.description` is
`null`, `ai_summary.error` describes why, and Herald renders a stub entry
rather than dropping the change.

## What's not built yet

- The ronin-side reporter workflow.
- The Herald-side ingester / renderer.
- The `repository_dispatch` plumbing.
- Slack output.
- Reporters for worker-images, fxci-config, infra code.

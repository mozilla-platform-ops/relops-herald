# Herald Worklog

A running log of work on RelOps Herald. Purpose: a durable resume point so
anyone (or Claude via `/resume`) can pick up context without re-deriving it.

**Update this file as work progresses.** Newest entries at the top of the log.
Keep the "Current state" and "Next steps" sections rewritten to reflect reality,
not appended to.

---

## Current state (as of 2026-07-13)

**Phase:** POC **wired end-to-end with the real AI summarizer, verified live.**
A role change in ronin_puppet is summarized by Claude (Sonnet 5) on the diff,
dispatched to relops-herald, and rendered into a committed changelog. Reporter
is still scoped to a build branch (`herald-reporter-dev`), not master.

**What exists:**
- `README.md` — project overview, POC scope, intended data flow.
- `schema/event.schema.json` — the change-event contract (JSON Schema draft 2020-12).
- `examples/event-example-*.json` — happy-path + AI-failure events.
- `herald/` — the ingester/renderer (`python -m herald --event <f> --root .`);
  validates the event, renders newest-first per-entity changelogs + `activity.md`,
  idempotent per commit_sha.
- `tests/test_ingest.py` — 10 stdlib-unittest tests (schema contract + rendering).
- `.github/workflows/ingest.yml` — repository_dispatch receiver (render + commit).
- `reporter-templates/ronin_puppet/` — copy-into-ronin reporter: workflow +
  `map_entities.py` / `summarize.py` (placeholder AI) / `build_event.py`.
- `docs/github-app-setup.md` — GitHub App config, updated to what shipped.

**Infra that's live:**
- GitHub App **`relops-herald-dispatch`** created, security-reviewed (Clovis
  Foji), transferred to `mozilla-platform-ops` (ctb). Scoped to **Contents RW
  only — no webhook, no event subscriptions** (narrower than the original plan).
  Tracked in [bug 2041840](https://bugzilla.mozilla.org/show_bug.cgi?id=2041840).
- Installed on **`relops-herald`** (the dispatch target — required) and
  `ronin_puppet`. App ID / Client ID / private-key location still need to be
  recorded in the setup doc.

**What the design says (encoded in the schema):**
- A reporter workflow in a source repo (first: `ronin_puppet`) emits a JSON
  event on merge to its default branch, via `repository_dispatch`.
- AI narrative summaries are generated **upstream in the reporter**, shipped in
  the event payload. On AI failure the event still flows: exactly one of
  `ai_summary.description` (success) or `ai_summary.error` (failure) is non-null,
  enforced by an `allOf`/`oneOf` invariant.
- Entities are derived deterministically from changed file paths; types:
  `role | profile | module | role-hiera | os-data | common-data`.
- Staging/alpha entities excluded by filename pattern (`*_staging.*`, `*alpha*`).
- Herald ingests the event, appends to per-entity changelogs + `activity.md`,
  commits the result back.

**What is NOT built yet:**
- End-to-end wiring: reporter template not yet installed in ronin_puppet; the
  two sides haven't run against each other live.
- Real AI summarizer in the reporter (`summarize.py` is a placeholder).
- Slack output.
- Reporters for worker-images, fxci-config, infra code.

## Known issues / decisions pending

- [x] ~~Schema "Crier" leftover~~ — fixed (now "Herald").
- [x] ~~`$id` unconfirmed~~ — confirmed; repo/app both live at
      `mozilla-platform-ops/relops-herald`.
- [x] ~~No validation harness~~ — `tests/test_ingest.py` (10 tests) covers the
      schema contract + rendering; run with `python -m unittest discover -s tests`.
- [ ] **Record App ID / Client ID / private-key location** in
      `docs/github-app-setup.md` (needed to set `HERALD_APP_ID` /
      `HERALD_APP_PRIVATE_KEY` secrets on ronin_puppet).
- [x] ~~Install the app on the target repo `relops-herald`~~ **DONE
      (2026-07-13).** The dispatch token needs Contents:write on the target;
      ronin_puppet install is not needed for the POC.
- [ ] Confirm ronin hiera layout so the `role-hiera`/`os-data`/`common-data`
      path patterns in `map_entities.py` are correct (currently best-effort).

## Next steps

1. ~~Create the GitHub App~~ **DONE** (bug 2041840).
2. ~~Reconcile docs; build Herald ingester + tests; fix Crier/`$id`~~ **DONE**.
3. ~~Draft the ronin reporter~~ **DONE** — template in
   `reporter-templates/ronin_puppet/` (workflow + map/summarize/build helpers).
4. ~~Wire it live — secrets, install reporter, one real end-to-end dispatch~~
   **DONE** — verified 2026-07-13 (see log). Reporter merged to ronin master
   (inert), building on `herald-reporter-dev`.
5. ~~Replace the placeholder `summarize.py` with the real AI call~~ **DONE
   (2026-07-13)** — Claude Sonnet 5 summarizes the diff via structured outputs;
   any failure → error-shaped `ai_summary` so the event still flows. Needs
   `ANTHROPIC_API_KEY` secret on ronin_puppet (added).
6. **NEXT:** Flip the reporter's push trigger `branches: [herald-reporter-dev]`
   → `[master]` (edit `.github/workflows/report.yml`) and merge PR #1280 to go
   fully live on real merges.
7. Housekeeping before real traffic: the live tests left test changelog entries
   (`changelogs/role/gecko_1_b_osx_1015.md` + activity rows) for comment-only
   ronin commits — remove if we want a clean slate. Tune the summarizer
   prompt/tags against real merges.
7. Later: Slack output; reporters for worker-images / fxci-config / infra.

---

## Log

### 2026-07-13 (later still) — real AI summarizer live
- Replaced the placeholder `summarize.py` with a real **Claude Sonnet 5** call:
  sends the commit subject + changed files + a size-bounded diff, uses
  structured outputs (`output_config.format`) to return `{description, headline,
  tags}`, thinking disabled. Any failure (missing key, network, refusal,
  bad output) → error-shaped `ai_summary` so the event still flows as a stub.
- Reporter workflow gains `pip install anthropic`, a diff-capture step, the
  `ANTHROPIC_API_KEY` secret (already added to ronin_puppet), and a `before`
  output from the meta step for the diff range. Model overridable via `MODEL`.
- Verified live on `herald-reporter-dev`: a comment-only role change produced an
  accurate Sonnet-5 summary (correctly flagged as a no-op, tags `test/herald/
  no-op`), dispatched, and rendered into the role changelog on relops-herald
  `main`. Error path also verified (SDK/key absent → valid stub event).

### 2026-07-13 (later) — end-to-end live
- **Pipeline verified live.** Reporter deployed to ronin_puppet via PR
  [#1280](https://github.com/mozilla-platform-ops/ronin_puppet/pull/1280),
  scoped to build branch `herald-reporter-dev` (+ workflow_dispatch) so it does
  not fire on master merges yet. Herald ingester + receiver merged to
  relops-herald `main` (PRs #1–#3).
- A comment-only change to `gecko_1_b_osx_1015.pp` on `herald-reporter-dev`
  dispatched `herald-change`; the receiver rendered and committed
  `changelogs/role/gecko_1_b_osx_1015.md` + an `activity.md` row (commit by
  `relops-herald[bot]`).
- **Gotcha fixed:** `repository_dispatch` caps `client_payload` at 10 top-level
  properties; the event has 11. Nest the whole event under `client_payload.event`
  (reporter) and unwrap it (receiver). First live attempt 422'd on this.
- Secrets `HERALD_APP_ID` / `HERALD_APP_PRIVATE_KEY` set on ronin_puppet; app
  installed on target repo `relops-herald` (Contents:write) — both confirmed by
  a successful token-mint + dispatch.

### 2026-07-13
- **GitHub App is live.** `relops-herald-dispatch` was security-reviewed (Clovis
  Foji), transferred from markco's personal account to `mozilla-platform-ops`,
  and installed on `ronin_puppet` (ctb). markco has app-manager rights. Tracked
  in [bug 2041840](https://bugzilla.mozilla.org/show_bug.cgi?id=2041840).
- Noted the shipped app is **narrower than planned**: Contents RW only, no
  webhook, no event subscriptions. Updated `docs/github-app-setup.md` to match.
- Chose the next sequence: reconcile docs → scaffold the Herald ingester/renderer
  (+ schema-validation test, + Crier/`$id` fixes) → draft the ronin reporter.
- Built the **Herald ingester** (`herald/`): validate → render newest-first
  per-entity changelogs + `activity.md`, idempotent per commit_sha via a hidden
  `herald:commit=<sha>` anchor. Added `.github/workflows/ingest.yml` (dispatch
  receiver) and `requirements.txt`.
- Wrote `tests/test_ingest.py` (10 tests, stdlib unittest). Found + fixed two
  real bugs while testing: activity rows had no idempotency anchor (would
  duplicate on re-ingest), and a test asserted on the wrong field.
- Fixed the schema "Crier" leftover; confirmed `$id`.
- Built the **ronin reporter template** (`reporter-templates/ronin_puppet/`):
  `map_entities.py` (deterministic path→entity + staging/alpha exclusion, has a
  `--self-check`), placeholder `summarize.py`, `build_event.py`, and `report.yml`
  (dispatches via `create-github-app-token`). Verified the helper chain produces
  a schema-valid event locally.

### 2026-07-02
- Decided GitHub App scope: **auth for dispatch + future webhooks** ("both"),
  created **manually via UI**, under personal account then transferred to org.
- Wrote `docs/github-app-setup.md` with the exact config (permissions:
  Metadata RO, Contents RW, Pull requests RO; events: push + pull_request;
  webhook inactive for now) and a fill-in checklist for App ID / key / secret /
  transfer status.
- Created this worklog to serve as a `/resume` anchor.
- Analyzed the repo: single commit (`7ed6bf9`), contract-only POC. Findings
  recorded in "Current state" and "Known issues" above.

# Herald Worklog

A running log of work on RelOps Herald. Purpose: a durable resume point so
anyone (or Claude via `/resume`) can pick up context without re-deriving it.

**Update this file as work progresses.** Newest entries at the top of the log.
Keep the "Current state" and "Next steps" sections rewritten to reflect reality,
not appended to.

---

## Current state (as of 2026-07-13)

**Phase:** Early POC — contract + both code halves built (ingester and reporter
template); GitHub App live; not yet wired end-to-end.

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
4. **NEXT:** Wire it live — record the App ID/key + set `HERALD_APP_ID` /
   `HERALD_APP_PRIVATE_KEY` secrets on ronin_puppet, install the reporter
   (`reporter-templates/ronin_puppet/`) into ronin_puppet, and do one real
   end-to-end dispatch. Then replace the placeholder summarizer with the real
   AI call. (App is now installed on the target repo `relops-herald`.)
5. Later: Slack output; reporters for worker-images / fxci-config / infra.

---

## Log

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

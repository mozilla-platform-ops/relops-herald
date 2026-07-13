# ronin_puppet reporter (template)

These files are meant to be **copied into the `ronin_puppet` repo**, not run
from here. They are the emitting half of the Herald pipeline: on merge to
`master`, map changed files to entities, summarize the change, and
`repository_dispatch` a Herald change event to `relops-herald`.

## Files

| File | Role |
|---|---|
| `report.yml` | GitHub Actions workflow. Goes in `ronin_puppet/.github/workflows/`. |
| `map_entities.py` | Deterministic changed-path → entity mapping (+ staging/alpha exclusion). |
| `summarize.py` | Produces `ai_summary`. **Placeholder** — wire the real AI call here. |
| `build_event.py` | Assembles the final event JSON from the above + commit metadata. |

Suggested layout in ronin_puppet: workflow in `.github/workflows/report.yml`,
the three scripts in `.github/herald/` (matches the paths in `report.yml`).

## Prerequisites

1. **Secrets on `ronin_puppet`:** `HERALD_APP_ID` and `HERALD_APP_PRIVATE_KEY`
   (the `relops-herald-dispatch` app's ID and private key).

2. ⚠️ **App must be installed on the _target_ repo `relops-herald`.** The
   dispatch is `POST /repos/mozilla-platform-ops/relops-herald/dispatches`, so
   the token minted by `create-github-app-token` needs **Contents:write on
   `relops-herald`** — which means the app has to be installed there.
   Bug 2041840 records the app as installed on **`ronin_puppet`**. Confirm it is
   also installed on **`relops-herald`**, or the dispatch step will 404/403.
   (Installing on `ronin_puppet` only matters if the reporter later needs app
   auth to read ronin itself; the built-in `github.token` already covers the
   read/PR-lookup steps here.)

## Local sanity check

The Python helpers chain without any GitHub context:

```bash
export GENERATED_AT=2026-07-13T00:00:00Z COMMIT_SUBJECT="test change"
FILES="modules/generic_worker/manifests/init.pp"
python map_entities.py $FILES  > entities.json
python summarize.py    $FILES  > ai_summary.json
python build_event.py --entities entities.json --ai ai_summary.json
python map_entities.py --self-check
```

## Buildout

`report.yml` is scoped to the **`herald-reporter-dev`** branch during
development (plus `workflow_dispatch` for manual runs), so it does not fire on
real merges to `master`. When the reporter is ready, change
`branches: [herald-reporter-dev]` → `[master]`.

## Open items

- Replace the `summarize.py` fallback with the real AI agent; keep the
  error-path shape so a failed AI call still emits a (stub) event.

## Verified against ronin_puppet (2026-07-13)

- Default branch is `master`.
- `data/roles/*.yaml`, `data/os/*.yaml`, `data/common.yaml`, and
  `modules/roles_profiles/manifests/{roles,profiles}/` all exist — the
  `map_entities.py` patterns match the real layout. Staging files like
  `data/roles/gecko_1_b_osx_1015_staging.yaml` are correctly excluded.

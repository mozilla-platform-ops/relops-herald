# all windows hardware worker pools

Every change across all windows hardware worker pools, maintained by RelOps Herald. Newest first.

<!-- HERALD:ENTRIES -->
<!-- herald:commit=1e540890ac91a70bd1749c9dad9a5d6a9ef4cdfb -->
## herald test: touch win116424h2hw.pp (windows-hardware routing)

[`1e540890ac91`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/1e540890ac91a70bd1749c9dad9a5d6a9ef4cdfb) · 2026-07-16T10:19:02-07:00 · @markcor

Added a trailing comment to the win116424h2hw role manifest to trigger and validate Herald's windows-hardware routing logic. No functional changes to the role's included profiles.

Entities:
  - role: `win116424h2hw`

Files:
  - `modules/roles_profiles/manifests/roles/win116424h2hw.pp`

Tags: `herald` `test` `windows` `roles_profiles`

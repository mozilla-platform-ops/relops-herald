# all windows Azure worker pools

Every change across all windows Azure worker pools, maintained by RelOps Herald. Newest first.

<!-- HERALD:ENTRIES -->
<!-- herald:commit=2c5b21c4232547efc71b0a3384470f36095255a5 -->
## herald test: touch win116424h2azure.pp (windows-azure routing)

[`2c5b21c42325`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/2c5b21c4232547efc71b0a3384470f36095255a5) · 2026-07-16T10:19:39-07:00 · @markcor

Added a trailing comment to the win116424h2azure role manifest to trigger a Herald replay test, exercising windows-azure routing. No functional Puppet logic was changed.

Entities:
  - role: `win116424h2azure`

Files:
  - `modules/roles_profiles/manifests/roles/win116424h2azure.pp`

Tags: `herald` `test` `windows-azure` `roles`

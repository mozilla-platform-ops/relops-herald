# GitHub App: relops-herald-dispatch

The App authenticates cross-repo automation: reporter repos (first
`ronin_puppet`) triggering Herald via `repository_dispatch`, and Herald
committing changelogs back.

**Status: DONE.** Created, security-reviewed, transferred to
`mozilla-platform-ops`, and installed on `ronin_puppet`. Tracked in
[bug 2041840](https://bugzilla.mozilla.org/show_bug.cgi?id=2041840).

> **What shipped differs from the original plan.** The app was scoped down to
> the minimum dispatch path: **Contents read/write only, no webhook, no event
> subscriptions.** The earlier plan (Metadata RO + Contents RW + PRs RO, with
> push/pull_request webhooks) was deferred — PR enrichment and webhooks can be
> added when a receiver service actually exists. History of that plan is in
> git.

## Configuration (as registered)

**Basics**
- Name: `relops-herald-dispatch`
- Created under `markco`'s personal account, then transferred to the org.

**Webhook**
- None. No receiver yet.

**Repository permissions**
| Permission | Level | Why |
|---|---|---|
| Metadata | Read-only | Mandatory (implicit) |
| Contents | Read & write | `POST /repos/{owner}/{repo}/dispatches` requires Contents:write; also commit changelogs / read diffs |

**Subscribed events**
- None.

## Artifacts (record the non-sensitive IDs here)

> Do NOT commit the private key. Store it in a secret manager / GitHub Actions
> secrets. Only non-sensitive IDs go here.

- [ ] App ID: `__________`
- [ ] Client ID: `__________`
- [ ] App slug: `relops-herald-dispatch`
- [ ] Private key (.pem): stored at `__________` (secret manager location)
- [x] Transferred to `mozilla-platform-ops` (per bug 2041840; ctb orchestrated)
- [x] Installed on `ronin_puppet` (per bug 2041840)
- [x] Installed on `relops-herald` (REQUIRED for dispatch — done 2026-07-13)

## Where the app must be installed

The dispatch is `POST /repos/mozilla-platform-ops/relops-herald/dispatches`,
sent *from* a reporter workflow in `ronin_puppet`. An app installation token is
scoped to the repos the app is installed on, and the dispatch endpoint needs
**Contents:write on the _target_ repo**. Therefore:

- **`relops-herald`** — REQUIRED. Without it, the reporter's dispatch step
  fails (403/404). *(Installed 2026-07-13.)*
- **`ronin_puppet`** — not required for the POC. The reporter's own steps (diff,
  PR lookup) use ronin's built-in `github.token`. Harmless to leave installed.

## Notes / decisions

- Security review approved by Clovis Foji; transfer + install orchestrated by
  Chris Brentano (ctb). `markco` granted app-manager privileges.
- **Decision (2026-07-13):** app must be installed on `relops-herald` (the
  dispatch target). Installing on ronin_puppet alone does not enable dispatch.
- Scoped to dispatch-only: Contents:write is the sole functional permission the
  POC needs. Webhook/PR-read deferred until there is a service to consume them.
- **TODO:** fill in the App ID / Client ID / private-key location above so the
  ronin reporter workflow can be configured to authenticate as this app.

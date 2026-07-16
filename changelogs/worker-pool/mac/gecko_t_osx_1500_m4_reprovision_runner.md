# worker pool: gecko_t_osx_1500_m4_reprovision_runner

Changelog for the `gecko_t_osx_1500_m4_reprovision_runner` mac worker pool (role + role Hiera), maintained by RelOps Herald. Newest entries first.

<!-- HERALD:ENTRIES -->
<!-- herald:commit=8198634cda099676d0737758ffbe179b3e4ad543 -->
## reprovision_runner: activate step_renew on m4-81 (auto-renewing cert) (#1276)

[`8198634cda09`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/8198634cda099676d0737758ffbe179b3e4ad543) · 2026-07-16T10:16:36-07:00 · @markcor

Switches the `gecko_t_osx_1500_m4_reprovision_runner` role from `cert_mode: vault` to `cert_mode: step_renew`, enabling the auto-renewing step-ca `step ca renew --daemon` LaunchDaemon since step-ca is now confirmed reachable from MDC1 by IP. Adds a new `step_ca_ip` parameter to the `reprovision_runner` module/profile that pins step-ca's IP in `/etc/hosts` (since its hostname isn't in MDC1 DNS) and orders the hosts entry before `step ca bootstrap`; the CA fingerprint is also promoted from a commented-out placeholder to an active Hiera key. This removes the need for the manual `mint-runner-cert.sh` periodic re-mint chore on this host.

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`

Tags: `reprovision_runner` `step-ca` `hiera` `certificates` `puppet`
<!-- herald:commit=2b44b100865cebad292df032e5c3896a549a6ec7 -->
## reprovision_runner: document the ready-to-activate step_renew flip (#1275)

[`2b44b100865c`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/2b44b100865cebad292df032e5c3896a549a6ec7) · 2026-07-16T10:15:52-07:00 · @markcor

Updated documentation comments in the gecko_t_osx_1500_m4_reprovision_runner Hiera role to clarify why `cert_mode: vault` is used instead of `step_renew`, noting the 24h step-ca provisioner cap and the need for periodic re-minting via mint-runner-cert.sh. Added detailed activation steps for flipping to `cert_mode: step_renew` once step-ca is reachable from MDC1, referencing relops-bootstrap#28 and the reprovision_runner module README. No functional configuration change; comments only.

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`

Tags: `hiera` `documentation` `reprovision_runner` `config`
<!-- herald:commit=f1b1347adff24aa4e212d234f596819c430c6305 -->
## reprovision_runner role data: wire creds + cert via vault_secrets (cert_mode: vault) (#1272)

[`f1b1347adff2`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/f1b1347adff24aa4e212d234f596819c430c6305) · 2026-07-16T10:13:33-07:00 · @markcor

Switches the reprovision_runner profile from separate hiera lookups to a single deep-merged `reprovision_runner` hash combining role data and vault.yaml secrets, using `pick_default` for defaults. Sets `cert_mode: vault` for the gecko_t_osx_1500_m4_reprovision_runner role since step-ca isn't reachable from MDC1 (GCP/IAP-only), delivering the mTLS client cert/key via vault.yaml instead of step_renew auto-renewal; role data now documents the expected flat vault.yaml layout.

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`

Tags: `puppet` `hiera` `reprovision_runner` `cert_mode` `vault`
<!-- herald:commit=fe873a0dad294210a462a06775abec93d0f5be57 -->
## Add reprovision_runner module/profile/role for the on-network runner host (#1271)

[`fe873a0dad29`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/fe873a0dad294210a462a06775abec93d0f5be57) · 2026-07-16T10:12:47-07:00 · @markcor

Adds a new `reprovision_runner` module, profile, and role to run the Hangar reprovision-runner on an on-network (MDC1) macOS host, polling Hangar over mTLS to claim and execute reprovision jobs since Hangar cannot SSH into MDC1. Includes LaunchDaemons for the runner and cert renewal (step-ca `step_renew` mode or vault-delivered certs), a Python 3.11 venv install of relops-bootstrap's orchestrator, and non-secret Hiera config for the `gecko_t_osx_1500_m4_reprovision_runner` role.

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m4_reprovision_runner.pp`

Tags: `new-module` `macos` `role` `hiera` `security`
<!-- herald:commit=ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d -->
## herald test: revert 20 ronin commits (baseline reset for replay)

[`ee98aa6d86f7`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d) · 2026-07-16T09:59:49-07:00 · @markcor

Reverts a batch of 20 prior commits as a baseline reset for replay testing, rolling back CI workflow changes (Ruby setup, cache keys), removal of `.ruby-version` pinning, Gemfile/Gemfile.lock updates, README instructions, the `kitchen_docker` script, mac staging test workflow (removing 1015 pool try support), and numerous module/role/profile files across macOS, Linux, and reprovision_runner components.

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m4_reprovision_runner.pp`

Tags: `revert` `ci` `ruby` `gemfile` `baseline-reset`

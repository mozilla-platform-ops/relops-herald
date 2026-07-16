# all mac worker pools

Every change across all mac worker pools, maintained by RelOps Herald. Newest first.

<!-- HERALD:ENTRIES -->
<!-- herald:commit=8198634cda099676d0737758ffbe179b3e4ad543 -->
## reprovision_runner: activate step_renew on m4-81 (auto-renewing cert) (#1276)

[`8198634cda09`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/8198634cda099676d0737758ffbe179b3e4ad543) · 2026-07-16T10:16:36-07:00 · @markcor

Switches the `gecko_t_osx_1500_m4_reprovision_runner` role from `cert_mode: vault` to `cert_mode: step_renew`, enabling the auto-renewing step-ca `step ca renew --daemon` LaunchDaemon since step-ca is now confirmed reachable from MDC1 by IP. Adds a new `step_ca_ip` parameter to the `reprovision_runner` module/profile that pins step-ca's IP in `/etc/hosts` (since its hostname isn't in MDC1 DNS) and orders the hosts entry before `step ca bootstrap`; the CA fingerprint is also promoted from a commented-out placeholder to an active Hiera key. This removes the need for the manual `mint-runner-cert.sh` periodic re-mint chore on this host.

Entities:
  - role-hiera: `gecko_t_osx_1500_m4_reprovision_runner`

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`

Tags: `reprovision_runner` `step-ca` `hiera` `certificates` `puppet`
<!-- herald:commit=2b44b100865cebad292df032e5c3896a549a6ec7 -->
## reprovision_runner: document the ready-to-activate step_renew flip (#1275)

[`2b44b100865c`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/2b44b100865cebad292df032e5c3896a549a6ec7) · 2026-07-16T10:15:52-07:00 · @markcor

Updated documentation comments in the gecko_t_osx_1500_m4_reprovision_runner Hiera role to clarify why `cert_mode: vault` is used instead of `step_renew`, noting the 24h step-ca provisioner cap and the need for periodic re-minting via mint-runner-cert.sh. Added detailed activation steps for flipping to `cert_mode: step_renew` once step-ca is reachable from MDC1, referencing relops-bootstrap#28 and the reprovision_runner module README. No functional configuration change; comments only.

Entities:
  - role-hiera: `gecko_t_osx_1500_m4_reprovision_runner`

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`

Tags: `hiera` `documentation` `reprovision_runner` `config`
<!-- herald:commit=f1b1347adff24aa4e212d234f596819c430c6305 -->
## reprovision_runner role data: wire creds + cert via vault_secrets (cert_mode: vault) (#1272)

[`f1b1347adff2`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/f1b1347adff24aa4e212d234f596819c430c6305) · 2026-07-16T10:13:33-07:00 · @markcor

Switches the reprovision_runner profile from separate hiera lookups to a single deep-merged `reprovision_runner` hash combining role data and vault.yaml secrets, using `pick_default` for defaults. Sets `cert_mode: vault` for the gecko_t_osx_1500_m4_reprovision_runner role since step-ca isn't reachable from MDC1 (GCP/IAP-only), delivering the mTLS client cert/key via vault.yaml instead of step_renew auto-renewal; role data now documents the expected flat vault.yaml layout.

Entities:
  - role-hiera: `gecko_t_osx_1500_m4_reprovision_runner`

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`

Tags: `puppet` `hiera` `reprovision_runner` `cert_mode` `vault`
<!-- herald:commit=fe873a0dad294210a462a06775abec93d0f5be57 -->
## Add reprovision_runner module/profile/role for the on-network runner host (#1271)

[`fe873a0dad29`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/fe873a0dad294210a462a06775abec93d0f5be57) · 2026-07-16T10:12:47-07:00 · @markcor

Adds a new `reprovision_runner` module, profile, and role to run the Hangar reprovision-runner on an on-network (MDC1) macOS host, polling Hangar over mTLS to claim and execute reprovision jobs since Hangar cannot SSH into MDC1. Includes LaunchDaemons for the runner and cert renewal (step-ca `step_renew` mode or vault-delivered certs), a Python 3.11 venv install of relops-bootstrap's orchestrator, and non-secret Hiera config for the `gecko_t_osx_1500_m4_reprovision_runner` role.

Entities:
  - role: `gecko_t_osx_1500_m4_reprovision_runner`
  - role-hiera: `gecko_t_osx_1500_m4_reprovision_runner`

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m4_reprovision_runner.pp`

Tags: `new-module` `macos` `role` `hiera` `security`
<!-- herald:commit=d53fecbb16eac8cd6787f8ef164ee210eb9c7bd7 -->
## packages: add openssl_legacy_cellar to restore Cellar layout on Catalina build workers (#1267)

[`d53fecbb16ea`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/d53fecbb16eac8cd6787f8ef164ee210eb9c7bd7) · 2026-07-16T10:10:16-07:00 · @markcor

Adds a new `packages::openssl_legacy_cellar` module that restores the legacy Homebrew openssl@1.1 Cellar layout (1.1.1h) on macOS 10.15 build workers, fixing a broken hardcoded path check in the macosx64-python-3.11 toolchain build's dylib fixup step on recently-provisioned hosts. The `gecko_3_b_osx_1015` role now includes this class with version 1.1.1h and its checksum.

Entities:
  - role-hiera: `gecko_3_b_osx_1015`

Files:
  - `data/roles/gecko_3_b_osx_1015.yaml`

Tags: `macos` `openssl` `hiera` `packages` `catalina`
<!-- herald:commit=28dab26ff79406ae625f91611528183ec06d7d29 -->
## Enable Safari Remote Automation on SIP-enabled macOS 14/15 workers (#1152)

[`28dab26ff794`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/28dab26ff79406ae625f91611528183ec06d7d29) · 2026-07-16T10:07:19-07:00 · @markcor

Adds SIP-aware TCC/Safari automation support for macOS 14/15 CI workers: a new org.mozilla.ci-tcc-pppc.mobileconfig MDM profile grants system-level TCC permissions when SIP is enabled, while add_tcc_perms.sh now detects SIP state via csrutil and only writes system TCC.db entries directly on SIP-disabled hosts. Also adjusts run-puppet.sh to avoid unnecessary reboots on transient TCC.db access errors, and temporarily disables the virt_audio_s3 class on gecko_t_osx_1500_m4(_staging) pending a BlackHole install fix on macOS 15.

Entities:
  - role-hiera: `gecko_t_osx_1500_m4`

Files:
  - `data/roles/gecko_t_osx_1500_m4.yaml`

Tags: `macos` `tcc` `sip` `safari` `mobileconfig`
<!-- herald:commit=bb63fec04a5567001b18f0233e985596e72291aa -->
## [RELOPS-2214] puppet module power mgmt (#1071)

[`bb63fec04a55`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/bb63fec04a5567001b18f0233e985596e72291aa) · 2026-07-16T10:03:50-07:00 · @markcor

Adds a new `macos_power_management` module using `pmset` exec resources to disable sleep, display sleep, and disk sleep while enabling wake-on-LAN and autorestart, replacing the old `macos_mobileconfig_profiles::power_management` class in the `power_management` profile. The `power_management` profile is now also included in several macOS roles (enterprise, gecko, nss) that previously lacked it.

Entities:
  - role: `enterprise_1_b_osx_arm64`
  - role: `enterprise_3_b_osx_arm64`
  - role: `gecko_1_b_osx_1015`
  - role: `gecko_1_b_osx_arm64`
  - role: `gecko_3_b_osx_1015`
  - role: `gecko_3_b_osx_arm64`
  - role: `gecko_t_osx_1015_r8`
  - role: `gecko_t_osx_1400_r8`
  - role: `gecko_t_osx_1500_m4`
  - role: `gecko_t_osx_1500_m4_ipv6`
  - role: `gecko_t_osx_1500_m_vms`
  - role: `nss_1_b_osx_1015`
  - role: `nss_3_b_osx_1015`

Files:
  - `modules/roles_profiles/manifests/roles/enterprise_1_b_osx_arm64.pp`
  - `modules/roles_profiles/manifests/roles/enterprise_3_b_osx_arm64.pp`
  - `modules/roles_profiles/manifests/roles/gecko_1_b_osx_1015.pp`
  - `modules/roles_profiles/manifests/roles/gecko_1_b_osx_arm64.pp`
  - `modules/roles_profiles/manifests/roles/gecko_3_b_osx_1015.pp`
  - `modules/roles_profiles/manifests/roles/gecko_3_b_osx_arm64.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1015_r8.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1400_r8.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m4.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m4_ipv6.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m_vms.pp`
  - `modules/roles_profiles/manifests/roles/nss_1_b_osx_1015.pp`
  - `modules/roles_profiles/manifests/roles/nss_3_b_osx_1015.pp`

Tags: `macos` `power-management` `puppet-module` `roles-profiles` `hiera`
<!-- herald:commit=ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d -->
## herald test: revert 20 ronin commits (baseline reset for replay)

[`ee98aa6d86f7`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d) · 2026-07-16T09:59:49-07:00 · @markcor

Reverts a batch of 20 prior commits as a baseline reset for replay testing, rolling back CI workflow changes (Ruby setup, cache keys), removal of `.ruby-version` pinning, Gemfile/Gemfile.lock updates, README instructions, the `kitchen_docker` script, mac staging test workflow (removing 1015 pool try support), and numerous module/role/profile files across macOS, Linux, and reprovision_runner components.

Entities:
  - role: `enterprise_1_b_osx_arm64`
  - role: `enterprise_3_b_osx_arm64`
  - role: `gecko_1_b_osx_1015`
  - role: `gecko_1_b_osx_arm64`
  - role: `gecko_3_b_osx_1015`
  - role: `gecko_3_b_osx_arm64`
  - role: `gecko_t_osx_1015_r8`
  - role: `gecko_t_osx_1400_r8`
  - role: `gecko_t_osx_1500_m4`
  - role: `gecko_t_osx_1500_m4_ipv6`
  - role: `gecko_t_osx_1500_m4_reprovision_runner`
  - role: `gecko_t_osx_1500_m_vms`
  - role: `nss_1_b_osx_1015`
  - role: `nss_3_b_osx_1015`
  - role-hiera: `gecko_3_b_osx_1015`
  - role-hiera: `gecko_t_osx_1500_m4`
  - role-hiera: `gecko_t_osx_1500_m4_reprovision_runner`

Files:
  - `data/roles/gecko_3_b_osx_1015.yaml`
  - `data/roles/gecko_t_osx_1500_m4.yaml`
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`
  - `modules/roles_profiles/manifests/roles/enterprise_1_b_osx_arm64.pp`
  - `modules/roles_profiles/manifests/roles/enterprise_3_b_osx_arm64.pp`
  - `modules/roles_profiles/manifests/roles/gecko_1_b_osx_1015.pp`
  - `modules/roles_profiles/manifests/roles/gecko_1_b_osx_arm64.pp`
  - `modules/roles_profiles/manifests/roles/gecko_3_b_osx_1015.pp`
  - `modules/roles_profiles/manifests/roles/gecko_3_b_osx_arm64.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1015_r8.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1400_r8.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m4.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m4_ipv6.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m4_reprovision_runner.pp`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m_vms.pp`
  - `modules/roles_profiles/manifests/roles/nss_1_b_osx_1015.pp`
  - `modules/roles_profiles/manifests/roles/nss_3_b_osx_1015.pp`

Tags: `revert` `ci` `ruby` `gemfile` `baseline-reset`

# all mac worker pools

Every change across all mac worker pools, maintained by RelOps Herald. Newest first.

<!-- HERALD:ENTRIES -->
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

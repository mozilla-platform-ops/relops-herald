# worker pool: gecko_3_b_osx_1015

Changelog for the `gecko_3_b_osx_1015` mac worker pool (role + role Hiera), maintained by RelOps Herald. Newest entries first.

<!-- HERALD:ENTRIES -->
<!-- herald:commit=d53fecbb16eac8cd6787f8ef164ee210eb9c7bd7 -->
## packages: add openssl_legacy_cellar to restore Cellar layout on Catalina build workers (#1267)

[`d53fecbb16ea`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/d53fecbb16eac8cd6787f8ef164ee210eb9c7bd7) · 2026-07-16T10:10:16-07:00 · @markcor

Adds a new `packages::openssl_legacy_cellar` module that restores the legacy Homebrew openssl@1.1 Cellar layout (1.1.1h) on macOS 10.15 build workers, fixing a broken hardcoded path check in the macosx64-python-3.11 toolchain build's dylib fixup step on recently-provisioned hosts. The `gecko_3_b_osx_1015` role now includes this class with version 1.1.1h and its checksum.

Files:
  - `data/roles/gecko_3_b_osx_1015.yaml`

Tags: `macos` `openssl` `hiera` `packages` `catalina`
<!-- herald:commit=bb63fec04a5567001b18f0233e985596e72291aa -->
## [RELOPS-2214] puppet module power mgmt (#1071)

[`bb63fec04a55`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/bb63fec04a5567001b18f0233e985596e72291aa) · 2026-07-16T10:03:50-07:00 · @markcor

Adds a new `macos_power_management` module using `pmset` exec resources to disable sleep, display sleep, and disk sleep while enabling wake-on-LAN and autorestart, replacing the old `macos_mobileconfig_profiles::power_management` class in the `power_management` profile. The `power_management` profile is now also included in several macOS roles (enterprise, gecko, nss) that previously lacked it.

Files:
  - `modules/roles_profiles/manifests/roles/gecko_3_b_osx_1015.pp`

Tags: `macos` `power-management` `puppet-module` `roles-profiles` `hiera`
<!-- herald:commit=ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d -->
## herald test: revert 20 ronin commits (baseline reset for replay)

[`ee98aa6d86f7`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d) · 2026-07-16T09:59:49-07:00 · @markcor

Reverts a batch of 20 prior commits as a baseline reset for replay testing, rolling back CI workflow changes (Ruby setup, cache keys), removal of `.ruby-version` pinning, Gemfile/Gemfile.lock updates, README instructions, the `kitchen_docker` script, mac staging test workflow (removing 1015 pool try support), and numerous module/role/profile files across macOS, Linux, and reprovision_runner components.

Files:
  - `data/roles/gecko_3_b_osx_1015.yaml`
  - `modules/roles_profiles/manifests/roles/gecko_3_b_osx_1015.pp`

Tags: `revert` `ci` `ruby` `gemfile` `baseline-reset`

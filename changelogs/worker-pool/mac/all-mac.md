# all mac worker pools

Every change across all mac worker pools, maintained by RelOps Herald. Newest first.

<!-- HERALD:ENTRIES -->
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

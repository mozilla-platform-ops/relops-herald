# worker pool: gecko_t_osx_1500_m4_reprovision_runner

Changelog for the `gecko_t_osx_1500_m4_reprovision_runner` mac worker pool (role + role Hiera), maintained by RelOps Herald. Newest entries first.

<!-- HERALD:ENTRIES -->
<!-- herald:commit=ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d -->
## herald test: revert 20 ronin commits (baseline reset for replay)

[`ee98aa6d86f7`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d) · 2026-07-16T09:59:49-07:00 · @markcor

Reverts a batch of 20 prior commits as a baseline reset for replay testing, rolling back CI workflow changes (Ruby setup, cache keys), removal of `.ruby-version` pinning, Gemfile/Gemfile.lock updates, README instructions, the `kitchen_docker` script, mac staging test workflow (removing 1015 pool try support), and numerous module/role/profile files across macOS, Linux, and reprovision_runner components.

Files:
  - `data/roles/gecko_t_osx_1500_m4_reprovision_runner.yaml`
  - `modules/roles_profiles/manifests/roles/gecko_t_osx_1500_m4_reprovision_runner.pp`

Tags: `revert` `ci` `ruby` `gemfile` `baseline-reset`

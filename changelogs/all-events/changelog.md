# All events

Every change we collect across all reporter repos, maintained by RelOps Herald. Grouped by day (newest first) and by platform; times in UTC.

<!-- HERALD:ROWS -->
## Jul 16, 2026

### 🍎 Mac workers

| Time (UTC) | Change | Worker pools | Commit |
|---|---|---|---|
| 17:18 | macOS provisioner: retry-hardened Safari automation scripts, auto-BST + mTLS Vault fetch | — | [`23c8566`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/23c856635abba915a8f962cc7f4806115c1686fd) · @markcor<!-- herald:commit=23c856635abba915a8f962cc7f4806115c1686fd --> |
| 17:17 | reprovision_runner: point m4-81 at Hangar's dedicated runner frontend | `gecko_t_osx_1500_m4_reprovision_runner` | [`e21cbf3`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/e21cbf33533305851b0c93ac9249650b5c24b1a4) · @markcor<!-- herald:commit=e21cbf33533305851b0c93ac9249650b5c24b1a4 --> |
| 17:16 | Activate step_renew auto-renewing certs on m4-81 reprovision runner | `gecko_t_osx_1500_m4_reprovision_runner` | [`8198634`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/8198634cda099676d0737758ffbe179b3e4ad543) · @markcor<!-- herald:commit=8198634cda099676d0737758ffbe179b3e4ad543 --> |
| 17:15 | Document ready-to-activate step_renew flip for reprovision_runner role | `gecko_t_osx_1500_m4_reprovision_runner` | [`2b44b10`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/2b44b100865cebad292df032e5c3896a549a6ec7) · @markcor<!-- herald:commit=2b44b100865cebad292df032e5c3896a549a6ec7 --> |
| 17:13 | reprovision_runner role switches to cert_mode: vault with deep-merged hiera secrets | `gecko_t_osx_1500_m4_reprovision_runner` | [`f1b1347`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/f1b1347adff24aa4e212d234f596819c430c6305) · @markcor<!-- herald:commit=f1b1347adff24aa4e212d234f596819c430c6305 --> |
| 17:12 | Add reprovision_runner module/profile/role for on-network runner host | `gecko_t_osx_1500_m4_reprovision_runner` | [`fe873a0`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/fe873a0dad294210a462a06775abec93d0f5be57) · @markcor<!-- herald:commit=fe873a0dad294210a462a06775abec93d0f5be57 --> |
| 17:10 | Add openssl_legacy_cellar package class to fix Catalina toolchain builds | `gecko_3_b_osx_1015` | [`d53fecb`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/d53fecbb16eac8cd6787f8ef164ee210eb9c7bd7) · @markcor<!-- herald:commit=d53fecbb16eac8cd6787f8ef164ee210eb9c7bd7 --> |
| 17:07 | Enable Safari Remote Automation on SIP-enabled macOS 14/15 workers via MDM TCC profile | `gecko_t_osx_1500_m4` | [`28dab26`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/28dab26ff79406ae625f91611528183ec06d7d29) · @markcor<!-- herald:commit=28dab26ff79406ae625f91611528183ec06d7d29 --> |
| 17:04 | macos_screenshot_helper: fix empty/blank screenshots via WatchPaths | — | [`c04a80c`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/c04a80c1672956ce47d2a06562662c00843bf68e) · @markcor<!-- herald:commit=c04a80c1672956ce47d2a06562662c00843bf68e --> |
| 17:03 | Add macos_power_management module using pmset, wired into more macOS roles | `enterprise_1_b_osx_arm64`, `enterprise_3_b_osx_arm64`, `gecko_1_b_osx_1015`, `gecko_1_b_osx_arm64`, `gecko_3_b_osx_1015`, `gecko_3_b_osx_arm64`, `gecko_t_osx_1015_r8`, `gecko_t_osx_1400_r8`, `gecko_t_osx_1500_m4`, `gecko_t_osx_1500_m4_ipv6`, `gecko_t_osx_1500_m_vms`, `nss_1_b_osx_1015`, `nss_3_b_osx_1015` | [`bb63fec`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/bb63fec04a5567001b18f0233e985596e72291aa) · @markcor<!-- herald:commit=bb63fec04a5567001b18f0233e985596e72291aa --> |
| 16:59 | Revert 20 ronin commits to reset baseline for replay testing | `enterprise_1_b_osx_arm64`, `enterprise_3_b_osx_arm64`, `gecko_1_b_osx_1015`, `gecko_1_b_osx_arm64`, `gecko_3_b_osx_1015`, `gecko_3_b_osx_arm64`, `gecko_t_osx_1015_r8`, `gecko_t_osx_1400_r8`, `gecko_t_osx_1500_m4`, `gecko_t_osx_1500_m4_ipv6`, `gecko_t_osx_1500_m4_reprovision_runner`, `gecko_t_osx_1500_m_vms`, `nss_1_b_osx_1015`, `nss_3_b_osx_1015` | [`ee98aa6`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d) · @markcor<!-- herald:commit=ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d --> |

### 🐧 Linux workers

| Time (UTC) | Change | Worker pools | Commit |
|---|---|---|---|
| 17:33 | Touch gecko_t_linux_2404_talos.pp to test Herald linux-hardware routing | `gecko_t_linux_2404_talos` | [`fb3463b`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/fb3463bb38aa8342b9fbb06a458eaf63a2df0039) · @markcor<!-- herald:commit=fb3463bb38aa8342b9fbb06a458eaf63a2df0039 --> |
| 17:09 | Recover interrupted dpkg, fetch TC binaries from GitHub, and pin Ruby to 3.4.8 | — | [`21a72bb`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/21a72bb1ffad544ef1608cf742b79a9ab6da9b2a) · @markcor<!-- herald:commit=21a72bb1ffad544ef1608cf742b79a9ab6da9b2a --> |
| 17:08 | linux: run apt autoremove when boot partition is full | — | [`5605612`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/56056122229e34ba335796149615396fce01a5bf) · @markcor<!-- herald:commit=56056122229e34ba335796149615396fce01a5bf --> |
| 16:59 | Revert 20 ronin commits to reset baseline for replay testing | — | [`ee98aa6`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d) · @markcor<!-- herald:commit=ee98aa6d86f74ab7f54186a2b193d1f0d7ed3d2d --> |

### 🪟 Windows workers

| Time (UTC) | Change | Worker pools | Commit |
|---|---|---|---|
| 17:19 | Touch win116424h2azure.pp to test Herald windows-azure routing | `win116424h2azure` | [`2c5b21c`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/2c5b21c4232547efc71b0a3384470f36095255a5) · @markcor<!-- herald:commit=2c5b21c4232547efc71b0a3384470f36095255a5 --> |
| 17:19 | Touch win116424h2hw.pp to test Herald windows-hardware routing | `win116424h2hw` | [`1e54089`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/1e540890ac91a70bd1749c9dad9a5d6a9ef4cdfb) · @markcor<!-- herald:commit=1e540890ac91a70bd1749c9dad9a5d6a9ef4cdfb --> |

### Other

| Time (UTC) | Change | Worker pools | Commit |
|---|---|---|---|
| 17:15 | reprovision_runner now also deploys and manages the hangar-screen-agent LaunchDaemon | — | [`75c660f`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/75c660fdd7877fb4103a1c2fe50f83a0c9e71711) · @markcor<!-- herald:commit=75c660fdd7877fb4103a1c2fe50f83a0c9e71711 --> |
| 17:14 | reprovision_runner: fix git safe.directory config path and pip index for MDC1 hosts | — | [`ddc923c`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/ddc923c7d4de357bfd850fa619bb0867689883ec) · @markcor<!-- herald:commit=ddc923c7d4de357bfd850fa619bb0867689883ec --> |
| 17:12 | Bump scriptworker-scripts revision in common.yaml | — | [`20fe730`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/20fe7300a0a8d135bfddc5aa645114e7fb4f50bd) · @markcor<!-- herald:commit=20fe7300a0a8d135bfddc5aa645114e7fb4f50bd --> |
| 17:11 | worker_runner: purge stale generic-worker cache-state on binary version change | — | [`145d164`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/145d164f4eebda0dcd4620ff43d0e8628d087c20) · @markcor<!-- herald:commit=145d164f4eebda0dcd4620ff43d0e8628d087c20 --> |
| 17:06 | Add systemd unit for v3 bitbar devicepool service | — | [`dc77a5b`](https://github.com/mozilla-platform-ops/ronin_puppet/commit/dc77a5bc8aa5d8ab2d2e5de8773042fbcb171ae6) · @markcor<!-- herald:commit=dc77a5bc8aa5d8ab2d2e5de8773042fbcb171ae6 --> |


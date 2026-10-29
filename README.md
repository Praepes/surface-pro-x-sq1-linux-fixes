# Surface Pro X SQ1 Linux fixes

Backports, configuration fixes and validation notes for **Surface Pro X SQ1**, running the Arch Linux ARM desktop image with `6.18.3-1-surface+`.

This is a repair journal, not a claim that every fitted device works. It distinguishes hardware tests, build checks and work that remains experimental. [中文说明](README.zh-CN.md)

**Open storage failure:** after the initial successful wake observations, the owner reported that even `/usr/bin/ls /` returned an I/O error with a normal PATH, and SSH stopped completing its handshake. The external USB root filesystem is no longer reliably readable. Suspend/resume must not be treated as stable. USB disconnect, bridge recovery, disk and filesystem causes remain to be distinguished; see [incident notes](docs/storage-after-resume.md). LTE testing is paused.

| Change | Evidence | Remaining validation |
| --- | --- | --- |
| Display VSYNC clock shared-RCG backport | Patched module identified after reboot; owner confirmed desktop and screen after suspend/resume | Repeated cold/warm boot and longer-term testing |
| Touch discovery and startup | Owner previously confirmed touch; bounded retries automatically recovered iptsd after 6 restarts on recovery boot | More boot cycles and physical pen |
| Power button → suspend | Action and initial wake confirmed; a later root-storage I/O failure remains open | Storage investigation before further suspend tests |
| Hyprland 0.55 configuration migration | Configuration errors cleared; desktop usable | Normal ongoing use |
| USB and PCIe GDSC retention | Candidate boot confirmed; initial wake succeeded, followed by owner-reported root-storage I/O failure | Not a stable suspend fix; investigate full USB storage path |
| A680 GMEM alignment | Experimental module compiled; extracted test initramfs contains 474 real modules, correct GPU/display build IDs and boot-driver coverage | Candidate boot and pixel regression |
| Wi-Fi changing identity | Driver fallback identified; link rule selected on recovery boot but connected MAC still differs | Workaround not yet effective; trace address override/failure |

See [build notes](docs/build-6.18.3.md), [boot testing](docs/boot-testing.md), [findings](docs/findings.md) and [rollback](docs/rollback.md). Candidate build checks do **not** establish hardware success.

The [dated validation record](validation/2026-10-29.json) records exact completed checks. For the touch fix, install the local udev rule, discovery service and bounded retry drop-in using [these instructions](docs/touch.md). See also [Wi-Fi identity findings](docs/wifi-identity.md).

## Scope and provenance

* Display fix: mainline [8c522da70f0c](https://github.com/torvalds/linux/commit/8c522da70f0c2e5148c4c13ccb1c64cca57a6fdb), using `clk_rcg2_shared_ops` for the VSYNC source.
* USB retention: mainline [25bc96f26cd6](https://github.com/torvalds/linux/commit/25bc96f26cd6c19dde13a0b9859183e531d6fbfc).
* PCIe retention: mainline [ccb92c78b42e](https://github.com/torvalds/linux/commit/ccb92c78b42edd26225b4d5920847dfee3e1b093).
* Experimental GPU fix: Denys Vitali's [44e2749dfbaa](https://github.com/denysvitali/linux-surface/commit/44e2749dfbaa0ecc669ffa39ae3fa6822be31ad4), adapted to the older driver without changing other GPU generations' behavior.
* Original kernel branch: [`linux-surface/kernel` at `3d83d8ff8b3c`](https://github.com/linux-surface/kernel/tree/3d83d8ff8b3c5ed045a7d576d2f0ccf2165d8c0b).
* Desktop image project: [denysvitali/surface-pro-x-arch-linux-aarch64-images](https://github.com/denysvitali/surface-pro-x-arch-linux-aarch64-images).

Original patch authors retain attribution. Backports here are not new upstream fixes. The GPU change is experimental and was not yet submitted upstream when reviewed.

Only source patches, configuration and sanitized notes are published. Device-specific modem/EFS data, Windows firmware, passwords and raw private logs are excluded.

License: GPL-2.0-only, except where individual upstream files specify otherwise.

Ubuntu follow-up: [native SQ1 graphics comparisons](docs/ubuntu-graphics.md) reproduce GTK Vulkan corruption; a tested OpenGL mitigation and source-only validation fixtures are included. Complete Ubuntu image boot remains unverified.

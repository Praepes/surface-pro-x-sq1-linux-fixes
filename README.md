# Surface Pro X SQ1 Linux fixes

Backports, configuration fixes and hardware validation notes for **Surface Pro X SQ1**. The current device runs **Ubuntu 26.04.1 ARM64 / GNOME with `6.18.3-sq1-ubuntu1` from an external USB drive**. Earlier Arch Linux ARM tests with `6.18.3-1-surface+` are preserved separately.

This is a repair journal, not a claim that every fitted device works. It distinguishes hardware tests, build checks and work that remains experimental. [中文说明](README.zh-CN.md)

## Current Ubuntu status — 2026-10-30

| Component | Evidence and limits |
| --- | --- |
| USB-root boot, GNOME and Wi-Fi | Physical SQ1 boot and login verified; current root filesystem reads/writes normally |
| Finger touch | Backported SPI HID fixes; owner confirmed click/drag, driver errors and iptsd restarts remain zero |
| Bluetooth | Address configuration allows power-on and nearby discovery; pairing/audio untested |
| Repair persistence | Module, initramfs, udev and systemd configuration installed and checked; not reboot-validated |
| Application startup | Big-core-only tests showed no consistent benefit. Native Firefox started faster than the same Snap version; Mozilla APT build installed and Dock updated. Owner reports a slight subjective improvement |
| Desktop graphics | Animations enabled, GTK OpenGL mitigation retained; one Firefox render-callback timeout remains recorded despite a successful bounded retest |
| LTE | **Not fixed**: factory-test mode, DeviceNotReady on online request, no cellular net port; see [LTE status](docs/lte-status.md) |
| Internal audio, microphone and cameras | Unavailable; board driver/device-tree integration remains missing |
| USB-root suspend/resume | **Unresolved; sleep remains disabled.** No suspend or reboot during this round |

[Physical report](docs/ubuntu-physical-20261030.md) · [Installation and rollback](docs/ubuntu-repairs.md) · [Sanitized results](validation/ubuntu-physical-20261030.json) · [Probe source](validation/ubuntu-startup/README.md)

## Earlier Arch tests

Suspend/resume previously caused root I/O errors, USB disk re-enumeration and SSH handshake failure; a complete power cycle restored boot. This remains unresolved. A currently readable Ubuntu root does not establish working suspend/resume. See [incident notes](docs/storage-after-resume.md). The table below describes the earlier Arch environment, not Ubuntu acceptance.

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

Graphics history: [native SQ1 graphics comparisons](docs/ubuntu-graphics.md) document GTK Vulkan corruption, the OpenGL mitigation and earlier validation fixtures.

# Remaining hardware work

## Cellular

The fitted SIM is readable and its application reports `ready`. The modem responds through QRTR, but reports `factory-test`; requesting `online` returns QMI `DeviceNotReady`. There is no cellular network interface.

All five original `/var/lib/rmtfs/` files in the desktop image were 2 MiB zero-filled placeholders. The [upstream Wi-Fi setup](https://github.com/linux-surface/surface-pro-x/wiki/WiFi) explicitly describes this workaround. [Issue #2](https://github.com/linux-surface/surface-pro-x/issues/2) discusses real EFS access and the Windows driver's `bootmodem_fs1`/`bootmodem_fs2` files.

Two nonzero files from **this same device's Windows installation** were staged separately, retaining the original placeholders. Windows was mounted read-only and unmounted afterward. The staged files have not yet been boot-tested. This is a provisioning experiment, not proof of the cause of `DeviceNotReady`.

The DriverStore provenance establishes the source of these boot files; it does not establish that they contain the device's current, fully provisioned calibration state. They may be initialization images rather than live EFS backups. Before the next isolated modem boot, their unchanged private hashes, sizes and access permissions were checked, as was the explicit GRUB test flag. Do not treat an unsuccessful seed-file test as justification to reset or overwrite radio NV/calibration.

**Never copy another device's modem/EFS data.** No EFS payloads or device-specific hashes are published here. SC8180X IPA/RMNET host integration remains missing in the examined driver/tree, so a registered modem alone would still not establish data connectivity. See [#22](https://github.com/linux-surface/surface-pro-x/issues/22).

## Internal audio

[Issue #21](https://github.com/linux-surface/surface-pro-x/issues/21) has a recent SQ2 speaker/microphone report. Its attachments explicitly contain unverified GPIO/supply assignments copied from another board. The later [development fork](https://github.com/denysvitali/linux-surface/tree/spx/validated-fixes-20261025) contains substantially more audio work, but still records incomplete speaker protection and lifecycle testing.

This test device is SQ1. No unverified amplifier supply changes were activated. No claim of working internal audio is made.

## Cameras

The development fork demonstrates real raw captures on a different test installation. The older 6.18 camera flow still includes direct PMIC rail manipulation and acknowledges missing proper regulator integration. Its scripts also contain watchdog/reboot actions tied to that owner's boot layout.

Those scripts were read as research and were not executed on this device. Normal board-power integration and SQ1 validation remain prerequisites. The stock [camera issue #23](https://github.com/linux-surface/surface-pro-x/issues/23) alone does not capture all recent development.

## External display

Only eDP and Writeback are currently exposed. The newer fork has real external-display progress, but integrates SAM USC hotplug forwarding, MSM DP changes and orientation/lane handling. Its implementation references APIs absent from the installed 6.18 stack and is not a standalone configuration toggle.

No live unbind/rebind of MSM/DPU was attempted. The owner has an HDMI dock available for a later integrated test. See [SAM USB-C tracking](https://github.com/linux-surface/surface-pro-x/issues/35).

## Hardware identification

The owner confirmed SQ1. The stock board device tree nevertheless contains a hard-coded SQ2 model string and SQ2-named firmware paths. That string is not evidence that a device is SQ2. No firmware path was renamed solely to correct the displayed label.

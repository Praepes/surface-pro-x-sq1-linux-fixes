# Root-storage I/O failure after initial wake observations

Status on 2026-10-29: **open, unresolved**. Pause LTE testing and additional suspend trials.

The system root is ext4 on an external USB NVMe enclosure, identified as ASUS ROG STRIX Arion, USB ID `0b05:1932`. Initial screen/touch/Wi-Fi checks and two complete s2idle log sequences did not reveal the later storage problem.

The owner subsequently reported that `su` and even `ls` were unavailable. An absolute-path test, `/usr/bin/ls /`, returned an I/O error, while the shell built-in `printf` showed a normal PATH containing `/usr/bin`. SSH connections to the last known address stopped before banner exchange completed. This establishes a storage-read failure rather than a simple PATH lookup issue. The exact transport/device/filesystem cause is not yet established.

The owner then ran the shell-built-in-only command `printf '%s\n' /sys/class/block/sd*` and reported only `sdb`, `sdb1` and `sdb2`, where the working root was previously `/dev/sda2`. Together with the I/O errors, this strongly supports USB-storage removal and re-enumeration: a replacement block-device instance does not reconnect the existing root mount to the old, failed instance. Physical identity of the new instance and the triggering USB/bridge/power event still require recovery logs. This is not a recommendation to mount the new partition over the running root or rewrite fstab to a transient sdX name.

After restarting, both the modem-test and display-only entries also failed in GRUB's EFI disk reader with `failure reading sector` from `hd0`, including sector zero. The later missing boot-marker, missing partition and `you need to load the kernel first` messages follow that read failure; the selected Linux kernel has not loaded at this point. GRUB's hdX numbering must not be equated with Linux sdX numbering without verification. The boot-entry templates were reviewed locally and the same display-only entry had booted successfully earlier. A shared pre-kernel storage-access failure now takes priority over editing individual kernel entries.

A full shutdown and power removal from the external enclosure, followed by a direct connection to another Surface USB-C port, has been requested as a diagnostic cold-start step. Its result is pending. If EFI reads still fail afterward, inspect the enclosure/disk from another host without formatting, initializing or rewriting the partition table. Neither a failed sector read nor a successful cold start alone establishes the original cause or the health of all stored data.

## Cold-start recovery result

The owner performed the combined power-removal/port-change step and successfully booted the display-only entry. SSH returned; root is again `/dev/sda2`, ext4 mounted read/write. `su` and `ls` execute normally. Read-only raw-disk checks now read sector zero, the reported failure regions and the backup-GPT area successfully. Both primary and backup GPT header and partition-array CRCs pass. This does not substitute for a full-media test or offline ext4 check.

The previous boot used USB path `4-1`, while the recovered boot uses `6-1`. Because both enclosure power and port changed, recovery cannot be attributed to either intervention alone. The observed chain strongly supports a recoverable USB-storage path/bridge state problem, but the triggering layer remains unresolved. The root disk already uses `usb-storage`, with UAS ignored by the existing kernel quirk, and its runtime power control is `on`; neither disabling UAS nor disabling runtime autosuspend is a newly demonstrated fix here.

The previous persistent kernel journal ends immediately after the successful resume and Wi-Fi association. It contains legacy DWC3 HS-PHY-not-in-L2 warnings, but no saved trace of the later disconnect. That warning alone is insufficient to identify the cause. Future reproduction needs a remote log sink and a boot arrangement that does not depend on the device being tested for its root filesystem.

Sleep-related targets are now masked **at runtime only** on the recovered boot. This protects the active USB root while investigation continues; it automatically expires at reboot. No filesystem repair, USB-controller reset or additional suspend was performed. The boot-menu and repair configurations were backed up privately to the Windows workspace.

Do not claim that the retention backport proves stable USB-root suspend. It addresses one controller-state problem; it does not establish continued root-filesystem availability, bridge behavior or storage correctness after wake. The earlier physical recovery observations remain valid but are insufficient for overall acceptance.

## Evidence and recovery priorities

* Preserve the open shell and obtain sysfs block-device names with shell built-ins if external programs cannot be read. The owner has now observed only sdb/sdb1/sdb2; obtain transport logs next rather than repeatedly testing binaries from the failed root.
* Collect kernel USB, SCSI/UAS and ext4 messages if a cached diagnostic program or existing privileged session is available. SSH handshake failure alone does not identify the cause.
* Do not hot-unplug an active USB root disk or run filesystem repair on the mounted root. Prefer an orderly restart/shutdown when available; an unresponsive machine may require a forced shutdown before reconnecting storage.
* On recovery, collect the preceding boot journal, verify the actual root device and filesystem state, and obtain an offline read-only filesystem assessment from another boot environment before deciding whether repair is needed.
* Keep display-only and original recovery payloads available. They are boot-recovery options, not known-safe suspend alternatives.

Disabling runtime autosuspend is not equivalent to preventing system-suspend power loss. Do not present a blanket `usbcore.autosuspend=-1`, a guessed UAS quirk or a live USB-controller reset as a demonstrated correction. Further changes require evidence from this incident.

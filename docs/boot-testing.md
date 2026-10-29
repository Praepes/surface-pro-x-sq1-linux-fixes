# Installed candidate boot entries

These names describe the test installation; the paths are not an installer for other systems. The original kernel, DTB and initramfs were retained. The root filesystem is on the external USB device, so these changes persist on that device rather than being a RAM-only live session. Windows was not modified.

| Menu entry | Purpose | Status on 2026-10-29 |
| --- | --- | --- |
| Surface Linux - USB PCIe resume fix | New kernel, previous verified VSYNC initramfs; default entry | Booted, matching build ID; owner confirms screen/touch/Wi-Fi after s2idle |
| Surface Linux - USB PCIe + SQ1 modem files TEST | Same kernel, explicitly selects this device's staged modem files | Not booted; no claim of LTE connectivity |
| Surface Linux - USB PCIe + A680 GPU TEST | New kernel and separate verified experimental GPU initramfs | Not booted |
| Surface Linux - display VSYNC fix | Previous kernel plus VSYNC module backport | Owner confirmed normal desktop after reboot |
| Surface Linux - ORIGINAL recovery | Original kernel and original initramfs | Preserved |

The GPU and modem tests are separate so a failure can be attributed to the tested change. Neither is silently enabled by the ordinary USB/PCIe entry.

Save desktop work before rebooting. First boot the USB/PCIe entry, check the patched kernel and retained display module, verify touch, then test one suspend/resume cycle. Reaching SSH alone does not prove that the physical screen resumed. Check the screen, touch, USB root storage and logs together. Repeat warm/cold boot and several resume cycles before promoting a candidate to hardware-validated status.

The first candidate boot was checked on 2026-10-29: running kernel build ID `9d2b1e169016d3b069882defcf4d4c5c43e38fa9` matches the compiled vmlinux. The loaded display module retains build ID `2d84ebacadaf3304cbca2ca8e01a9a1c3acb3986`. The GPU remains the original module, as intended for this entry. See the touch notes for the additional early-start failure observed during this boot.

The owner subsequently tested short-press sleep and short-press wake and reported normal screen, touch and Wi-Fi recovery. The kernel log contains two complete `PM: suspend entry (s2idle)` / `PM: suspend exit` cycles, with device resume taking about 0.8 seconds and without the previous xHCI `USBSTS 0x401` recovery error. This is a successful s2idle test on this boot, not proof of deep suspend or all PCIe-device behavior.

## Next isolated cellular test

The modem-test entry was read back from the EFI partition and verified to select the new retention kernel, retained VSYNC initramfs, existing DTB and `spx_windows_efs=1`. The two staged Windows-source files still match their private provenance records. They are nonzero, 2 MiB each and mode 0600 under a mode-0700 directory. The wrapper retains RMTFS's `-r` read-only-backing mode. Normal and recovery entries remain available. No system reboot or live replacement of the shared Wi-Fi/RMTFS backend was performed for this check.

Boot that modem-test entry separately, verify the selected RMTFS path, then compare operating mode, SIM readiness, registration and radio state. A successful control-plane change alone still needs a real IPA/RMNET host data path before Internet access can be claimed.

If a candidate fails, return to the display-only entry, then the original recovery entry if needed. The test installation also has a private backup of its previous boot configuration and a local rollback script. No remote reboot was performed during publication.

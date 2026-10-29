# Installed candidate boot entries

These names describe the test installation; the paths are not an installer for other systems. The original kernel, DTB and initramfs were retained. The root filesystem is on the external USB device, so these changes persist on that device rather than being a RAM-only live session. Windows was not modified.

| Menu entry | Purpose | Status on 2026-10-29 |
| --- | --- | --- |
| Surface Linux - USB PCIe resume fix | New kernel, previous verified VSYNC initramfs; default entry | Built and installed, not booted |
| Surface Linux - USB PCIe + SQ1 modem files TEST | Same kernel, explicitly selects this device's staged modem files | Not booted; no claim of LTE connectivity |
| Surface Linux - USB PCIe + A680 GPU TEST | New kernel and separate verified experimental GPU initramfs | Not booted |
| Surface Linux - display VSYNC fix | Previous kernel plus VSYNC module backport | Owner confirmed normal desktop after reboot |
| Surface Linux - ORIGINAL recovery | Original kernel and original initramfs | Preserved |

The GPU and modem tests are separate so a failure can be attributed to the tested change. Neither is silently enabled by the ordinary USB/PCIe entry.

Save desktop work before rebooting. First boot the USB/PCIe entry, check the patched kernel and retained display module, verify touch, then test one suspend/resume cycle. Reaching SSH alone does not prove that the physical screen resumed. Check the screen, touch, USB root storage and logs together. Repeat warm/cold boot and several resume cycles before promoting a candidate to hardware-validated status.

If a candidate fails, return to the display-only entry, then the original recovery entry if needed. The test installation also has a private backup of its previous boot configuration and a local rollback script. No remote reboot was performed during publication.

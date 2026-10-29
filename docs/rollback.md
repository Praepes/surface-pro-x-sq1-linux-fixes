# Recovery and rollback

The tested installation retains the original kernel and DTB, the original initramfs, and the previous display-only fixed initramfs. New payloads use separate names.

* For a new candidate failure, choose the previous **display VSYNC fix** entry; the completely original recovery entry is also retained.
* GPU candidates must not replace the installed root `msm.ko`. The original initramfs must continue to contain the original GPU module.
* Staged Windows EFS files are used only when a candidate's command line explicitly contains `spx_windows_efs=1`. Ordinary recovery entries use the untouched original RMTFS directory.
* Remove the RMTFS service override and reload systemd to restore the original service command. A running modem is not reinitialized merely by `daemon-reload`.
* Disable `spx-touch-discover.service` to undo the additional boot discovery step. The upstream iptsd udev rule remains untouched.
* Remove the separate `99-spx-iptsd.rules` and reload udev rules to undo the stable-tag addition; see [touch instructions](touch.md).
* Restore the backed-up Hyprland config to undo its migration; doing so on 0.55.2 also restores its old configuration errors.

Exact boot paths and rollback scripts are installation-specific. Preserve your existing boot configuration before adapting these notes.

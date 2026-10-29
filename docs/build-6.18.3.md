# Reproducing the 6.18.3 backports

These are narrow backports for the exact installed kernel described in the README. Keep the existing bootable kernel, DTB and initramfs before testing a candidate. Do not apply device-tree experiments from another machine blindly.

## USB / PCIe candidate

1. Obtain `linux-surface/kernel` commit `3d83d8ff8b3c5ed045a7d576d2f0ccf2165d8c0b` (`spx/v6.18.3`), which is based on Linux 6.18.3.
2. Save `/proc/config.gz` from the running matching kernel and use it as `.config`.
3. Apply `patches/retention/0001-usb-pcie-retention-6.18.3.patch` with zero fuzz. It changes only the seven named USB/PCIe GDSCs from `PWRSTS_OFF_ON` to `PWRSTS_RET_ON`.
4. Apply the display patch if compiling that driver too. The tested installation already has its independently built display override in the retained initramfs.
5. Run `make olddefconfig LOCALVERSION=-1-surface+`, inspect the config diff, then build `make -j6 LOCALVERSION=-1-surface+ Image`.
6. Keep the candidate Image under a new filename. Preserve the existing recovery boot entries. Reusing installed modules requires checking configuration compatibility and the exported-symbol set; simply reusing a version string is insufficient.

The recorded build used GCC 16.1.1 / binutils 2.46. Only compiler/binutils version metadata changed from the original config. Both kernels had 15,487 identical built-in symbol export entries. No new kernel feature selection was enabled. Candidate boot/suspend testing remains necessary.

Recorded raw ARM64 Image SHA-256:

```
e4b0d87db1b897cfa48a04fb2ccefdcbfe90bfa45cea4f70c5c96b93ab436351
```

## Experimental GPU module

The older driver needs a small adaptation of 44e2749: update both the programmed UCHE range and the reported GMEM base for A680. Preserve the 6.18 behavior for all other GPUs. The public patch is under `patches/experimental/`.

The module was built against the installed matching kernel headers. An external build needs the matching full-source trace include path, for example:

```sh
make -C /usr/lib/modules/6.18.3-1-surface+/build \
  M="$source/drivers/gpu/drm/msm" \
  KCFLAGS="-I$source/include/trace" -j2 modules
```

Keep this replacement in a separate candidate initramfs. A late `add_file` install hook alone was found insufficient: mkinitcpio's subsequent module population restored the original module. Use an isolated module root and verify the extracted image's GNU build ID and `.text`/`.rodata` against the candidate. Stripping can change whole-file hashes, so a raw file comparison alone is not sufficient.

The isolated root must contain **real module files**. A symlink farm made with `cp -as` was found to produce an image containing links back to the real root filesystem. Such links cannot supply drivers before that filesystem is mounted. Materialize those files before running `depmod -b` and `mkinitcpio -r`, extract the resulting image, and reject unexpected module symlinks. Verify both the patched GPU and the retained display override, plus boot-storage driver coverage (built-in drivers count).

Do not unload/reload the active display stack to test this change. Boot the separate candidate and run pixel-level and desktop regressions before promoting it.

# SQ1 graphics laboratory fixtures

These files are the source of the bounded native comparisons described in
[the test report](../../docs/ubuntu-graphics.md). They are not an image installer
or a self-contained provisioning tool. The test ran on an existing Arch SQ1
with a separately prepared Ubuntu ARM64 userspace, GTK 4, PyGObject, GNOME Shell
50.1, GJS, Mesa, systemd-nspawn, Python 3 and the required desktop services.
No firmware, root filesystem, credentials or binary driver copies are included.

The controller expects an already prepared **tmpfs** at
`/run/spx-ubuntu-native-test`, an **overlay** Ubuntu root at its `root/`, and a
writable `results/`. It checks the two mount types before running. Preparing
those mounts and collecting/unmounting them are separate operator tasks.
Do not point this laboratory controller at the active system root.

Place these source files in the RAM directory `uploads/` using these names:

| Repository file | Upload name |
| --- | --- |
| fixture.py | overnight-fixture.py |
| vulkan-probe.py | overnight-vulkan-probe.py |
| automation.js | overnight-automation.js |
| inner.sh | overnight-inner.sh |
| scale.py | overnight-scale.py |

Run `suite.py` as root on that prepared SQ1. It exposes only `renderD128` to
each private-network container, creates a private 2880×1920 GNOME virtual
monitor, and uses an isolated runtime/home for Arch clients. The physical
desktop is not the input or screenshot target. The fixed UID/GID is 1000;
adapt and review the paths and permissions for a different laboratory setup.

`SPX_PLAN=ubuntu:gl,ubuntu:sysmem`, `SPX_REPEATS=12`, `SPX_SCALE=2` and
`SPX_TAG=mitigation` select the extended comparison. A unique tag prevents
overwriting earlier cases. Run only one controller at a time against this root.
The controller stops for low available memory or excessive temperature and
uses per-case timeouts. Inspect each case's return code and capture marker;
successful completion does not mean the pixels are correct.

The optional `mesa261` mode requires a separately prepared private driver and
dependencies under `/opt/spx-mesa261-ab`. They are deliberately not supplied
here. `noubwc` is an experimental OpenGL mode and was not part of the 79-case
completed result set; it is not a tested solution to the Vulkan defect.

Compare static and post-scroll PNGs with the same client's software baseline
at the same scale, excluding transient notifications. The published JSON
contains the aggregate results. No physical suspend, USB reset, flash or reboot
is part of these fixtures.

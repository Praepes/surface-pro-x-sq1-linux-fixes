# Ubuntu SQ1 follow-up validation, 2026-10-30 05:30 HKT

The earlier 79-case native graphics battery was not repeated. This follow-up
checked the actual preview2 image read-only, queried the running device without
rendering, and tested additional ARM64 CPU media paths using WSL QEMU user mode.
It is not a full Ubuntu image boot or physical display/audio acceptance.

## Image and service configuration

37 static checks passed: root UUID/fstab/menu consistency, referenced boot
files and DTB headers, required kernel features, matching initramfs modules and
firmware paths, desktop mitigations, suspend guards, first-boot enablement and
clean image identity/build state. ARM64 `dpkg --audit` was empty; validation of
five custom/touch systemd units completed without errors. Unit parsing is not
proof those services ran successfully in a complete boot.

The source block device was read-only, and ext4 was mounted with `ro,noload`.
Writable `/run`, `/tmp` and minimal device nodes were temporary mounts. Initial
harness failures due to a missing host `lsinitramfs` and a read-only validation
scratch directory were retained and corrected, not classified as image defects.

## Missing H.264 media plugins

The image lacked the GStreamer H.264 encoder/decoder plugins used by the test.
The practical Ubuntu addition is:

```sh
sudo apt update
sudo apt install gstreamer1.0-libav gstreamer1.0-plugins-ugly
```

On the clean preview2 package state, APT planned 56 new packages, no upgrades
and no removals, with 52,861,162 bytes of archives. Installing that dependency
set into a disposable overlay of the actual image completed successfully;
`dpkg --audit` remained empty. Direct H.264 and MP4/H.264 black/white/red tests
then passed, 12 frames each, **72 frames total**, with maximum sampled channel
error 2. This validates CPU codec output in that environment, not hardware
decoding, performance, playback controls, audio output or Snap browser codecs.

The owner's local offline addon contains those Ubuntu packages, package
metadata, checksums, an installer and rollback notes. Its installer preflight
also passed inside the overlay. Package binaries are not included in this Git
repository. The already delivered preview2 image was not rebuilt or modified.
The [installer source](../scripts/install-ubuntu-media-addon.sh) expects the
complete addon folder and its metadata, not this repository by itself.

Existing VP8, VP9 and Theora solid-color paths passed 108 frames in total.
FLAC, Opus and WAV sine-wave roundtrips passed. Vorbis initially failed because
the harness forced S16LE; its documented input format is F32LE. Correcting that
test input passed; the initial failed result was preserved.
See [GStreamer's Vorbis encoder documentation](https://gstreamer.freedesktop.org/documentation/vorbis/vorbisenc.html).

## GPU follow-up and limits

The read-only DRM query reported GPU 680, GMEM size 2,097,152 and base 1,048,576
bytes, fault counter 0. This supports investigating the existing experimental
A680 GMEM alignment patch; it is not proof that it fixes the observed GTK issue.
The unpatched image retains its tested GTK OpenGL mitigation.

The existing Arch root, desktop, touch service and network remained usable.
No suspend, firmware reload, USB reset or reboot was attempted. LTE, hardware
audio/cameras, hardware codecs and complete Ubuntu GDM/new-kernel validation
remain outstanding. Temporary mounts and test processes were cleaned up.

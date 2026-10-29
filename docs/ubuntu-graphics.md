# Ubuntu ARM64 graphics testing on SQ1 (2026-10-30)

The Ubuntu desktop userspace starts natively on this SQ1, but GTK Vulkan
rendering has reproducible corruption. Selecting `GSK_RENDERER=gl` avoids
the observed corruption in the recorded comparisons while retaining hardware
OpenGL. This is a mitigation, not a Vulkan driver fix.

## Method and scope

The physical device continued running its existing Arch installation and
`6.18.3-1-surface+` kernel. An Ubuntu 26.04.1 userspace from the local preview
image ran in a temporary RAM-backed container. GNOME Shell 50.1 used a private
2880×1920 virtual monitor and the GPU render node; it did not take over the
physical panel. No reboot, suspend, firmware reload or system driver replacement
was used.

The same synthetic GTK program ran as either an Ubuntu or an Arch client
against this private Ubuntu compositor. It displayed text, gradients, buttons,
switches and an entry, performed approximately 225 scrolling and damage updates
over eight seconds, then settled at a fixed position. Every case saved static
and post-scroll screenshots. Both 1× and 2× monitor scaling were exercised.

Both client stacks report GTK 4.22.4. Arch has Mesa 26.1.1-2 and Ubuntu has
Mesa 26.0.8-1ubuntu0.3. GTK confirmed `GskVulkanRenderer`; the Vulkan loader was
restricted to the freedreno ICD, whose device enumeration returned
`Turnip Adreno (TM) 680`. Software fallback is not counted as GPU validation.

## Observations

- In the first three matched rounds at 1×, Ubuntu default rendering corrupted
  the post-scroll image in all three cases. The corresponding Arch default,
  Ubuntu GL and Ubuntu `TU_DEBUG=sysmem` comparisons did not show the defect.
- At 2×, Ubuntu default rendering corrupted the image again; the Arch default,
  Ubuntu GL, sysmem and software comparisons were clean in that round.
- Twelve additional 2× GL/sysmem pairs completed without pixels exceeding the
  stated difference threshold outside the notification mask. Including earlier
  cases, each Ubuntu mitigation completed 16 cases without the observed defect.
- In a separate eight-pair experiment, Ubuntu's original default path showed
  corruption in six cases. Loading a private copy of Arch's Mesa 26.1.1 Turnip
  library inside the otherwise unchanged Ubuntu userspace still corrupted one
  case. An upgrade alone is therefore **not a verified fix**. This private
  experiment did not install Arch packages into Ubuntu or the host.
- Application launch tests using GTK GL produced windows and screenshots for
  Calculator, Text Editor, Files, Papers, Characters and Calendar. These are
  launch/rendering observations, not full application interaction acceptance.
- A separate Text Editor check used the private compositor's virtual keyboard
  to select, replace and save text, then verified the file contents. It passed
  after correcting the harness API and shortcut timing; earlier harness failures
  were retained locally. Physical keyboard and IME behavior were not tested.

Screenshot differences are measured against the same client's software-rendered
reference. Transient GNOME notification regions are excluded; a maximum channel
delta above 32 identifies changed pixels. This numerical check supports the
captured visible corruption and does not establish universal pixel correctness.
The test harness finishing successfully is separate from rendering passing.

Upstream [Surface issue #6](https://github.com/linux-surface/surface-pro-x/issues/6)
describes A680 UBWC texture corruption and a `FD_MESA_DEBUG=noubwc` workaround.
It is a related lead, not proof that the present failures have the same cause.
`TU_DEBUG=sysmem` avoids GMEM rendering in the tested Vulkan workload; the exact
underlying defect and responsible commit remain unidentified.
Comparing the packaged Mesa policy files found no GTK-specific Turnip rule
that explains the Arch/Ubuntu difference. This does not rule out other driver,
build or userspace differences.

## Mitigation and separate extension correction

For one GTK application:

```sh
GSK_RENDERER=gl gnome-calculator
```

For Ubuntu GNOME sessions, set `GSK_RENDERER=gl` in both `/etc/environment`
and a file under `/etc/environment.d/`, preserving other settings, then log
out and back in. The [GTK documentation](https://docs.gtk.org/gtk4/running.html)
documents renderer selection. This does not repair arbitrary Vulkan programs.

The local Ubuntu image also contained an error-handler defect in its
web-search-provider extension: `error.matches` was called with only a code,
without the error domain. The supplied Ubuntu ARM64 patcher corrects the call
and handles ordinary JavaScript errors. Cancellation, other Gio errors and
ordinary JS errors were checked using GJS. In the reduced test container,
the missing default HTTPS browser is still reported as the original error;
that missing prerequisite is not suppressed or declared fixed.

## Remaining validation

The new Ubuntu kernel, complete UEFI-to-GDM boot, physical panel/touch,
Ubuntu Wi-Fi integration, Snap/browser initialization, hardware media codecs,
audio and cameras have not been accepted by these container tests. The host's
Wi-Fi, DNS, HTTPS and a disposable USB-root file roundtrip were checked separately.
The current modem reports `factory-test`; LTE is not operationally accepted.

USB-root suspend/resume remains unsafe. The Ubuntu preview keeps suspend
disabled. Driver enumeration, active services and successful synthetic CPU
media pipelines are not substituted for missing hardware tests.

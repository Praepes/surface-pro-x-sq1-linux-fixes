# Touch discovery on the SQ1 test device

The supported controller enumerates as SPI HID `001C:045E:0C40.*`. The installed `iptsd@.service` binds to its hidraw device and stops when systemd no longer considers the device available.

Replaying discovery initially started iptsd and restored touch, confirmed by the owner. A subsequent replay stopped it again. Inspection showed that the current udev tags had lost `systemd`, although the historical tags still listed it. The upstream rule probes with `iptsd-check-device`; probing an already-owned device does not reliably preserve that match. The local rule makes systemd membership depend on the identified controller rather than the result of that probe. The upstream rule and service are unchanged.

On this exact board, after installing the rule, two successive discovery passes retained `systemd` in `CURRENT_TAGS`, retained `SYSTEMD_WANTS`, and left iptsd active. A new physical touch test and reboot persistence check remain pending.

## Install

Requires iptsd, systemd and udev. First verify that the device really is the matching controller; do not broaden the match to every hidraw device.

From the repository root:

```sh
sudo install -m 0644 udev/99-spx-iptsd.rules /etc/udev/rules.d/
sudo install -m 0644 systemd/spx-touch-discover.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
sudo systemctl enable --now spx-touch-discover.service
sudo udevadm settle
systemctl list-units 'iptsd*'
```

The hidraw number can change. The rule uses the actual device name, so no fixed hidraw number is enabled manually at boot.

## Undo

```sh
sudo systemctl disable --now spx-touch-discover.service
sudo rm /etc/systemd/system/spx-touch-discover.service /etc/udev/rules.d/99-spx-iptsd.rules
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
```

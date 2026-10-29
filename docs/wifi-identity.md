# Wi-Fi MAC changes between boots

The SQ1 test device's kernel explicitly reports:

```
ath10k_snoc 18800000.wifi: invalid MAC address; choosing random
```

The device's link address changed between recorded boots. NetworkManager has no cloned-MAC policy configured for the active connection, uses the iwd backend, and obtains a DHCP client identifier based on that address. The router consequently assigned a different lease after each observed boot. This is a driver/firmware fallback rather than evidence that NetworkManager privacy randomization was enabled. The reason the driver receives an invalid factory address has not yet been resolved.

## Staged workaround

A device-local `.link` configuration pins the **currently working locally administered unicast MAC**. It matches both `ath10k_snoc` and `platform-18800000.wifi`, retains the existing `NamePolicy=keep kernel`, and sets `MACAddressPolicy=none` plus an explicit `MACAddress`.

The file is installed on the device, but no network rediscovery, disconnect, or connection reactivation was performed. Its application at next boot is pending validation. The retained initramfs does not contain `ath10k_snoc`, so this interface is currently discovered after switching to the real root filesystem. If that boot arrangement changes, the configuration may also need to be included in the initramfs.

The [template](../systemd/10-spx-wifi-stable-mac.link.example) deliberately contains no usable shared address. Replace the placeholder with an address unique to your device, then install it as `/etc/systemd/network/10-spx-wifi-stable-mac.link`. Do not copy another machine's address. Record the chosen identity privately; actual MACs, SSIDs and local IPs are not published here.

This is a persistent userspace workaround, not a recovery of the original factory MAC. It does not guarantee a fixed IP address. For a fixed address, reserve a DHCP lease for the stable MAC on the router. To undo the workaround, remove that device-local `.link` file before the next boot.

Reference: [systemd.link](https://www.freedesktop.org/software/systemd/man/latest/systemd.link.html). `MACAddress=` requires `MACAddressPolicy=` to be unset, empty or `none`; the first matching `.link` file takes precedence.

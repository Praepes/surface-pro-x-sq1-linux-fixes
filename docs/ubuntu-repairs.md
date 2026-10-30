# Ubuntu 修复文件、安装与回退

适用实测环境：Surface Pro X SQ1、Ubuntu 26.04.1 ARM64、`6.18.3-sq1-ubuntu1`。当前机器已装好本轮修复。下面提供复现入口，不需要再次在它上面安装，也没有自动重启步骤。

| 仓库文件 | 实机安装位置 | 用途 |
| --- | --- | --- |
| scripts/build-ubuntu-touch-backport.sh | 在匹配的已准备内核构建树旁运行 | 拉取固定提交、校验源码并构建 SPI HID 模块 |
| config/ubuntu/spx-touch-backport | /etc/initramfs-tools/hooks/spx-touch-backport，755 | 让 initramfs 包含触摸覆盖模块 |
| scripts/spx-bluetooth-address | /usr/local/libexec/spx-bluetooth-address，755 | 通过内核 MGMT 接口配置缺失的蓝牙地址 |
| systemd/spx-bluetooth-address@.service | /etc/systemd/system/，644 | 对指定控制器执行地址配置 |
| systemd/spx-bluetooth-discover.service | /etc/systemd/system/，644 | initramfs 切换后重放蓝牙发现事件 |
| udev/99-spx-bluetooth-address.rules | /etc/udev/rules.d/，644 | 匹配 Surface UART 蓝牙并触发服务 |
| config/ubuntu/50-spx-kernel-support.conf | /etc/systemd/user/snap.prompting-client.daemon.service.d/，644 | 内核缺少 AppArmor notify 接口时跳过不支持的提示进程 |

## 触摸

构建脚本参数为内核源码目录、构建输出目录和一个不存在的新工作目录。必须使用该内核的配置、生成头文件与 Module.symvers。源码来自 [cfcaa144](https://github.com/denysvitali/linux-surface/tree/cfcaa144842c79bd11cc343de38ca5536f8adcee/drivers/hid/spi-hid)，文件哈希见 [provenance](../validation/ubuntu-touch-source-provenance.json)。构建出的模块版本为 `20261030.cfcaa144.backport1`。

先备份 `/boot/initrd.img-6.18.3-sq1-ubuntu1` 和任何已有的同名覆盖模块。核对 modinfo 的 vermagic 后，将新模块安装为 `/lib/modules/6.18.3-sq1-ubuntu1/updates/spx/spi-hid.ko`（644），安装上表 hook，运行 `depmod -a 6.18.3-sq1-ubuntu1` 和 `update-initramfs -u -k 6.18.3-sq1-ubuntu1`。用 modinfo 确认选择的是覆盖模块，再用 lsinitramfs 检查实际 initramfs。完整 iptsd 用户空间及原有自动发现配置也必须保留。

分步构建和实机运行已验证；仓库通用构建入口只做了语法检查。持久化文件已检查，尚未重启验收。回退时移除新覆盖模块和 hook、运行 depmod，并恢复备份的原 initramfs；在正常关机后的下次启动生效。不要在当前桌面热卸载触摸模块。

## 蓝牙和权限提示服务

按表安装蓝牙文件后，运行 `systemctl daemon-reload`、`udevadm control --reload-rules`、`systemctl enable --now spx-bluetooth-discover.service`。helper 只匹配 c8c000.serial，已配置好的控制器不改地址；新地址在各设备上独立生成并保存在 `/var/lib/spx/bluetooth-address`，不是出厂地址提取结果。不要把该地址文件打包分享。

蓝牙开启和扫描已验证，配对及开机自动配置未验收。回退时先 disable discover 服务，再移除对应 helper、两个 unit 和 udev 规则，重新加载配置。可保留地址文件，以便后续恢复。

权限提示 drop-in 安装后，在桌面用户会话运行 `systemctl --user daemon-reload` 和 `systemctl --user reset-failed snap.prompting-client.daemon.service`。它保留 AppArmor 和 Snap 沙箱，只跳过需要当前内核没有的通知接口的可选提示程序。删除 drop-in 并重新加载即可回退。

## Firefox 与测试

原生浏览器遵循 [Mozilla 官方 APT 安装步骤](https://support.mozilla.org/en-US/kb/install-firefox-linux)，签名密钥指纹核对为 `35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3`，实装版本为 159.0，另装中文语言包。启动测量在本机真实 GNOME 会话中执行。

原 Snap 及其资料保留，可用 `snap run firefox` 启动；本机将资料复制到原生目录并把 Dock 入口换成 firefox.desktop。动画保持开启，没有修改系统调度策略。测量代码和边界见 [测试入口](../validation/ubuntu-startup/README.md)，结果及一次超时记录见 [JSON](../validation/ubuntu-physical-20261030.json)。

USB 根盘睡眠恢复仍未解决，保留镜像禁止睡眠的配置。本仓库不包含完整镜像、编译好的内核模块、Windows 固件或设备专属数据。

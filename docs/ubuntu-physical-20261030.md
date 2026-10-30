# SQ1 Ubuntu 实机修复与启动性能 · 2026-10-30

完整 preview3 已在真实 SQ1 上从外置 USB 盘进入 GNOME 桌面。此次通过 SSH 读取到了正在运行的 `6.18.3-sq1-ubuntu1` 内核和桌面进程，不能再把本次验收等同于此前容器或 QEMU 测试。原镜像文件及其哈希没有改变，以下修复写入了当前外置盘上的系统。

## 已完成

| 项目 | 结果和边界 |
| --- | --- |
| 触摸 | 原 SPI HID 驱动初始化/运行时电源管理存在竞态。回移开发分支修复后 ready，iptsd active、重启计数 0、总线/逻辑错误 0；用户确认点击、拖动正常。没有实体笔测试。 |
| 触摸持久化 | 独立模块安装到 updates/spx，depmod 已选择它；initramfs 实际包含同一模块。未重启验收。 |
| 蓝牙 | 固件已加载，失败点是控制器缺少 public-address 配置。补充每设备独立保存的稳定地址后可开启、扫描；没有配对和蓝牙音频测试。udev/systemd 开机配置已安装，未重启验收。 |
| 桌面动画 | 按机主反馈恢复开启，未再关闭。 |
| Snap 提示服务 | 证实当前内核缺少 AppArmor notify 接口，服务登录时连续失败 6 次。添加条件启动配置后跳过不支持的提示程序，失败状态清除；AppArmor 仍开启，检查时加载 238 个 profile。 |
| Firefox | 安装签名 Mozilla APT 源的 ARM64 原生 Firefox 159.0 和中文语言包；Dock 已改为原生版。原 Snap 和原始资料保留，已本地复制资料到原生目录。 |

触摸源：[denysvitali/linux-surface，固定提交 cfcaa144](https://github.com/denysvitali/linux-surface/tree/cfcaa144842c79bd11cc343de38ca5536f8adcee/drivers/hid/spi-hid)。新增的本地版本标识为 `20261030.cfcaa144.backport1`，不是声称这些上游驱动改动由本项目原创。

## CPU 调度与打开应用的卡顿

CPU 0–3 capacity=355、最高 1.7664GHz，CPU 4–7 capacity=1024、最高 2.9952GHz。两组均为 performance governor，温度约 35–37°C，检查时无持续 CPU、内存或 I/O 饱和。Firefox 未被限制在小核。

保持同一测试程序，按“默认全部核 → 仅大核 → 仅大核 → 默认全部核”顺序测 Snap Firefox。启动到 Marionette 自动化接口可用分别为 **3.432、2.569、2.699、2.446 秒**。第一轮还包含新测试资料目录的初始化。预热后的默认调度没有比仅大核慢，现有样本不支持将卡顿归因于大核调度失效，因此没有修改系统调度器或持久绑核。

同版本 Firefox 154.0 的原生官方 ARM64 包测得 **1.849、1.170 秒**；Snap 基线为 **3.492、2.470 秒**。两者均使用 Wayland、Adreno FD680 和硬件 WebRender。Snap 使用自身 Mesa 25.2.8，原生版使用系统 Mesa 26.0.8，故只能确认原生启动路径明显更快，不能把全部收益归因于 Snap 沙箱。

安装的新原生 Firefox 159.0 测得 **1.970、1.169 秒**。第二轮虽然成功启动和导航，但渲染回调超时，原失败记录保留；增加可见性记录和 8 秒截止后的一次补测完成 120 个帧间隔，页面可见、启动就绪 **1.933 秒**。原超时原因尚未证实，不能据一次补测宣布不存在图形问题。

这些时间是**进程启动到自动化接口就绪**，不是物理点击到屏幕显示的延迟。测试使用独立资料目录和本地静态测试页；没有修改用户的 Firefox 性能偏好或关闭浏览器沙箱。测试页的 requestAnimationFrame 间隔也不等同于整桌面或面板实际扫描帧率。

GTK GL 简单测试窗口的首次 after-paint 约 782–861 毫秒，已构建页面切换约 10.7–14.9 毫秒。Firefox 154 本地页面首次内容绘制约 64–104 毫秒。存储只做了现有 GTK 库的 192 次 4KiB 只读直接随机读取：中位数 0.204ms、p95 0.792ms；这不是完整磁盘或冷启动基准。当前数据更支持应用初始化存在开销，不能据此证明所有应用、网页或设备无卡顿。

## 未完成

- 扬声器、麦克风：ALSA 仍无声卡。运行中的设备树没有接入 SC8180x 的完整音频板级拓扑，相关机器驱动也未安装，不能靠重新启动 PipeWire 解决。
- 摄像头：无 /dev/video 捕获设备，缺少完整板级摄像头管线。没有运行上游实验脚本中的直接 PMIC 供电写入。
- LTE：SIM 可识别，但基带仍在 factory-test；一次有限 online 请求返回 QMI 52 DeviceNotReady，同时缺少蜂窝数据网络端口。未做 NV 写入、重置或复制其他设备的基带数据。
- USB 根盘睡眠恢复：原严重故障未解决，本轮没有睡眠、断盘、USB reset 或重启。镜像原有禁止睡眠配置保留。
- 真实硬件视频解码、笔、蓝牙配对、外接显示，以及修复后的冷启动持久性仍待验收。

## 复现和回退

本仓库只提供源码、配置和脱敏结果，不发布编译好的模块、完整系统镜像或固件。

触摸构建入口为 `scripts/build-ubuntu-touch-backport.sh`，需要原有 6.18.3-sq1-ubuntu1 内核的已配置源码、构建输出和 Module.symvers。它下载固定提交的五个文件并校验哈希，仅构建 spi-hid 外部模块，不修改原内核源码。构建后核对 vermagic；安装到对应内核 updates/spx，再 depmod 并确保 initramfs 包含覆盖模块。必须先备份原 initramfs。具体环境的逐步安装已完成，仓库通用构建入口本轮只检查语法。

蓝牙源码为 `scripts/spx-bluetooth-address`，安装路径 `/usr/local/libexec/spx-bluetooth-address`（755）；对应两个 unit 在 systemd/、规则在 udev/。只匹配 Surface 的 c8c000.serial 控制器，已配置的控制器不改地址。安装后 reload systemd 和 udev、enable spx-bluetooth-discover.service。设备地址由各机器自行生成，绝不共用本机地址。当前控制器开启与扫描通过，开机自动配置尚未重启验收。

AppArmor 提示服务的修复是在用户 unit 的 drop-in 添加 `ConditionPathExists=/sys/kernel/security/apparmor/.notify`，仅跳过不受内核支持的可选提示进程，保持 AppArmor 本身启用。

触摸回退为删除对应 updates/spx/spi-hid.ko 和 initramfs hook、depmod，然后恢复备份的原 initramfs，在正常关机后的下一次启动生效。蓝牙回退为 disable discover unit、移除新 helper/unit/udev 规则并 reload。不要在 USB 根盘上用睡眠验证回退。原生 Firefox 来自签名 Mozilla APT 源，旧 Snap 与原资料仍保留，可通过 `snap run firefox` 使用。

脱敏原始测量见 [validation JSON](../validation/ubuntu-physical-20261030.json)，触摸来源哈希见 [provenance](../validation/ubuntu-touch-source-provenance.json)。一次渲染回调超时也保留在结果中，没有将其删除或计为通过。私人连接配置、硬件标识和原始私人日志没有发布。

官方参考：[Mozilla Linux 安装说明](https://support.mozilla.org/en-US/kb/install-firefox-linux)、[Mozilla Marionette 协议](https://firefox-source-docs.mozilla.org/remote/marionette/Protocol.html)、[GTK FrameClock 文档](https://docs.gtk.org/gdk4/class.FrameClock.html)。

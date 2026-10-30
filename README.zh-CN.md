# Surface Pro X SQ1 Linux 修复记录

Surface Pro X **SQ1** 的源码修复、配置和实机测试记录。当前系统为 **Ubuntu 26.04.1 ARM64 / GNOME，内核 `6.18.3-sq1-ubuntu1`**，从外置 USB 设备运行；同时保留早期 Arch Linux ARM（`6.18.3-1-surface+`）的记录。

## Ubuntu 当前状态 · 2026-10-30

| 项目 | 结果 |
| --- | --- |
| 外置盘启动、GNOME、Wi-Fi | 已在真实 SQ1 上启动并登录；当前根文件系统正常读写 |
| 手指触摸 | 回移 SPI HID 修复后，机主确认点击、拖动正常；驱动错误和 iptsd 重启计数为 0 |
| 蓝牙 | 补齐控制器地址配置后，开启和附近设备扫描通过；配对及蓝牙音频未测 |
| 触摸和蓝牙持久化 | 模块、initramfs、udev 和 systemd 配置已安装检查；尚未重启验收 |
| 应用启动卡顿 | 大核对照没有稳定收益；原生 Firefox 比同版本 Snap 启动更快，已安装 Mozilla 官方 APT 版并更新 Dock。机主反馈感觉略有改善，未宣称全部卡顿消失 |
| 桌面与图形 | 保持动画开启、GTK 使用 OpenGL；保留一次 Firefox 绘制回调超时，后续有限补测通过 |
| LTE | **未修复**：基带处于 factory-test，online 请求返回 DeviceNotReady，缺少蜂窝数据网口；见 [LTE 状态](docs/lte-status.md) |
| 扬声器、麦克风、摄像头 | 未可用，仍缺板级驱动和设备树集成 |
| USB 根盘睡眠恢复 | **未解决，禁止睡眠配置保留**；本轮未睡眠或重启 |

[本轮实机报告](docs/ubuntu-physical-20261030.md) · [安装与回退](docs/ubuntu-repairs.md) · [脱敏测量](validation/ubuntu-physical-20261030.json) · [测试脚本](validation/ubuntu-startup/README.md)

## 早期 Arch 测试记录

曾在睡眠恢复后出现 `/usr/bin/ls /` 的 I/O error、USB 根盘重新枚举及 SSH 无法握手，完全断电后恢复启动。这一故障尚未修复；当前 Ubuntu 正常运行不等于睡眠恢复通过。见[故障记录](docs/storage-after-resume.md)。下表属于早期 Arch 测试，不能代替 Ubuntu 的结果。

| 项目 | 当前结果 |
| --- | --- |
| 热重启显示 | 已回移主线 VSYNC 时钟修复，确认加载；机主确认重启和睡眠唤醒后画面正常，长期稳定性仍需复测 |
| 手指触摸 | 机主曾确认正常；恢复启动后，有限重试机制自动重启 6 次使 iptsd 保持 active，更多开机周期和实体笔仍待验 |
| 触控笔 | 虚拟输入设备已创建，无实体笔，未实测 |
| 短按电源 | 动作与初次唤醒确认正常，随后出现根盘 I/O 故障；排查存储前不继续睡眠测试 |
| Hyprland | 旧配置的四类报错已修正并重新加载 |
| USB / PCIe 睡眠恢复 | 新内核已启动；初次唤醒正常后，机主报告根盘 I/O 故障，不能作为稳定睡眠修复；需继续检查整条 USB 存储链路 |
| A680 GPU | 回移版已编译；独立测试 initramfs 的 474 个实际模块、GPU / 显示版本标识和启动驱动覆盖已核验；启动及像素回归待验 |
| Wi-Fi 每次启动换 IP | 驱动随机地址回退已确认；恢复启动选中了固定 MAC 规则，但实际连接地址仍不同，固定规则尚未达到预期，见[说明](docs/wifi-identity.md) |
| 内置音频 / 摄像头 / 外接显示 / LTE | 见[调查记录](docs/findings.md)，没有宣称已可用 |

内核镜像、设备专属基带数据、Windows 固件、账号密码和私人日志不上传。这个项目用于公开可复现的补丁和真实验证记录。

[编译说明](docs/build-6.18.3.md) · [回退说明](docs/rollback.md) · [上游出处](README.md#scope-and-provenance)

[本次验证记录](validation/2026-10-29.json) · [触摸修复安装步骤](docs/touch.md)

图形历史：[原生图形对照记录](docs/ubuntu-graphics.md) 记录 GTK/Vulkan 花屏复现、OpenGL 缓解配置及早期测试源码。

# Surface Pro X SQ1 Linux 修复记录

测试环境：Surface Pro X **SQ1**、Arch Linux ARM 桌面镜像、内核 `6.18.3-1-surface+`。

**当前有未解决的存储故障：** 初次唤醒观察正常后，机主报告 `/usr/bin/ls /` 也报 I/O error，PATH 正常，SSH 同时无法完成握手。外置 USB 根文件系统已不能可靠读取。睡眠恢复不能视为稳定；尚需区分 USB 掉线、桥接恢复、磁盘或文件系统故障，见[故障记录](docs/storage-after-resume.md)。LTE 测试暂停。

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

Ubuntu 后续：[原生图形对照记录](docs/ubuntu-graphics.md) 已复现 GTK/Vulkan 花屏，附 OpenGL 缓解配置及测试源码；完整 Ubuntu 镜像启动仍未验收。

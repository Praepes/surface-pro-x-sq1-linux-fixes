# Surface Pro X SQ1 Linux 修复记录

测试环境：Surface Pro X **SQ1**、Arch Linux ARM 桌面镜像、内核 `6.18.3-1-surface+`。

| 项目 | 当前结果 |
| --- | --- |
| 热重启显示 | 已回移主线 VSYNC 时钟修复，重启后确认加载，机主确认桌面正常；长期稳定性仍需复测 |
| 手指触摸 | 本次重启机主反馈正常，稳定 udev 标签已保留；但 iptsd 早期仍有设备未就绪失败，稍后启动成功；已补有限重试，重试配置的下次开机效果待验 |
| 触控笔 | 虚拟输入设备已创建，无实体笔，未实测 |
| 短按电源 | 已配置为 suspend，并核验 logind 生效值；修复内核下的恢复待验 |
| Hyprland | 旧配置的四类报错已修正并重新加载 |
| USB / PCIe 睡眠恢复 | 已启动新内核，运行中 GNU build ID 与候选一致，机主确认屏幕和触摸正常；实际睡眠恢复待验 |
| A680 GPU | 回移版已编译；独立测试 initramfs 的 474 个实际模块、GPU / 显示版本标识和启动驱动覆盖已核验；启动及像素回归待验 |
| Wi-Fi 每次启动换 IP | 已确认驱动收到无效 MAC 后随机生成地址；已写入本机固定 MAC 启动规则，下次开机生效待验；固定 IP 仍需路由器 DHCP 保留，见[说明](docs/wifi-identity.md) |
| 内置音频 / 摄像头 / 外接显示 / LTE | 见[调查记录](docs/findings.md)，没有宣称已可用 |

内核镜像、设备专属基带数据、Windows 固件、账号密码和私人日志不上传。这个项目用于公开可复现的补丁和真实验证记录。

[编译说明](docs/build-6.18.3.md) · [回退说明](docs/rollback.md) · [上游出处](README.md#scope-and-provenance)

[本次验证记录](validation/2026-10-29.json) · [触摸修复安装步骤](docs/touch.md)

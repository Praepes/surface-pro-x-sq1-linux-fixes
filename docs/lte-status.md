# LTE 状态与后续入口 · 2026-10-30

**本机 LTE 尚未可用。** 本轮停在故障定位阶段，没有网络注册、获取蜂窝 IP 或实际蜂窝流量的成功记录。识别 SIM 或能响应 QMI 查询都不能算联网通过。

## 已知证据

| 层级 | 当前结果 |
| --- | --- |
| 固件与控制面 | modem remoteproc 运行，QRTR/QMI 查询可响应 |
| SIM | 插卡可识别，USIM 应用 ready；不公开卡号和身份数据 |
| 基带运行模式 | factory-test；一次 online 请求返回 QMI 52 DeviceNotReady |
| Linux 数据面 | 无蜂窝数据网络端口；ModemManager 无法创建可用 modem |
| Ubuntu RMTFS | 镜像保留零填充占位文件；这不是已验证的本机完整配置/校准数据 |

早期 Arch 曾把**同一台设备 Windows 驱动目录**内的 bootmodem_fs1/fs2 另存为独立测试来源，原占位文件保留。它们未完成独立启动验收，也不等于当前基带的完整活动 EFS 备份。Ubuntu 没有因为这些文件存在就被标记为已配置。来源说明见 [findings](findings.md#cellular)。

## 两个独立阻塞点

1. **基带初始化/配置**：SIM ready 但不能进入 online。需要核对 RMTFS、tqftpserv 的启动请求、所用文件和固件版本，判断缺少哪一步；现有证据不能把 DeviceNotReady 唯一归因于占位文件。
2. **SC8180X 数据通道**：当前内核/设备树没有接入完整 IPA/RMNET/WWAN 路径。即使 online 成功，仍需真正的数据端口、驱动资源和 ModemManager 集成，才有条件验证 APN 和联网。

上游 [surface-pro-x #22](https://github.com/linux-surface/surface-pro-x/issues/22) 也记录了 QRTR 能查询 SIM、但 ModemManager 找不到网络端口的现象。开发分支的 [TODO](https://github.com/denysvitali/linux-surface/blob/cfcaa144842c79bd11cc343de38ca5536f8adcee/TODO.md) 和 [验收清单](https://github.com/denysvitali/linux-surface/blob/cfcaa144842c79bd11cc343de38ca5536f8adcee/PORT-CHECKLIST.md) 同样保留 cellular provisioning、IPA 和 WWAN 的缺口；不能把“modem 启动了”解释为完整 LTE 修复。

## 接续工作与通过条件

下一轮优先检查本机服务请求和初始化文件的实际来源，再评估 SC8180X 数据通道的驱动、设备树和硬件资源。调试时保留现有 Wi-Fi 远程连接及原文件备份。尚未执行基带 NV 写入、重置、其他设备 EFS 复制或会中断 Wi-Fi 的 modem 重启。

通过条件需包含：SIM ready、online、真实运营商注册、蜂窝数据端口、正确路由及实际蜂窝收发；随后才验证重连和重启持久性。当前没有任何一轮满足整组条件。

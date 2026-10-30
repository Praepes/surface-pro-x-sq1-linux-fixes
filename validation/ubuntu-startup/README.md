# Ubuntu 启动测试源码

这两个独立 Python 脚本对应 2026-10-30 的 SQ1 实机诊断。没有 SSH 客户端、密码、设备 IP 或私人资料。请在本机已登录的 Wayland 桌面用户终端手动运行；会短暂出现并自动关闭测试窗口，不会重启或睡眠。

```sh
GSK_RENDERER=gl python3 validation/ubuntu-startup/probe-gtk.py
GSK_RENDERER=gl SPX_FIREFOX_BINARY=/usr/bin/firefox python3 validation/ubuntu-startup/probe-firefox.py
```

GTK 脚本需要系统 Python 的 GI/GTK 4 支持，默认启动三次简单窗口，测量 import、map、after-paint 和页面切换。它包含 Python/GI 初始化开销，不代表任意应用的启动时间。

Firefox 脚本使用独立临时资料目录和仅回环地址的 Marionette 协议，默认启动两次；测试页为自带的本地 data URL。它不打开或修改用户的浏览器资料，结束时关闭自己启动的进程并删除临时目录。需要空闲端口 2829，发布版添加了启动前端口占用检查；这一检查只做过语法核对，未重跑实机。临时 Firefox 进程开启特权自动化接口，退出后不会留下自动化服务。

`SPX_PROBE_RUNS=1` 可只做一轮；`--cpu-ab` 在测试进程范围内执行默认核/大核/大核/默认核对照，仅适合本测试设备的大核 4–7，不改变系统调度器或其他应用的亲和性。

输出为逐行 JSON。必须检查每轮的 error、子进程退出码、页面 visibility 和渲染回调截止原因，不能仅根据整个脚本退出码判定通过。原脚本已经出现过一次绘制回调超时，详见 [结果 JSON](../ubuntu-physical-20261030.json)。部分早期结果由未加入可见性记录的版本产生，原始字段差异已保留。

automation_ready_seconds 是启动到 Marionette 接口可用的时间；session_ready_seconds 包含 NewSession 初始化，不是物理点击到显示的延迟。requestAnimationFrame 间隔也不是面板扫描时序或整桌面 FPS。不同包会使用不同版本的 Mesa/库，不应把全部差异归因于 Snap 沙箱。

参考：[Mozilla Marionette](https://firefox-source-docs.mozilla.org/remote/marionette/Protocol.html)、[GTK FrameClock](https://docs.gtk.org/gdk4/class.FrameClock.html)。

#!/bin/bash
set -uo pipefail
R=/home/surface/native-test-results
export LC_ALL=C.UTF-8 XDG_SESSION_TYPE=wayland XDG_CURRENT_DESKTOP=ubuntu:GNOME GNOME_SHELL_SESSION_MODE=ubuntu
export GSETTINGS_BACKEND=memory GIO_USE_VFS=local GTK_USE_PORTAL=0
unset GSK_RENDERER TU_DEBUG FD_MESA_DEBUG LIBGL_ALWAYS_SOFTWARE MESA_LOADER_DRIVER_OVERRIDE
gnome-shell --headless --virtual-monitor 2880x1920 --automation-script /usr/local/sbin/spx-overnight-automation.js > "$R/$SPX_CASE-shell.log" 2>&1 &
shell=$!
app=0
cleanup() { test "$app" = 0 || kill "$app" 2>/dev/null || true; kill "$shell" 2>/dev/null || true; wait 2>/dev/null || true; }
trap cleanup EXIT
for n in $(seq 1 60); do
  kill -0 "$shell" 2>/dev/null || exit 10
  test -S "$XDG_RUNTIME_DIR/wayland-0" && break
  sleep .5
done
python3 /usr/local/sbin/spx-overnight-scale > "$R/$SPX_CASE-scale.log" 2>&1 || exit 14
touch "$R/$SPX_CASE-shell.ready"
if [ "$SPX_CLIENT" = ubuntu ]; then
  export WAYLAND_DISPLAY=wayland-0 SPX_RESULTS="$R"
  export VK_DRIVER_FILES=/usr/share/vulkan/icd.d/freedreno_icd.json
  case "$SPX_RENDER_MODE" in
    default) :;;
    vulkan) export GSK_RENDERER=vulkan;;
    sysmem) export GSK_RENDERER=vulkan TU_DEBUG=sysmem;;
    mesa261) export GSK_RENDERER=vulkan VK_DRIVER_FILES=/opt/spx-mesa261-ab/freedreno_icd.json LD_LIBRARY_PATH=/opt/spx-mesa261-ab;;
    gl) export GSK_RENDERER=gl;;
    noubwc) export GSK_RENDERER=gl FD_MESA_DEBUG=noubwc;;
    software) export GSK_RENDERER=gl LIBGL_ALWAYS_SOFTWARE=1 MESA_LOADER_DRIVER_OVERRIDE=llvmpipe VK_DRIVER_FILES=/usr/share/vulkan/icd.d/lvp_icd.json;;
  esac
  python3 /usr/local/sbin/spx-overnight-vulkan-probe > "$R/$SPX_CASE-vulkan.log" 2>&1
  python3 /usr/local/sbin/spx-overnight-fixture > "$R/$SPX_CASE-app.log" 2>&1 &
  app=$!
fi
for n in $(seq 1 110); do
  test -s "$R/$SPX_CASE-capture.done" && { echo SPX_CASE_CAPTURED; exit 0; }
  kill -0 "$shell" 2>/dev/null || exit 11
  if [ "$app" != 0 ]; then kill -0 "$app" 2>/dev/null || { echo SPX_APP_EXITED; exit 12; }; fi
  sleep 1
done
echo SPX_CASE_TIMEOUT
exit 13

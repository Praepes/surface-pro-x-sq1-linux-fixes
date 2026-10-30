#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-only
# Build against the original prepared Ubuntu SQ1 6.18.3 kernel build tree.
set -euo pipefail
test "$#" = 3 || { echo 'Usage: bash build-ubuntu-touch-backport.sh KERNEL_SOURCE KERNEL_OUTPUT NEW_WORK_DIR'; exit 2; }
src=$(realpath "$1")
out=$(realpath "$2")
work=$(realpath -m "$3")
test -s "$out/Module.symvers"
test ! -e "$work" || { echo 'Use a new work directory'; exit 1; }
mkdir -p "$work/drivers/hid/spi-hid"
python3 - "$work" <<'PY'
import sys,urllib.request,hashlib
from pathlib import Path
root=Path(sys.argv[1])/'drivers/hid/spi-hid'
commit='cfcaa144842c79bd11cc343de38ca5536f8adcee'
hashes={
 'Makefile':'684e2bc8238db1787b99af3163fece1d9a2c45c757082ccd388ff0aa7a2ef9c2',
 'spi-hid-core.c':'7a0103146b0e0f8c27b518dd8b6df1712cb21bbdda9761ac06456245ac37804b',
 'spi-hid-core.h':'d0afbddbe7498df062c4720273475ac3dc0026066bc5138eb39f69b057ec98be',
 'spi-hid_trace.h':'d8f35ee21eb3c7c87d38022a562e64f4e1153cbb0583c3c36fa344cd7e2078fe',
 'trace.c':'9930074e5d1528c56da37f7099e2949d4108f67fdcc13c5bf6df3538e4ef9adf',
}
for name,expected in hashes.items():
    url=f'https://raw.githubusercontent.com/denysvitali/linux-surface/{commit}/drivers/hid/spi-hid/{name}'
    with urllib.request.urlopen(url,timeout=40) as response:data=response.read()
    assert hashlib.sha256(data).hexdigest()==expected,name
    if name=='spi-hid-core.c':data+=b'\nMODULE_VERSION("20261030.cfcaa144.backport1");\n'
    (root/name).write_bytes(data)
PY
cp "$src/drivers/hid/hid-ids.h" "$work/drivers/hid/hid-ids.h"
make -C "$src" O="$out" M="$work/drivers/hid/spi-hid" ARCH=arm64 CROSS_COMPILE="${CROSS_COMPILE:-aarch64-linux-gnu-}" -j4 modules
modinfo "$work/drivers/hid/spi-hid/spi-hid.ko"
# Installation and initramfs changes are deliberately separate; see the notes.

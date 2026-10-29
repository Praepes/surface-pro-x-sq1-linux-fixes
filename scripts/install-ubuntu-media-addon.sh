#!/bin/bash
# Offline codec addon for the locally built Ubuntu 26.04 ARM64 SQ1 preview2.
set -euo pipefail
BASE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
check_only=false
if [[ ${1:-} = --check-only ]]; then check_only=true; shift; fi
[[ $# = 0 ]] || { echo 'Usage: install.sh [--check-only]' >&2; exit 2; }
. /etc/os-release
[[ $ID = ubuntu && $VERSION_ID = 26.04 ]]
[[ $(dpkg --print-architecture) = arm64 ]]
cd "$BASE"
sha256sum --check SHA256SUMS
python3 - "$BASE" <<'PY'
import json,subprocess,sys
from pathlib import Path
base=Path(sys.argv[1]); manifest=json.loads((base/'packages.json').read_text())
assert len(manifest)==56
for row in manifest:
    path=base/'packages'/row['file']
    assert path.name==row['file'] and path.is_file()
    actual=subprocess.check_output(['dpkg-deb','-f',str(path),'Package','Version','Architecture'],text=True).splitlines()
    fields=dict(x.split(': ',1) for x in actual)
    assert fields=={'Package':row['package'],'Version':row['version'],'Architecture':row['architecture']}
    assert row['architecture'] in ['arm64','all']
    p=subprocess.run(['dpkg-query','-W','-f=${db:Status-Status}\t${Version}',row['package']],capture_output=True,text=True)
    if p.returncode==0 and p.stdout.startswith('installed\t'):
        current=p.stdout.split('\t',1)[1]
        assert current==row['version'], 'Different installed version for '+row['package']+'; use normal Ubuntu apt instead'
print('SPX_MEDIA_ADDON_PREFLIGHT_PASSED')
PY
if $check_only; then exit 0; fi
[[ $EUID = 0 ]] || { echo 'Run: sudo ./install.sh' >&2; exit 1; }
install -d -m 755 /var/lib/spx
if [[ ! -e /var/lib/spx/media-addon-packages-before.tsv ]]; then
  dpkg-query -W -f='${Package}\t${Version}\t${db:Status-Status}\n' > /var/lib/spx/media-addon-packages-before.tsv
fi
dpkg -i "$BASE"/packages/*.deb
audit=$(dpkg --audit)
[[ -z $audit ]] || { printf '%s\n' "$audit" >&2; exit 1; }
echo 'Codecs installed. Restart media applications. Hardware decoding remains unverified.'

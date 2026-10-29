#!/usr/bin/env python3
"""Apply the locally tested GTK OpenGL mitigation and a GNOME error-handler fix.

For an Ubuntu ARM64 root filesystem only. This does not replace Mesa or fix
the underlying Vulkan driver. Existing files get a .sq1-before-mitigations backup.
"""
import argparse,hashlib,json
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=Path('/'))
args=parser.parse_args()
root=args.root.resolve()
release=(root/'etc/os-release').read_text()
assert any(line in ['ID=ubuntu','ID="ubuntu"'] for line in release.splitlines()),'Ubuntu root required'
elf=(root/'usr/bin/gnome-shell').read_bytes()[:20]
assert elf[:4]==b'\x7fELF' and int.from_bytes(elf[18:20],'little')==183,'ARM64 GNOME required'
extension=root/'usr/share/gnome-shell/extensions/web-search-provider@ubuntu.com/extension.js'
old='if (error.matches(Gio.IOErrorEnum.CANCELLED))'
new='if (error.matches?.(Gio.IOErrorEnum, Gio.IOErrorEnum.CANCELLED))'
source=extension.read_text()
assert old in source or new in source,'Unexpected extension version; inspect before patching'
changes={}
environment=root/'etc/environment'
existing=environment.read_text() if environment.exists() else ''
lines=[line for line in existing.splitlines() if not line.lstrip().startswith('GSK_RENDERER=')]
changes[environment]='\n'.join(lines+['GSK_RENDERER=gl'])+'\n'
changes[root/'etc/environment.d/90-sq1-gtk-renderer.conf']='# SQ1: avoid the reproduced GTK Vulkan corruption; retain hardware OpenGL.\nGSK_RENDERER=gl\n'
changes[extension]=source.replace(old,new)
record=[]
for p,content in changes.items():
    before=p.read_text() if p.exists() else None
    if before==content:continue
    p.parent.mkdir(parents=True,exist_ok=True)
    backup=p.with_name(p.name+'.sq1-before-mitigations')
    if before is not None and not backup.exists():backup.write_text(before)
    p.write_text(content)
    record.append({'path':'/'+str(p.relative_to(root)),'backup':'/'+str(backup.relative_to(root)) if before is not None else None,'sha256':hashlib.sha256(content.encode()).hexdigest()})
print(json.dumps({'changes':record,'note':'Re-login required. Vulkan driver root cause is not repaired.'},indent=2))

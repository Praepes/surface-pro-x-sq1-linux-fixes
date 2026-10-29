"""Audit the actual preview2 image while its backing block device is read-only."""
from pathlib import Path
import json,re,subprocess,sys,hashlib
root=Path(sys.argv[1]);loop=sys.argv[2];checks=[]
assert subprocess.check_output(['blockdev','--getro',loop],text=True).strip()=='1','Read-only backing block device required'
def check(name,condition,**data):
    checks.append(dict(name=name,passed=bool(condition),**data))
def read(p):return (root/p.lstrip('/')).read_text()
uuid=subprocess.check_output(['blkid','-s','UUID','-o','value',loop+'p2'],text=True).strip()
configured=read('/etc/spx/root-uuid').strip()
fstab=read('/etc/fstab')
menus=[read('/boot/grub/grub.cfg'),read('/etc/spx/grub-menu.cfg'),read('/boot/efi/EFI/BOOT/grub.cfg')]
check('root_uuid_consistency',configured==uuid and any(line.startswith('UUID='+uuid) and line.split()[1]=='/' for line in fstab.splitlines()))
check('boot_menu_copies_equal',len(set(menus))==1)
menu=menus[0]
paths=re.findall(r'^\s*(?:linux|initrd|devicetree)\s+(/\S+)',menu,re.M)
check('boot_references_present',all((root/p.lstrip('/')).is_file() for p in paths),count=len(paths))
check('all_kernel_entries_use_root_uuid',all('root=UUID='+uuid in line for line in menu.splitlines() if line.lstrip().startswith('linux ')))
check('all_kernel_entries_specify_device_tree',menu.count('\n    devicetree ')==4)
efi=(root/'boot/efi/EFI/BOOT/BOOTAA64.EFI').read_bytes()
check('removable_efi_header',efi[:2]==b'MZ' and len(efi)>100000,size=len(efi))
for path in sorted(set(p for p in paths if '/dtb/' in p)):
    raw=(root/path.lstrip('/')).read_bytes()
    check('dtb_header:'+path,raw[:4]==bytes.fromhex('d00dfeed'),sha256=hashlib.sha256(raw).hexdigest())
k='6.18.3-sq1-ubuntu1'
config=dict(re.findall(r'^(CONFIG_\w+)=(.*)$',read('/boot/config-'+k),re.M))
for key in ['CONFIG_EFI_STUB','CONFIG_DEVTMPFS','CONFIG_EXT4_FS','CONFIG_USB_XHCI_HCD','CONFIG_USB_STORAGE','CONFIG_USB_DWC3','CONFIG_DRM_MSM','CONFIG_SECURITY_APPARMOR','CONFIG_SQUASHFS_ZSTD']:
    check('kernel_config:'+key,config.get(key) in ['y','m'],value=config.get(key))
files=subprocess.check_output(['timeout','-k','5','60','chroot',str(root),'/usr/bin/env','TMPDIR=/run/spx-0530','lsinitramfs','/boot/initrd.img-'+k],text=True).splitlines()
for needle in ['dispcc-sm8250.ko','msm.ko','firmware/updates/qcom/msft/surface/pro-x-sq2']:
    check('initramfs_contains:'+needle,any(needle in x for x in files))
check('matching_custom_module_tree',any('/'+k+'/' in '/'+x for x in files) and (root/'usr/lib/modules'/k/'modules.dep').is_file())
check('gtk_gl_environment',all('GSK_RENDERER=gl' in read(p).splitlines() for p in ['/etc/environment','/etc/environment.d/90-sq1-gtk-renderer.conf']))
check('extension_error_domain','error.matches?.(Gio.IOErrorEnum, Gio.IOErrorEnum.CANCELLED)' in read('/usr/share/gnome-shell/extensions/web-search-provider@ubuntu.com/extension.js'))
for unit in ['sleep.target','suspend.target','hibernate.target','hybrid-sleep.target','suspend-then-hibernate.target']:
    p=root/'etc/systemd/system'/unit
    check('sleep_guard:'+unit,p.is_symlink() and p.readlink()==Path('/dev/null'))
for unit in ['spx-grow-root.service','spx-hwdb-refresh.service','spx-ssh-hostkeys.service','spx-touch-discover.service']:
    check('enabled:'+unit,(root/'etc/systemd/system/multi-user.target.wants'/unit).is_symlink())
check('machine_id_unset',not (root/'etc/machine-id').read_bytes())
check('no_host_ssh_keys',not list((root/'etc/ssh').glob('ssh_host_*_key')))
check('no_wifi_connections',not list((root/'etc/NetworkManager/system-connections').glob('*')))
check('no_build_service_blocker',not (root/'usr/sbin/policy-rc.d').exists())
check('deferred_build_wrappers_restored',not list((root/'usr/bin').glob('*.spx-real')) and not list((root/'usr/sbin').glob('*.spx-real')))
print(json.dumps({'scope':'Actual preview2 read-only image: static consistency only; no boot acceptance','checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks)},indent=2))
if any(not x['passed'] for x in checks):sys.exit(1)

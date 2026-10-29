"""Bounded native graphics A/B suite. Runs as root on the SQ1; all writes in RAM."""
from pathlib import Path
import os,subprocess as S,time,json,signal,shutil

T=Path('/run/spx-ubuntu-native-test'); R=T/'results'
assert S.check_output(['findmnt','-n','-o','FSTYPE','--mountpoint',str(T)],text=True).strip()=='tmpfs'
assert S.check_output(['findmnt','-n','-o','FSTYPE','--mountpoint',str(T/'root')],text=True).strip()=='overlay'
R.mkdir(exist_ok=True); os.chown(R,1000,1000)
for stem in ['fixture.py','vulkan-probe.py','automation.js','inner.sh','scale.py']:
    shutil.copyfile(T/'uploads'/('overnight-'+stem),T/'root/usr/local/sbin'/('spx-overnight-'+stem.removesuffix('.py') if stem.endswith('.py') else 'spx-overnight-'+stem))

def temps():
    values=[]
    for p in Path('/sys/class/thermal').glob('thermal_zone*/temp'):
        try: values.append(int(p.read_text()))
        except (ValueError,OSError): pass
    return max(values,default=0)/1000

records=[]
plan=[]
scale=os.getenv('SPX_SCALE','1')
custom=os.getenv('SPX_PLAN','')
for repeat in range(1,int(os.getenv('SPX_REPEATS','3'))+1):
    if custom:
        for item in custom.split(','):
            client,mode=item.split(':'); plan.append((client,mode,repeat))
    else:
        for mode in ['default','vulkan','sysmem','gl','software']:
            for client in ['ubuntu','arch']:
                plan.append((client,mode,repeat))
if os.getenv('SPX_SMOKE')=='1': plan=[('ubuntu','vulkan',0),('arch','vulkan',0)]
for client,mode,repeat in plan:
    if temps()>75: print('SPX_THERMAL_ABORT',flush=True); break
    mem=dict((line.split(':')[0],line.split(':')[1].strip()) for line in Path('/proc/meminfo').read_text().splitlines())
    if int(mem['MemAvailable'].split()[0])<2500000: print('SPX_LOW_MEMORY_ABORT',flush=True); break
    name=f'{client}-{mode}-r{repeat:02d}'
    if scale!='1':name+='-s'+scale
    if os.getenv('SPX_TAG'):name+='-'+os.environ['SPX_TAG']
    runtime=T/f'runtime-{name}'; runtime.mkdir(mode=0o700,exist_ok=True); os.chown(runtime,1000,1000)
    home=T/'arch-home'; home.mkdir(exist_ok=True); os.chown(home,1000,1000)
    for p in R.glob(name+'-*'): p.unlink()
    argv=['systemd-nspawn','--quiet','--directory='+str(T/'root'),'--machine=spx-overnight','--register=no','--private-network','--resolv-conf=off','--bind=/dev/dri/renderD128','--bind='+str(R)+':/home/surface/native-test-results','--bind='+str(runtime)+':/run/user/1000','--setenv=XDG_RUNTIME_DIR=/run/user/1000','--setenv=SPX_CASE='+name,'--setenv=SPX_CLIENT='+client,'--setenv=SPX_RENDER_MODE='+mode,
          '/bin/bash','-c','mkdir -p /run/dbus /var/lib/dbus; if [ ! -s /etc/machine-id ]; then dbus-uuidgen > /etc/machine-id; fi; dbus-daemon --system --fork --nopidfile; exec timeout -k 5 130 setpriv --reuid=1000 --regid=1000 --clear-groups env HOME=/home/surface dbus-run-session -- bash /usr/local/sbin/spx-overnight-inner.sh']
    argv.insert(argv.index('/bin/bash'),'--setenv=SPX_SCALE='+scale)
    start=time.time(); app=None
    print('SPX_CASE_BEGIN',name,flush=True)
    with (R/f'{name}-container.log').open('w') as log:
        proc=S.Popen(argv,stdout=log,stderr=S.STDOUT,start_new_session=True)
        try:
            if client=='arch':
                for n in range(120):
                    if (R/f'{name}-shell.ready').exists() and (runtime/'wayland-0').exists(): break
                    if proc.poll() is not None: break
                    time.sleep(.5)
                if proc.poll() is None and (runtime/'wayland-0').exists():
                    env={'PATH':'/usr/bin','HOME':str(home),'XDG_RUNTIME_DIR':str(runtime),'XDG_CACHE_HOME':str(home/'cache'),'XDG_CONFIG_HOME':str(home/'config'),'XDG_DATA_HOME':str(home/'data'),'WAYLAND_DISPLAY':'wayland-0','GDK_BACKEND':'wayland','GSETTINGS_BACKEND':'memory','GIO_USE_VFS':'local','GTK_USE_PORTAL':'0','LC_ALL':'C.UTF-8','SPX_CASE':name,'SPX_RESULTS':str(R),'VK_DRIVER_FILES':'/usr/share/vulkan/icd.d/freedreno_icd.json'}
                    if mode in ['vulkan','sysmem']: env['GSK_RENDERER']='vulkan'
                    if mode=='sysmem': env['TU_DEBUG']='sysmem'
                    if mode=='gl': env['GSK_RENDERER']='gl'
                    if mode=='software': env.update(GSK_RENDERER='gl',LIBGL_ALWAYS_SOFTWARE='1',MESA_LOADER_DRIVER_OVERRIDE='llvmpipe')
                    with (R/f'{name}-vulkan.log').open('w') as v:
                        S.run(['setpriv','--reuid=1000','--regid=1000','--clear-groups','python3',str(T/'uploads/overnight-vulkan-probe.py')],env=env,stdout=v,stderr=S.STDOUT,timeout=12)
                    app_log=(R/f'{name}-app.log').open('w')
                    app=S.Popen(['setpriv','--reuid=1000','--regid=1000','--clear-groups','dbus-run-session','--','python3',str(T/'uploads/overnight-fixture.py')],env=env,stdout=app_log,stderr=S.STDOUT,start_new_session=True)
            rc=proc.wait(timeout=145)
        except Exception as e:
            print('SPX_CASE_EXCEPTION',repr(e),flush=True); rc=-1
        finally:
            if app and app.poll() is None:
                os.killpg(app.pid,signal.SIGTERM)
                try: app.wait(timeout=8)
                except S.TimeoutExpired: os.killpg(app.pid,signal.SIGKILL); app.wait()
            if proc.poll() is None:
                os.killpg(proc.pid,signal.SIGTERM)
                try: proc.wait(timeout=10)
                except S.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL); proc.wait()
    record={'case':name,'client':client,'mode':mode,'repeat':repeat,'returncode':rc,'elapsed':round(time.time()-start,2),'max_thermal_c':temps(),'capture_complete':(R/f'{name}-capture.done').exists()}
    records.append(record); (R/'suite-summary.json').write_text(json.dumps(records,indent=2))
    print('SPX_CASE_END',json.dumps(record),flush=True)
print('SPX_OVERNIGHT_SUITE_DONE',flush=True)

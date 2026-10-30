"""Isolated Firefox GUI probe using Mozilla's loopback-only Marionette protocol."""
import os,sys,time,json,socket,subprocess,tempfile,pathlib,shutil,signal,urllib.parse,statistics
with socket.socket() as port_check:
    port_check.settimeout(.3)
    if port_check.connect_ex(('127.0.0.1',2829))==0:
        raise SystemExit('Port 2829 is already in use; no browser started')
base=pathlib.Path.home()/'snap/firefox/common'
base.mkdir(parents=True,exist_ok=True)
profile=pathlib.Path(tempfile.mkdtemp(prefix='spx-startup-probe-',dir=base))
prefs={'marionette.port':2829,'browser.shell.checkDefaultBrowser':False,'browser.startup.homepage_override.mstone':'ignore','browser.startup.page':0,'browser.startup.homepage':'about:blank','browser.aboutwelcome.enabled':False,'datareporting.policy.dataSubmissionEnabled':False,'toolkit.telemetry.reportingpolicy.firstRun':False,'browser.newtabpage.enabled':False}
(profile/'user.js').write_text('\n'.join('user_pref(%s, %s);'%(json.dumps(k),json.dumps(v)) for k,v in prefs.items()))

class Client:
    def __init__(self,sock):self.sock=sock;self.seq=0;self.recv()
    def recv(self):
        size=b''
        while True:
            ch=self.sock.recv(1)
            if not ch:raise EOFError('Marionette closed')
            if ch==b':':break
            size+=ch
        data=b''
        while len(data)<int(size):
            part=self.sock.recv(int(size)-len(data))
            if not part:raise EOFError('Marionette frame incomplete')
            data+=part
        return json.loads(data)
    def call(self,name,params=None):
        self.seq+=1
        data=json.dumps([0,self.seq,name,params or {}]).encode()
        self.sock.sendall(str(len(data)).encode()+b':'+data)
        response=self.recv()
        if response[2]:raise RuntimeError(response[2])
        return response[3]

page='<!doctype html><meta charset="utf-8"><title>SQ1 Firefox 启动测试（自动关闭）</title><style>body{font:20px sans-serif;background:#eff4fb}article{margin:12px;padding:10px;border-radius:14px;background:white;box-shadow:0 2px 6px #aaa}</style><h1>Surface Pro X SQ1</h1>'+''.join('<article>本地测试页面 %s — browser initialization and rendering</article>'%n for n in range(24))
try:
    cpu_ab='--cpu-ab' in sys.argv
    original_affinity=os.sched_getaffinity(0)
    variants=[None,{4,5,6,7},{4,5,6,7},None] if cpu_ab else [None]*int(os.environ.get('SPX_PROBE_RUNS','2'))
    for run,affinity in enumerate(variants):
        os.sched_setaffinity(0,affinity or original_affinity)
        log=open('/tmp/spx-firefox-probe-%s.log'%run,'w')
        env=dict(os.environ,MOZ_ENABLE_WAYLAND='1',MOZ_REMOTE_ALLOW_SYSTEM_ACCESS='1')
        before=time.monotonic()
        binary=os.environ.get('SPX_FIREFOX_BINARY','firefox')
        proc=subprocess.Popen([binary,'--no-remote','--new-instance','--marionette','--remote-allow-system-access','--profile',str(profile),'about:blank'],env=env,stdout=log,stderr=log,start_new_session=True)
        client=None
        row={'run':run+1,'affinity':sorted(os.sched_getaffinity(0)),'scope':'isolated automated visible profile, first/warm launch; not user profile or cold boot'}
        cpus=set()
        try:
            deadline=before+35
            while time.monotonic()<deadline:
                try:
                    sock=socket.create_connection(('127.0.0.1',2829),.25);sock.settimeout(25)
                    client=Client(sock);break
                except (ConnectionRefusedError,TimeoutError):
                    if proc.poll() is not None:raise RuntimeError('Firefox exited '+str(proc.returncode))
                    time.sleep(.1)
            if not client:raise TimeoutError('Marionette not ready')
            row['automation_ready_seconds']=round(time.monotonic()-before,3)
            client.call('WebDriver:NewSession',{'capabilities':{'alwaysMatch':{}}})
            row['session_ready_seconds']=round(time.monotonic()-before,3)
            if cpu_ab:
                print(json.dumps(row,ensure_ascii=False),flush=True)
                client.call('Marionette:Quit',{'flags':['eAttemptQuit']})
                continue
            client.call('Marionette:SetContext',{'value':'chrome'})
            row['graphics']=client.call('WebDriver:ExecuteAsyncScript',{'script':"const done=arguments[arguments.length-1]; ChromeUtils.importESModule('resource://gre/modules/Troubleshoot.sys.mjs').Troubleshoot.snapshot().then(s=>done(s.graphics));",'args':[],'newSandbox':True,'sandbox':'default'})
            client.call('Marionette:SetContext',{'value':'content'})
            nav=time.monotonic()
            client.call('WebDriver:Navigate',{'url':'data:text/html;charset=utf-8,'+urllib.parse.quote(page)})
            row['local_navigation_seconds']=round(time.monotonic()-nav,3)
            row['content']=client.call('WebDriver:ExecuteAsyncScript',{'script':"const done=arguments[arguments.length-1]; let times=[],ended=false; function finish(reason){if(ended)return;ended=true;let gaps=times.slice(1).map((t,i)=>t-times[i]); let c=document.createElement('canvas');let gl=c.getContext('webgl');let ext=gl&&gl.getExtension('WEBGL_debug_renderer_info');done({reason,visibility:document.visibilityState,frameIntervals:gaps,paints:performance.getEntriesByType('paint').map(x=>({name:x.name,start:x.startTime})),webglRenderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):null,webglVendor:ext?gl.getParameter(ext.UNMASKED_VENDOR_WEBGL):null});} function frame(t){if(ended)return;times.push(t); if(times.length<121){requestAnimationFrame(frame);return;}finish('121 frames');} setTimeout(()=>finish('bounded 8s deadline'),8000);requestAnimationFrame(frame);",'args':[],'newSandbox':True,'sandbox':'default'})
            for p in pathlib.Path('/proc').iterdir():
                if not p.name.isdigit():continue
                try:
                    if os.getpgid(int(p.name))!=proc.pid:continue
                    status=(p/'status').read_text()
                    if 'firefox' in status or 'Web Content' in status:
                        row.setdefault('cpu_affinities',[]).append(next(x for x in status.splitlines() if x.startswith('Cpus_allowed_list:')))
                except (ProcessLookupError,PermissionError,FileNotFoundError):pass
            print(json.dumps(row,ensure_ascii=False),flush=True)
            client.call('Marionette:Quit',{'flags':['eAttemptQuit']})
        except Exception as e:
            row['error']=str(e);print(json.dumps(row,ensure_ascii=False),flush=True)
        finally:
            if client:client.sock.close()
            try:proc.wait(timeout=7)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=4)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            log.close()
finally:
    assert profile.parent==base and profile.name.startswith('spx-startup-probe-')
    shutil.rmtree(profile)

"""Bounded, visible GTK test; does not represent every application or browser."""
import os,sys,time,json,subprocess

if '--child' not in sys.argv:
    rows=[]
    for n in range(3):
        env=dict(os.environ,SPX_PROBE_START_NS=str(time.monotonic_ns()))
        result=subprocess.run([sys.executable,__file__,'--child'],env=env,text=True,capture_output=True,timeout=12)
        print(json.dumps({'run':n+1,'exit':result.returncode,'output':result.stdout.strip(),'stderr':result.stderr.strip()},ensure_ascii=False),flush=True)
    raise SystemExit()

start=int(os.environ['SPX_PROBE_START_NS'])/1e9
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,GLib
import_done=time.monotonic()
app=Gtk.Application(application_id='org.surface.SQ1StartupProbe')
result={'scope':'bounded GTK GL window, no cache drop; not browser benchmark', 'import_ms':round((import_done-start)*1000,2)}
state={'first':True,'page_pending':False}

def activate(app):
    window=Gtk.ApplicationWindow(application=app,title='SQ1 启动测试（自动关闭）')
    window.set_default_size(680,460)
    stack=Gtk.Stack()
    for page in range(2):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=3)
        box.append(Gtk.Label(label=f'测试页面 {page+1}'))
        for row in range(14):
            line=Gtk.Box(spacing=8)
            line.append(Gtk.Label(label=f'图形初始化测试 {row:02d} — Surface Pro X SQ1'))
            line.append(Gtk.Button(label=f'按钮 {row+1}'))
            box.append(line)
        stack.add_named(box,str(page))
    window.set_child(stack)
    def finish():
        result['renderer']=window.get_renderer().__gtype__.name
        print(json.dumps(result,ensure_ascii=False),flush=True)
        window.close();app.quit();return False
    def page_change():
        state['page_started']=time.monotonic()
        state['page_pending']=True
        stack.set_visible_child_name('1')
        return False
    def paint(clock):
        now=time.monotonic()
        if state['first']:
            state['first']=False
            result['first_after_paint_ms']=round((now-start)*1000,2)
            GLib.timeout_add(500,page_change)
        elif state['page_pending']:
            state['page_pending']=False
            result['page_after_paint_ms']=round((now-state['page_started'])*1000,2)
    def mapped(widget):
        result['mapped_ms']=round((time.monotonic()-start)*1000,2)
        widget.get_frame_clock().connect('after-paint',paint)
    window.connect('map',mapped)
    window.present()
    GLib.timeout_add(1700,finish)

app.connect('activate',activate)
app.run(None)

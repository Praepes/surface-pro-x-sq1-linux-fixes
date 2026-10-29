"""Deterministic private-display GTK workload; no host input or personal data."""
import os, json, math, time
from pathlib import Path
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk, Gdk, GLib

root=Path(os.environ['SPX_RESULTS'])
prefix=os.environ['SPX_CASE']
def mark(stage,**kw):
    value={'stage':stage,'time':time.time(),'gtk':f'{Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}',**kw}
    (root/f'{prefix}-status.json').write_text(json.dumps(value))
    print('SPX_FIXTURE '+json.dumps(value),flush=True)

class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='org.example.SQ1PrivateGraphicsTest')
        self.connect('activate',self.activate)
        self.tick=0
    def activate(self,app):
        self.win=Gtk.ApplicationWindow(application=self)
        self.win.set_title('SQ1 synthetic graphics test')
        self.win.set_default_size(1050,820)
        self.win.fullscreen()
        outer=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12)
        outer.set_margin_top(18); outer.set_margin_bottom(18)
        outer.set_margin_start(18); outer.set_margin_end(18)
        title=Gtk.Label(label='SQ1 Ubuntu / Arch GTK rendering validation — 中文测试 0123456789')
        title.add_css_class('title-1'); outer.append(title)
        self.entry=Gtk.Entry(); self.entry.set_text('Text, glyphs, gradients, scrolling and damage updates'); outer.append(self.entry)
        self.progress=Gtk.ProgressBar(); self.progress.set_fraction(.625); outer.append(self.progress)
        self.scroll=Gtk.ScrolledWindow(); self.scroll.set_vexpand(True)
        rows=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        for n in range(96):
            row=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=12)
            row.add_css_class('card'); row.set_size_request(-1,52)
            label=Gtk.Label(label=f'{n:03d}  Surface Pro X SQ1  ──  GTK texture & glyph test  中文渲染')
            label.set_hexpand(True); label.set_xalign(0)
            row.append(label)
            button=Gtk.Button(label=f'Button {n%10}'); row.append(button)
            switch=Gtk.Switch(); switch.set_active(n%2==0); row.append(switch)
            rows.append(row)
        self.scroll.set_child(rows); outer.append(self.scroll)
        self.win.set_child(outer)
        css=Gtk.CssProvider()
        css.load_from_data(b'.card { background-image: linear-gradient(110deg, #f2f6fa, #b7cee5); color: #142d48; border-radius: 9px; padding: 9px; }')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.win.present()
        GLib.timeout_add(2500,self.static_ready)
    def static_ready(self):
        mark('static-ready',renderer=self.win.get_renderer().__gtype__.name,scale=self.win.get_scale_factor(),width=self.win.get_width(),height=self.win.get_height()); GLib.timeout_add(4000,self.start_stress); return False
    def start_stress(self):
        self.t0=time.monotonic(); GLib.timeout_add(35,self.stress); return False
    def stress(self):
        self.tick+=1
        a=self.scroll.get_vadjustment()
        span=max(0,a.get_upper()-a.get_page_size())
        a.set_value(span*(.5+.5*math.sin(self.tick*.19)))
        self.entry.set_text(f'Frame {self.tick:04d}  中文 glyph damage  ΑΒΓ 0123456789')
        self.progress.set_fraction((self.tick%100)/100)
        if time.monotonic()-self.t0<8: return True
        a.set_value(820)
        self.entry.set_text('Final stable frame — rendering verification 中文 0123456789')
        self.progress.set_fraction(.625)
        GLib.timeout_add(1500,self.stress_ready)
        return False
    def stress_ready(self):
        mark('stress-ready',updates=self.tick,renderer=self.win.get_renderer().__gtype__.name,scale=self.win.get_scale_factor())
        return False

mark('starting',renderer_request=os.getenv('GSK_RENDERER','default'),tu_debug=os.getenv('TU_DEBUG',''))
App().run([])

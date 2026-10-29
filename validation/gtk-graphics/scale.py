import os,time,json,gi
from gi.repository import Gio,GLib
scale=float(os.getenv('SPX_SCALE','1'))
if scale==1: raise SystemExit(0)
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
name='org.gnome.Mutter.DisplayConfig'; path='/org/gnome/Mutter/DisplayConfig'
for i in range(30):
    try:
        state=bus.call_sync(name,path,name,'GetCurrentState',None,None,Gio.DBusCallFlags.NONE,2000,None).unpack()
        break
    except GLib.Error:time.sleep(.2)
serial,monitors,logical,props=state
connector=monitors[0][0][0]; mode=monitors[0][1][0][0]
args=GLib.Variant('(uua(iiduba(ssa{sv}))a{sv})',(serial,1,[(0,0,scale,0,True,[(connector,mode,{})])],{}))
bus.call_sync(name,path,name,'ApplyMonitorsConfig',args,None,Gio.DBusCallFlags.NONE,5000,None)
state=bus.call_sync(name,path,name,'GetCurrentState',None,None,Gio.DBusCallFlags.NONE,2000,None).unpack()
print('SPX_MONITOR_SCALE '+repr(state[2]),flush=True)
assert state[2][0][2]==scale

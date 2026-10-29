"""Read-only Vulkan device enumeration; never treats lavapipe as GPU acceleration."""
import ctypes as C,json
P=C.c_void_p; U=C.c_uint32
class App(C.Structure):
    _fields_=[('sType',U),('pNext',P),('pApplicationName',C.c_char_p),('applicationVersion',U),('pEngineName',C.c_char_p),('engineVersion',U),('apiVersion',U)]
class Info(C.Structure):
    _fields_=[('sType',U),('pNext',P),('flags',U),('pApplicationInfo',C.POINTER(App)),('enabledLayerCount',U),('ppEnabledLayerNames',P),('enabledExtensionCount',U),('ppEnabledExtensionNames',P)]
v=C.CDLL('libvulkan.so.1')
v.vkCreateInstance.argtypes=[C.POINTER(Info),P,C.POINTER(P)]; v.vkCreateInstance.restype=C.c_int
v.vkEnumeratePhysicalDevices.argtypes=[P,C.POINTER(U),C.POINTER(P)]; v.vkEnumeratePhysicalDevices.restype=C.c_int
v.vkGetPhysicalDeviceProperties.argtypes=[P,P]
v.vkDestroyInstance.argtypes=[P,P]
app=App(0,None,b'SQ1 read-only Vulkan enumeration',0,None,0,(1<<22)|(1<<12))
info=Info(1,None,0,C.pointer(app),0,None,0,None); inst=P()
result=v.vkCreateInstance(C.byref(info),None,C.byref(inst))
assert result==0,f'vkCreateInstance {result}'
try:
    n=U(); assert v.vkEnumeratePhysicalDevices(inst,C.byref(n),None)==0
    devices=(P*n.value)(); assert v.vkEnumeratePhysicalDevices(inst,C.byref(n),devices)==0
    items=[]
    for d in devices:
        buf=C.create_string_buffer(4096); v.vkGetPhysicalDeviceProperties(d,buf)
        data=buf.raw
        items.append({'name':data[20:276].split(b'\0')[0].decode(),'vendor_id':int.from_bytes(data[8:12],'little'),'device_id':int.from_bytes(data[12:16],'little'),'type':int.from_bytes(data[16:20],'little')})
    print('SPX_VULKAN_DEVICES '+json.dumps(items),flush=True)
    assert items, 'No Vulkan devices'
finally:v.vkDestroyInstance(inst,None)

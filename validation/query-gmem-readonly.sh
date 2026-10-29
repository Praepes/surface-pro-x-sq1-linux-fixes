set -eu
python3 - <<'PY'
import os,fcntl,struct,json
fd=os.open('/dev/dri/renderD128',os.O_RDONLY|os.O_CLOEXEC)
try:
    result={}
    # drm_msm_param is 24 bytes; DRM_COMMAND_BASE=0x40, GET_PARAM=0.
    request=(3<<30)|(24<<16)|(ord('d')<<8)|0x40
    for name,param in [('gpu_id',1),('gmem_size',2),('gmem_base',6),('gpu_fault_counter',9)]:
        b=bytearray(struct.pack('IIQII',0x10,param,0,0,0))
        fcntl.ioctl(fd,request,b,True)
        result[name]=struct.unpack('IIQII',b)[2]
    result['gmem_base_aligned_to_size']=result['gmem_base']%result['gmem_size']==0
    print('SPX_GMEM_READONLY '+json.dumps(result))
finally:os.close(fd)
PY

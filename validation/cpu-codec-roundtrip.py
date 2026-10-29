"""Bounded CPU codec correctness tests; ARM64 userspace under QEMU user mode."""
from pathlib import Path
import json,math,struct,time,traceback,os
import gi
gi.require_version('Gst','1.0')
from gi.repository import Gst
Gst.init(None)
results=[]
out=Path('/run/spx-0530')
filter_names=os.getenv('SPX_CODEC_FILTER','').split(',')
result_name=os.getenv('SPX_RESULT_NAME','media-results.json')

def record(name,status,**info):
    row=dict(name=name,status=status,**info);results.append(row)
    (out/result_name).write_text(json.dumps(results,indent=2))
    print('SPX_CODEC_RESULT '+json.dumps(row),flush=True)

def run(name,plugins,pipeline,check):
    if filter_names!=[''] and not any(name.startswith(x) for x in filter_names):return
    missing=[p for p in plugins if not Gst.ElementFactory.find(p)]
    if missing:
        record(name,'unavailable',missing_plugins=missing);return
    p=None;start=time.monotonic()
    try:
        p=Gst.parse_launch(pipeline)
        sink=p.get_by_name('sink');assert sink
        assert p.set_state(Gst.State.PLAYING)!=Gst.StateChangeReturn.FAILURE
        bus=p.get_bus();buffers=[];caps=None;deadline=start+65
        while time.monotonic()<deadline:
            sample=sink.emit('try-pull-sample',Gst.SECOND)
            if sample:
                caps=sample.get_caps().to_string()
                b=sample.get_buffer();buffers.append(b.extract_dup(0,b.get_size()))
            msg=bus.pop_filtered(Gst.MessageType.ERROR)
            if msg:
                err,debug=msg.parse_error();raise RuntimeError(str(err)+' '+str(debug))
            if sink.get_property('eos'): break
        assert sink.get_property('eos'),'No EOS within 65-second case budget'
        details=check(buffers)
        record(name,'pass',elapsed_seconds=round(time.monotonic()-start,2),buffers=len(buffers),caps=caps,**details)
    except Exception as e: record(name,'fail',error=str(e),traceback=traceback.format_exc()[-1800:])
    finally:
        if p:p.set_state(Gst.State.NULL)

def audio_check(buffers):
    data=b''.join(buffers);assert len(data)%4==0
    samples=struct.unpack('<'+'f'*(len(data)//4),data)
    assert 8000<=len(samples)<=12000,(len(samples),'unexpected decoded sample count')
    assert all(math.isfinite(x) for x in samples)
    rms=math.sqrt(sum(x*x for x in samples)/len(samples))
    crossings=sum(a<=0<b for a,b in zip(samples,samples[1:]))
    freq=crossings*48000/len(samples)
    assert .45<rms<.65,(rms,'unexpected RMS')
    assert abs(freq-440)<30,(freq,'unexpected frequency')
    return {'samples':len(samples),'rms':round(rms,4),'estimated_frequency_hz':round(freq,2)}

for name,plugins,chain in [
    ('flac',['flacenc','flacdec'],'flacenc ! flacdec'),
    ('opus',['opusenc','opusdec'],'opusenc ! opusdec'),
    ('vorbis',['vorbisenc','vorbisdec'],'vorbisenc ! vorbisdec'),
    ('wav',['wavenc','wavparse'],'wavenc ! wavparse')]:
    run('audio-'+name,plugins,
        'audiotestsrc wave=sine freq=440 volume=0.8 samplesperbuffer=480 num-buffers=20 ! '
        'audioconvert ! audio/x-raw,format='+('F32LE' if name=='vorbis' else 'S16LE')+',rate=48000,channels=1 ! '+chain+
        ' ! audioconvert ! audio/x-raw,format=F32LE,rate=48000,channels=1 ! appsink name=sink sync=false',audio_check)

def video_check(buffers,expected):
    assert len(buffers)==12,(len(buffers),'unexpected decoded frame count')
    maxerr=0
    for data in buffers:
        assert len(data)==64*48*3,len(data)
        for i in [0,((48//2)*64+32)*3,len(data)-3]:
            maxerr=max(maxerr,max(abs(a-b) for a,b in zip(data[i:i+3],expected)))
    assert maxerr<=6,(maxerr,'solid-color reconstruction mismatch')
    return {'frames':len(buffers),'checked_positions_per_frame':3,'maximum_channel_error':maxerr}

for name,plugins,chain in [
    ('vp8',['vp8enc','vp8dec'],'vp8enc deadline=1 ! vp8dec'),
    ('vp9',['vp9enc','vp9dec'],'vp9enc deadline=1 ! vp9dec'),
    ('h264',['x264enc','avdec_h264'],'x264enc tune=zerolatency speed-preset=ultrafast ! avdec_h264'),
    ('h264-mp4',['x264enc','mp4mux','qtdemux','avdec_h264'],'x264enc tune=zerolatency speed-preset=ultrafast ! mp4mux ! qtdemux ! avdec_h264'),
    ('theora',['theoraenc','theoradec'],'theoraenc ! theoradec')]:
    for color,rgb in [('black',(0,0,0)),('white',(255,255,255)),('red',(255,0,0))]:
        run('video-'+name+'-'+color,plugins,
            'videotestsrc pattern='+color+' num-buffers=12 ! '
            'video/x-raw,format=I420,width=64,height=48,framerate=10/1,colorimetry=bt601 ! '+chain+
            ' ! videoconvert ! video/x-raw,format=RGB ! appsink name=sink sync=false',
            lambda b,e=rgb:video_check(b,e))

print('SPX_CPU_MEDIA_COMPLETE '+json.dumps({'cases':len(results),'passed':sum(x['status']=='pass' for x in results),'failed':sum(x['status']=='fail' for x in results),'unavailable':sum(x['status']=='unavailable' for x in results),'scope':'QEMU user-mode CPU codec test only; no hardware codec/audio/display acceptance'}),flush=True)

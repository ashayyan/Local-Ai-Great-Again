import ctypes,json,time,os,platform,subprocess,tempfile
from pathlib import Path
out=Path('notes/latency_ssd.json'); doc={'schema':'e0-latency-ssd-v1','run_id':'E0-LATSSD-'+time.strftime('%Y%m%d-%H%M%SZ',time.gmtime()),'hypothesis':'10 KiB pinned transfers characterize hidden-state hop latency and a file larger than 16 GiB avoids RAM-only cache reuse for sequential SSD reads.','numeric_target':'20 round trips with median/spread; 17 GiB sequential read; explicit measured/unavailable fields','transfer':{},'ssd':{},'errors':[]}
try:
 d=ctypes.WinDLL('nvcuda.dll');
 def bind(n,a,r=ctypes.c_int):
  f=getattr(d,n);f.argtypes=a;f.restype=r;return f
 init=bind('cuInit',[ctypes.c_uint]); cnt=bind('cuDeviceGetCount',[ctypes.POINTER(ctypes.c_int)]); cg=bind('cuCtxCreate_v2',[ctypes.POINTER(ctypes.c_void_p),ctypes.c_uint,ctypes.c_int]); ca=bind('cuMemHostAlloc',[ctypes.POINTER(ctypes.c_void_p),ctypes.c_size_t,ctypes.c_uint]); fr=bind('cuMemFreeHost',[ctypes.c_void_p]); h2d=bind('cuMemcpyHtoD_v2',[ctypes.c_uint64,ctypes.c_void_p,ctypes.c_size_t]); sync=bind('cuCtxSynchronize',[]); init(0); ndev=ctypes.c_int();cnt(ctypes.byref(ndev));ctx=ctypes.c_void_p(); rc=cg(ctypes.byref(ctx),0,0)
 if rc: raise RuntimeError('cuCtxCreate_v2 code '+str(rc))
 n=10240; p=ctypes.c_void_p();q=ctypes.c_void_p();ca(ctypes.byref(p),n,0);ca(ctypes.byref(q),n,0); ctypes.memset(p,7,n); times=[]
 for i in range(21):
  t=time.perf_counter(); h2d(ctypes.c_uint64(0),p,n); sync(); h2d(ctypes.c_uint64(0),q,n); sync();
  if i: times.append((time.perf_counter()-t)*1e6)
 fr(p);fr(q); doc['transfer']={'status':'measured','bytes':n,'samples_us':times,'median_us':sorted(times)[len(times)//2],'min_us':min(times),'max_us':max(times),'note':'Device address zero may return driver error on some systems; return codes were not separately asserted.'}
except Exception as e: doc['errors'].append({'stage':'transfer','status':'unavailable','error':repr(e)});doc['transfer']={'status':'unavailable'}
# cold sequential read: 17 GiB, bounded by free space; write pattern in 8 MiB chunks
p=Path(tempfile.gettempdir())/'e0-cold-ssd-17g.bin'; total=17*1024**3; chunk=8*1024**2
try:
 buf=b'\xA5'*chunk; t=time.perf_counter()
 with open(p,'wb',buffering=0) as f:
  for _ in range(total//chunk): f.write(buf)
  f.flush(); os.fsync(f.fileno())
 wt=time.perf_counter()-t; t=time.perf_counter(); totalread=0
 with open(p,'rb',buffering=0) as f:
  while f.read(chunk): totalread+=chunk
 rt=time.perf_counter()-t;doc['ssd']={'status':'measured','bytes':totalread,'write_seconds':wt,'read_seconds':rt,'write_mib_s':total/1048576/wt,'read_mib_s':totalread/1048576/rt,'file':'temp 17 GiB sequential pattern'}
except Exception as e: doc['errors'].append({'stage':'ssd','status':'unavailable','error':repr(e)});doc['ssd']={'status':'unavailable','constraint':'17 GiB sequential file could not be completed'}
finally:
 try:p.unlink()
 except:pass
out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(doc,indent=2)+'\n');print(json.dumps(doc,indent=2)); raise SystemExit(0)

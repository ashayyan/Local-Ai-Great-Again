"""Windows-native CUDA driver API transfer probe (no torch/nvcc/packages).
Uses ctypes against nvcuda.dll. Reports explicit unavailable errors when absent.
"""
from __future__ import annotations
import argparse, ctypes, json, os, platform, sys, time
from pathlib import Path

CUDA_SUCCESS = 0
CUDA_MEMHOSTALLOC_DEFAULT = 0

def _err(code):
    return f"CUDA error code {int(code)}"

class Driver:
    def __init__(self):
        self.dll = ctypes.WinDLL("nvcuda.dll") if os.name == "nt" else None
        if self.dll is None:
            raise RuntimeError("nvcuda.dll unavailable: non-Windows host")
        self._bind("cuInit", [ctypes.c_uint], ctypes.c_int)
        self._bind("cuDeviceGetCount", [ctypes.POINTER(ctypes.c_int)], ctypes.c_int)
        self._bind("cuDeviceGet", [ctypes.POINTER(ctypes.c_int), ctypes.c_int], ctypes.c_int)
        self._bind("cuDeviceGetName", [ctypes.c_char_p, ctypes.c_int, ctypes.c_int], ctypes.c_int)
        self._bind("cuDeviceTotalMem_v2", [ctypes.POINTER(ctypes.c_size_t), ctypes.c_int], ctypes.c_int)
        self._bind("cuDeviceComputeCapability", [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.c_int], ctypes.c_int)
        self._bind("cuCtxCreate_v2", [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint, ctypes.c_int], ctypes.c_int)
        self._bind("cuCtxDestroy_v2", [ctypes.c_void_p], ctypes.c_int)
        self._bind("cuCtxSynchronize", [], ctypes.c_int)
        self._bind("cuMemAlloc_v2", [ctypes.POINTER(ctypes.c_uint64), ctypes.c_size_t], ctypes.c_int)
        self._bind("cuMemFree_v2", [ctypes.c_uint64], ctypes.c_int)
        self._bind("cuMemHostAlloc", [ctypes.POINTER(ctypes.c_void_p), ctypes.c_size_t, ctypes.c_uint], ctypes.c_int)
        self._bind("cuMemFreeHost", [ctypes.c_void_p], ctypes.c_int)
        self._bind("cuMemcpyHtoD_v2", [ctypes.c_uint64, ctypes.c_void_p, ctypes.c_size_t], ctypes.c_int)
        self._bind("cuMemcpyDtoH_v2", [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_size_t], ctypes.c_int)
        self._bind("cuMemcpyDtoD_v2", [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_size_t], ctypes.c_int)
        self._check(self.cuInit(0))
    def _bind(self, name, args, result):
        fn = getattr(self.dll, name)
        fn.argtypes, fn.restype = args, result
        setattr(self, name, fn)
    def _check(self, code):
        if code != CUDA_SUCCESS: raise RuntimeError(_err(code))

def host_ptr(obj):
    return ctypes.cast(obj, ctypes.c_void_p)

def one_transfer(d, n, samples, warmups, kind):
    # Distinct deterministic byte pattern makes correctness test meaningful.
    pageable_src = ctypes.create_string_buffer(n)
    pageable_dst = ctypes.create_string_buffer(n)
    for i in range(n): pageable_src[i] = (i * 37 + 11) & 255
    pin_src = ctypes.c_void_p(); pin_dst = ctypes.c_void_p()
    d._check(d.cuMemHostAlloc(ctypes.byref(pin_src), n, CUDA_MEMHOSTALLOC_DEFAULT))
    d._check(d.cuMemHostAlloc(ctypes.byref(pin_dst), n, CUDA_MEMHOSTALLOC_DEFAULT))
    ctypes.memmove(pin_src, pageable_src, n)
    dev_a = ctypes.c_uint64(); dev_b = ctypes.c_uint64()
    d._check(d.cuMemAlloc_v2(ctypes.byref(dev_a), n)); d._check(d.cuMemAlloc_v2(ctypes.byref(dev_b), n))
    try:
        def op():
            if kind == "h2d_pinned": return d.cuMemcpyHtoD_v2(dev_a.value, pin_src, n)
            if kind == "d2h_pinned": return d.cuMemcpyDtoH_v2(pin_dst, dev_a.value, n)
            if kind == "h2d_pageable": return d.cuMemcpyHtoD_v2(dev_a.value, host_ptr(pageable_src), n)
            if kind == "d2h_pageable": return d.cuMemcpyDtoH_v2(host_ptr(pageable_dst), dev_a.value, n)
            return d.cuMemcpyDtoD_v2(dev_b.value, dev_a.value, n)
        # Seed device allocation so D2H and D2D correctness are checked.
        d._check(d.cuMemcpyHtoD_v2(dev_a.value, pin_src, n)); d._check(d.cuCtxSynchronize())
        for _ in range(warmups): d._check(op()); d._check(d.cuCtxSynchronize())
        ts=[]
        for _ in range(samples):
            t=time.perf_counter(); d._check(op()); d._check(d.cuCtxSynchronize()); ts.append(time.perf_counter()-t)
        if kind.startswith("d2h"):
            got = ctypes.string_at(pin_dst, n) if kind.endswith("pinned") else bytes(pageable_dst)
            correct = got == bytes(pageable_src)
        elif kind == "d2d":
            d._check(d.cuMemcpyDtoH_v2(host_ptr(pageable_dst), dev_b.value, n)); d._check(d.cuCtxSynchronize())
            correct = bytes(pageable_dst) == bytes(pageable_src)
        else:
            d._check(d.cuMemcpyDtoH_v2(host_ptr(pageable_dst), dev_a.value, n)); d._check(d.cuCtxSynchronize())
            correct = bytes(pageable_dst) == bytes(pageable_src)
        med=sorted(ts)[len(ts)//2]
        return {"status":"measured", "samples_s":ts, "median_s":med, "bandwidth_mib_s":n/med/1048576, "correct":correct}
    finally:
        d._check(d.cuMemFree_v2(dev_a.value)); d._check(d.cuMemFree_v2(dev_b.value)); d._check(d.cuMemFreeHost(pin_src)); d._check(d.cuMemFreeHost(pin_dst))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--sizes-mib", nargs="+", type=int, default=[1,16,64]); ap.add_argument("--samples", type=int, default=5); ap.add_argument("--warmups", type=int, default=1); ap.add_argument("--output", default="notes/gpu_transfer.json"); ap.add_argument("--run-id", default="E0-GPU-transfer")
    a=ap.parse_args(); doc={"schema":"e0-gpu-transfer-v1","run_id":a.run_id,"timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"script":"scripts/s10_cuda_transfer.py","hypothesis":"CUDA driver API copies should produce repeatable median bandwidth at 1, 16, and 64 MiB, with pinned transfers at least as fast as pageable transfers.","numeric_target":"3 sizes x 5 timed samples after 1 warmup for D2D, pinned/pageable H2D/D2H; numeric correctness true; otherwise explicit unavailable error.","platform":{"python":sys.version.split()[0],"os":platform.platform()},"sizes_mib":a.sizes_mib,"samples":a.samples,"warmups":a.warmups,"availability":"unavailable","inventory":[],"transfers":{},"errors":[]}
    try:
        d=Driver(); doc["availability"]="measured"; count=ctypes.c_int(); d._check(d.cuDeviceGetCount(ctypes.byref(count)))
        for ix in range(count.value):
            dev=ctypes.c_int(); d._check(d.cuDeviceGet(ctypes.byref(dev),ix)); name=ctypes.create_string_buffer(256); d._check(d.cuDeviceGetName(name,256,dev.value)); total=ctypes.c_size_t(); d._check(d.cuDeviceTotalMem_v2(ctypes.byref(total),dev.value)); maj=ctypes.c_int(); minor=ctypes.c_int(); d._check(d.cuDeviceComputeCapability(ctypes.byref(maj),ctypes.byref(minor),dev.value)); doc["inventory"].append({"index":ix,"name":name.value.decode(errors="replace"),"total_bytes":total.value,"compute_capability":f"{maj.value}.{minor.value}"})
        if not doc["inventory"]: raise RuntimeError("CUDA reports zero devices")
        ctx=ctypes.c_void_p(); d._check(d.cuCtxCreate_v2(ctypes.byref(ctx),0,0))
        try:
            for mib in a.sizes_mib:
                if mib <= 0 or mib > 64: raise RuntimeError(f"size {mib} MiB outside bounded range 1..64")
                n=mib*1048576
                for kind in ("d2d","h2d_pinned","d2h_pinned","h2d_pageable","d2h_pageable"):
                    doc["transfers"].setdefault(str(mib),{})[kind]=one_transfer(d,n,a.samples,a.warmups,kind)
        finally: d._check(d.cuCtxDestroy_v2(ctx))
    except Exception as e:
        doc["errors"].append({"status":"unavailable","error":str(e)})
        if doc["availability"] != "measured": doc["availability"]="unavailable"
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(doc,indent=2)+"\n",encoding="utf-8"); print(json.dumps(doc,indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main())

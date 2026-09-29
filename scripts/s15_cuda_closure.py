"""Bounded Windows CUDA-driver copy probe; only Python stdlib and nvcuda.dll.

Synchronous host-call + context-synchronization timing (not CUDA event timing).
"""
from __future__ import annotations

import ctypes
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

MIB = 1024 * 1024
SMALL = 10 * 1024
ROUTES = [
    "Free other GPU allocations and repeat the same 512 MiB two-buffer test; record free VRAM before allocation.",
    "Allocate a single 512 MiB device buffer and perform an explicitly labeled in-place D2D test, or use 256 MiB two-buffer chunks; do not substitute either result for the failed 512 MiB two-buffer measurement.",
]


class CUDAError(RuntimeError):
    def __init__(self, operation: str, code: int):
        self.operation, self.code = operation, code
        super().__init__(f"{operation} returned CUDA error {code}")


class Driver:
    def __init__(self):
        if os.name != "nt":
            raise RuntimeError("nvcuda.dll requires Windows")
        self.dll = ctypes.WinDLL("nvcuda.dll")
        p = ctypes.POINTER
        self._bind("cuInit", [ctypes.c_uint])
        self._bind("cuDeviceGetCount", [p(ctypes.c_int)])
        self._bind("cuDeviceGet", [p(ctypes.c_int), ctypes.c_int])
        self._bind("cuDeviceGetName", [ctypes.c_void_p, ctypes.c_int, ctypes.c_int])
        self._bind("cuCtxCreate_v2", [p(ctypes.c_void_p), ctypes.c_uint, ctypes.c_int])
        self._bind("cuCtxDestroy_v2", [ctypes.c_void_p])
        self._bind("cuCtxSynchronize", [])
        self._bind("cuMemAlloc_v2", [p(ctypes.c_uint64), ctypes.c_size_t])
        self._bind("cuMemFree_v2", [ctypes.c_uint64])
        self._bind("cuMemHostAlloc", [p(ctypes.c_void_p), ctypes.c_size_t, ctypes.c_uint])
        self._bind("cuMemFreeHost", [ctypes.c_void_p])
        self._bind("cuMemsetD8_v2", [ctypes.c_uint64, ctypes.c_ubyte, ctypes.c_size_t])
        self._bind("cuMemcpyDtoD_v2", [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_size_t])
        self._bind("cuMemcpyHtoD_v2", [ctypes.c_uint64, ctypes.c_void_p, ctypes.c_size_t])
        self._bind("cuMemcpyDtoH_v2", [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_size_t])
        self.call("cuInit", 0)

    def _bind(self, name, args):
        fn = getattr(self.dll, name)
        fn.argtypes, fn.restype = args, ctypes.c_int
        setattr(self, name, fn)

    def call(self, operation, *args):
        rc = getattr(self, operation)(*args)
        if rc != 0:
            raise CUDAError(operation, rc)


def summary(samples, n=None):
    median = statistics.median(samples)
    result = {"samples_us": samples, "median_us": median,
              "min_us": min(samples), "max_us": max(samples),
              "spread_us": max(samples) - min(samples),
              "spread_definition": "max - min"}
    if n is not None:
        result["bandwidth_mib_s"] = n / MIB / (median / 1e6)
    return result


def timed(d, operation):
    start = time.perf_counter_ns()
    operation()
    d.call("cuCtxSynchronize")
    return (time.perf_counter_ns() - start) / 1000


def release(d, allocations, failures):
    # Free every successfully acquired resource, even when an earlier free fails.
    for operation, address in reversed(allocations):
        try:
            d.call(operation, address)
        except Exception as exc:
            failures.append(error_record(exc, "cleanup"))


def error_record(exc, stage):
    result = {"stage": stage, "error": str(exc), "type": type(exc).__name__}
    if isinstance(exc, CUDAError):
        result.update({"operation": exc.operation, "cuda_error_code": exc.code})
    return result


def d2d(d, n):
    allocations = []
    failures = []
    try:
        src, dst = ctypes.c_uint64(), ctypes.c_uint64()
        d.call("cuMemAlloc_v2", ctypes.byref(src), n)
        allocations.append(("cuMemFree_v2", src.value))
        d.call("cuMemAlloc_v2", ctypes.byref(dst), n)
        allocations.append(("cuMemFree_v2", dst.value))
        # This is outside timing: all bytes must be initialized, including the tail.
        d.call("cuMemsetD8_v2", src.value, 0xA5, n)
        d.call("cuMemsetD8_v2", dst.value, 0x5A, n)
        d.call("cuCtxSynchronize")
        copy = lambda: d.call("cuMemcpyDtoD_v2", dst.value, src.value, n)
        timed(d, copy)  # exactly one warmup
        samples = [timed(d, copy) for _ in range(7)]
        # Verify the ENTIRE destination, not only a tiny prefix. Verification is
        # excluded from timing and uses 4 MiB pageable memory (no large host pin).
        chunk_size = 4 * MIB
        host = ctypes.create_string_buffer(chunk_size)
        expected = b"\xA5" * chunk_size
        correct = True
        for offset in range(0, n, chunk_size):
            count = min(chunk_size, n - offset)
            d.call("cuMemcpyDtoH_v2", ctypes.cast(host, ctypes.c_void_p), dst.value + offset, count)
            d.call("cuCtxSynchronize")
            if ctypes.string_at(host, count) != expected[:count]:
                correct = False
                break
        result = {"status": "measured", "bytes": n, "samples": 7,
                  "warmups": 1, "correct": correct,
                  "correctness_scope": "all destination bytes after final sample"}
        result.update(summary(samples, n))
    except Exception as exc:
        result = {"status": "error", "bytes": n, "error": error_record(exc, "d2d")}
    finally:
        release(d, allocations, failures)
    if failures:
        result["cleanup_errors"] = failures
        result["status"] = "error"
    if result["status"] == "measured" and not result["correct"]:
        result["status"] = "incorrect"
    return result


def pinned_small(d):
    allocations, failures = [], []
    result = {"status": "error", "bytes": SMALL}
    try:
        src, dst = ctypes.c_void_p(), ctypes.c_void_p()
        dev = ctypes.c_uint64()
        d.call("cuMemHostAlloc", ctypes.byref(src), SMALL, 0)
        allocations.append(("cuMemFreeHost", src))
        d.call("cuMemHostAlloc", ctypes.byref(dst), SMALL, 0)
        allocations.append(("cuMemFreeHost", dst))
        d.call("cuMemAlloc_v2", ctypes.byref(dev), SMALL)
        allocations.append(("cuMemFree_v2", dev.value))
        expected = bytes((i * 37 + 11) & 255 for i in range(SMALL))
        ctypes.memmove(src, expected, SMALL)
        h2d = lambda: d.call("cuMemcpyHtoD_v2", dev.value, src, SMALL)
        d2h = lambda: d.call("cuMemcpyDtoH_v2", dst, dev.value, SMALL)
        timed(d, h2d)  # one warmup of each direction
        timed(d, d2h)
        h, r, roundtrip = [], [], []
        correct = True
        for _ in range(20):
            h.append(timed(d, h2d))
            ctypes.memset(dst, 0, SMALL)
            r.append(timed(d, d2h))
            correct &= ctypes.string_at(dst, SMALL) == expected
            ctypes.memset(dst, 0, SMALL)
            roundtrip.append(timed(d, lambda: (d.call("cuMemcpyHtoD_v2", dev.value, src, SMALL),
                                                d.call("cuMemcpyDtoH_v2", dst, dev.value, SMALL))))
            correct &= ctypes.string_at(dst, SMALL) == expected
        result = {"status": "measured" if correct else "incorrect", "bytes": SMALL,
                  "samples": 20, "warmups_per_direction": 1, "correct": correct,
                  "correctness_scope": "all 10240 bytes checked after each D2H and round trip",
                  "h2d": summary(h, SMALL), "d2h": summary(r, SMALL),
                  "roundtrip": summary(roundtrip)}
    except Exception as exc:
        result["error"] = error_record(exc, "pinned_10kib")
    finally:
        release(d, allocations, failures)
    if failures:
        result["cleanup_errors"] = failures
        result["status"] = "error"
    return result


def main():
    doc = {"schema": "e0-cuda-closure-v1", "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "script": "scripts/s15_cuda_closure.py",
           "command": "python scripts/s15_cuda_closure.py",
           "hypothesis": "Dedicated D2D copies at 256/512 MiB and valid pinned 10 KiB copies expose measured bandwidth and per-hop latency.",
           "numeric_target": "D2D 256/512 MiB: 1 warmup + 7 samples each, whole-buffer correctness; 10 KiB pinned H2D/D2H and round trip: 20 samples each, all correct; exact CUDA errors if unavailable.",
           "platform": {"python": sys.version.split()[0], "os": platform.platform()},
           "timing": "perf_counter_ns around synchronous driver call + cuCtxSynchronize; separate operations for individual H2D and D2H; round trip includes two calls and one synchronize",
           "device": {}, "d2d": {}, "pinned_10kib": {}, "errors": [], "routes_if_blocked": ROUTES}
    ctx = ctypes.c_void_p()
    d = None
    try:
        d = Driver()
        count = ctypes.c_int()
        d.call("cuDeviceGetCount", ctypes.byref(count))
        if count.value < 1:
            raise RuntimeError("cuDeviceGetCount returned zero devices")
        device = ctypes.c_int()
        name = ctypes.create_string_buffer(256)
        d.call("cuDeviceGet", ctypes.byref(device), 0)
        d.call("cuDeviceGetName", name, len(name), device.value)
        doc["device"] = {"index": 0, "name": name.value.decode(errors="replace")}
        d.call("cuCtxCreate_v2", ctypes.byref(ctx), 0, device.value)
        for mib in (256, 512):
            doc["d2d"][str(mib)] = d2d(d, mib * MIB)
        doc["pinned_10kib"] = pinned_small(d)
    except Exception as exc:
        doc["errors"].append(error_record(exc, "initialization"))
    finally:
        if d is not None and ctx.value:
            try:
                d.call("cuCtxDestroy_v2", ctx)
            except Exception as exc:
                doc["errors"].append(error_record(exc, "context_cleanup"))
    entries = list(doc["d2d"].values()) + ([doc["pinned_10kib"]] if doc["pinned_10kib"] else [])
    doc["status"] = "measured" if len(entries) == 3 and all(x["status"] == "measured" for x in entries) and not doc["errors"] else "partial_or_error"
    out = Path("notes/cuda_closure.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=2))
    return 0 if doc["status"] == "measured" else 1


if __name__ == "__main__":
    raise SystemExit(main())

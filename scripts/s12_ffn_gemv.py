"""Bounded M=1 FFN GEMV: installed Numba CUDA only; never substitutes a copy for GEMV.

Run: python scripts/s12_ffn_gemv.py --output notes/ffn_gemv.json
Weights are generated, not model weights. Timing excludes allocation and transfers.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
import traceback
from pathlib import Path

ROWS, COLS = 17408, 5120
SAMPLES, WARMUPS = 5, 1


def make_kernel(cuda, float32, uint32, libdevice):
    @cuda.jit
    def gemv_f32(w, x, y):
        row = cuda.blockIdx.x
        lane = cuda.threadIdx.x
        partial = cuda.shared.array(256, dtype=float32)
        acc = float32(0)
        for col in range(lane, COLS, 256):
            acc += w[row, col] * x[col]
        partial[lane] = acc
        cuda.syncthreads()
        stride = 128
        while stride:
            if lane < stride:
                partial[lane] += partial[lane + stride]
            cuda.syncthreads()
            stride //= 2
        if lane == 0:
            y[row] = partial[0]

    @cuda.jit
    def gemv_bf16(w, x, y):
        row = cuda.blockIdx.x
        lane = cuda.threadIdx.x
        partial = cuda.shared.array(256, dtype=float32)
        acc = float32(0)
        for col in range(lane, COLS, 256):
            # BF16 storage, FP32 accumulation. All test values are BF16-exact.
            val = libdevice.int_as_float(uint32(w[row, col]) << 16)
            acc += val * x[col]
        partial[lane] = acc
        cuda.syncthreads()
        stride = 128
        while stride:
            if lane < stride:
                partial[lane] += partial[lane + stride]
            cuda.syncthreads()
            stride //= 2
        if lane == 0:
            y[row] = partial[0]

    return {"f32": gemv_f32, "bf16": gemv_bf16}


def run_dtype(dtype, np, cuda, kernels):
    # Bound device allocation to one weight matrix + input + output (~357 MiB F32).
    # Values exactly representable in BF16 and repeat every 32 columns, 17 rows.
    cols = np.arange(COLS, dtype=np.int32)
    x = ((cols % 16 - 8) * 0.0625).astype(np.float32)
    base = ((np.arange(17, dtype=np.int32)[:, None] - 8) * 0.03125 +
            ((cols % 32)[None, :] - 16) * 0.00390625).astype(np.float32)
    expected = (base.astype(np.float64) @ x.astype(np.float64)).astype(np.float32)
    weights = np.empty((ROWS, COLS), dtype=np.float32 if dtype == "f32" else np.uint16)
    for start in range(0, ROWS, 17):
        stop = min(start + 17, ROWS)
        tile = base[:stop - start]
        weights[start:stop] = tile if dtype == "f32" else (tile.view(np.uint32) >> 16).astype(np.uint16)
    w_dev = cuda.to_device(weights)
    del weights
    x_dev = cuda.to_device(x)
    y_dev = cuda.device_array(ROWS, dtype=np.float32)
    kernel = kernels[dtype]
    try:
        # Launch includes JIT compilation on first call; neither JIT nor H2D are timed.
        for _ in range(WARMUPS):
            kernel[ROWS, 256](w_dev, x_dev, y_dev)
            cuda.synchronize()
        times = []
        for _ in range(SAMPLES):
            start = time.perf_counter()
            kernel[ROWS, 256](w_dev, x_dev, y_dev)
            cuda.synchronize()
            times.append(time.perf_counter() - start)
        result = y_dev.copy_to_host()
        reference = expected[np.arange(ROWS) % 17]
        diff = np.abs(result.astype(np.float64) - reference.astype(np.float64))
        max_err = float(diff.max())
        correct = bool(np.all(np.isfinite(result)) and np.allclose(result, reference, rtol=1e-4, atol=1e-3))
        median = sorted(times)[len(times) // 2]
        weight_bytes = ROWS * COLS * (4 if dtype == "f32" else 2)
        traffic = weight_bytes + COLS * 4 + ROWS * 4
        return {"status": "measured", "correct": correct, "max_abs_error": max_err,
                "samples_s": times, "median_s": median,
                "weight_bytes": weight_bytes, "effective_bytes": traffic,
                "effective_gb_s": traffic / median / 1e9,
                "reference_method": "17 FP64 pattern-row dot products repeated over 17408 outputs; BF16 inputs exact"}
    finally:
        del w_dev, x_dev, y_dev


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="notes/ffn_gemv.json")
    a = parser.parse_args()
    doc = {"schema": "e0-ffn-gemv-v1", "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "script": "scripts/s12_ffn_gemv.py", "shape": [ROWS, COLS], "batch": 1,
           "hypothesis": "Resident-weight CUDA GEMV at FFN dimensions has measurable effective bandwidth and correct outputs.",
           "numeric_target": "BF16 and F32, 5 timed launches after 1 warmup, correct within atol=1e-3/rtol=1e-4, median effective decimal GB/s.",
           "timing_scope": "host wall-clock launch + cuda.synchronize; excludes weight generation, H2D and JIT",
           "samples": SAMPLES, "warmups": WARMUPS, "platform": {"python": sys.version.split()[0], "os": platform.platform()},
           "status": "unavailable", "dtype_results": {}, "errors": [],
           "routes": ["Repair installed Numba CUDA primary-context selection (cuda.current_context() must succeed), then rerun this identical JIT kernel without changing packages.",
                      "Use an already-installed CUDA BLAS runtime (cuBLAS sgemv/gemvEx) through ctypes with explicit symbol and correctness checks; benchmark the same resident-weight shape."]}
    try:
        import numpy as np
        import numba
        from numba import cuda, float32, uint32
        from numba.cuda import libdevice
        doc["backend"] = {"name": "numba.cuda", "numba": numba.__version__, "numpy": np.__version__}
        if not cuda.is_available():
            raise RuntimeError("numba.cuda.is_available() returned False")
        dev = cuda.get_current_device()
        doc["device"] = {"name": dev.name.decode(errors="replace") if isinstance(dev.name, bytes) else str(dev.name),
                         "compute_capability": ".".join(map(str, dev.compute_capability))}
        # CUDA device enumeration alone does not prove a usable context.
        cuda.select_device(0)
        cuda.current_context()
        kernels = make_kernel(cuda, float32, uint32, libdevice)
        for dtype in ("f32", "bf16"):
            try:
                doc["dtype_results"][dtype] = run_dtype(dtype, np, cuda, kernels)
            except Exception as e:
                doc["dtype_results"][dtype] = {"status": "unavailable", "error": f"{type(e).__name__}: {e}"}
                doc["errors"].append({"dtype": dtype, "stage": "allocation/compile/launch", "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})
        if all(v["status"] == "measured" and v["correct"] for v in doc["dtype_results"].values()) and len(doc["dtype_results"]) == 2:
            doc["status"] = "measured"
        elif any(v["status"] == "measured" for v in doc["dtype_results"].values()):
            doc["status"] = "partial"
    except Exception as e:
        doc["errors"].append({"stage": "backend/device/context", "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})
    path = Path(a.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=2))
    return 0 if doc["status"] == "measured" else 2


if __name__ == "__main__":
    raise SystemExit(main())

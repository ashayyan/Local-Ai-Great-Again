# E0 CUDA ctypes closure

## Hypothesis and numeric target (before execution)

Dedicated native CUDA-driver D2D copies of 256 and 512 MiB will expose resident-copy bandwidth above the small-transfer latency regime. Valid pinned 10 KiB host/device hops will expose per-hop and round-trip host-call latency. Target: each large copy, one warmup and seven timed samples, median and max-minus-min spread, whole-destination correctness; pinned H2D, D2H and round trip, 20 samples each, full 10 KiB correctness. Driver errors must retain their CUDA operation and integer return code. No packages or model weights.

## Command and results

```powershell
python scripts/s15_cuda_closure.py
```

RTX 3050 Laptop GPU, Windows 11 build 26200, Python 3.13.2; `nvcuda.dll` through Python stdlib `ctypes`. Both D2D device buffers are separately allocated with `cuMemAlloc_v2` (2 × 256 MiB and 2 × 512 MiB respectively); source and destination initialized with different bytes outside timing. All destination bytes were verified with bounded 4 MiB D2H chunks after the final sample. 10 KiB pinned source/destination were allocated with `cuMemHostAlloc`, and a real 10 KiB device allocation was used for H2D/D2H; all 10,240 output bytes checked after every D2H and round trip.

| Path | Samples after warmup | Median | Spread (max − min) | Derived bandwidth | Correct |
|---|---:|---:|---:|---:|---|
| 256 MiB D2D | 7 after 1 | 2,943.5 µs | 586.2 µs | 86,971 MiB/s | yes |
| 512 MiB D2D | 7 after 1 | 6,445.6 µs | 63.9 µs | 79,434 MiB/s | yes |
| 10 KiB pinned H2D | 20 after 1 | 13.85 µs | 36.0 µs | 705 MiB/s* | yes |
| 10 KiB pinned D2H | 20 after 1 | 11.9 µs | 19.5 µs | 821 MiB/s* | yes |
| 10 KiB pinned H2D→D2H | 20 after 1 warmup per direction | 26.2 µs | 26.8 µs | — | yes |

*10 KiB bandwidth is dominated by driver-call/synchronization latency and is not a link bandwidth estimate. All timings use `perf_counter_ns` around checked synchronous driver calls and `cuCtxSynchronize`; round-trip timing encloses both checked copy calls and one synchronization. Large-copy data are effective single-direction payload bandwidth, not a CUDA-event peak. Raw samples, exact numeric values, errors and fallback routes are preserved in `notes/cuda_closure.json`. No API errors in this run. Unlike the prior generic large-copy attempt, no pinned/pageable allocation of hundreds of MiB is performed.

If 512 MiB two-buffer allocation or another CUDA operation fails, the JSON preserves the failed operation, integer error code and error text. Two routes: (1) free other GPU allocations, record free VRAM and repeat the same two-buffer test; (2) explicitly label a single-buffer in-place 512 MiB D2D test, or use 256 MiB two-buffer chunks, without misrepresenting either as the failed 512 MiB two-buffer measurement. Cheapest next experiment if failure: `python scripts/s15_cuda_closure.py`, expecting checked success or exact failed-operation/code in JSON. For observed latency variance, repeat the same command with stable AC/power state, then compare seven/twenty raw samples against this run; no unmeasured model tok/s or quality claim is made.

## Status / Numbers / Next Experiment

- **Status:** Measured, all three paths correct, zero CUDA errors.
- **Numbers:** D2D 256/512 MiB = 86,971/79,434 MiB/s; pinned 10 KiB H2D/D2H/round-trip medians = 13.85/11.9/26.2 µs.
- **Next Experiment:** Repeat `python scripts/s15_cuda_closure.py` on AC with stable clocks and compare median/spread to isolate the 256 MiB alternating timing modes.

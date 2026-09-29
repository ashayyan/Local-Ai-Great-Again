# E0 FFN-shaped CUDA GEMV

## Hypothesis and numeric target (before run)

A resident-weight CUDA kernel computes M=1 GEMV at 17408 × 5120 in both BF16-weight/F32-accumulator and F32, with 5 timed launches after 1 warmup, full-output correctness (`atol=1e-3`, `rtol=1e-4`) and median effective decimal GB/s. If the kernel cannot safely run, record an explicit unavailable artifact, exact error, and two routes. BF16 weight matrix = 178,257,920 bytes (~170 MiB); F32 = 356,515,840 bytes (~340 MiB). Only one weight matrix is resident at a time. Synthetic deterministic BF16-exact inputs; no model weights.

## Run

```powershell
python scripts/s12_ffn_gemv.py --output notes/ffn_gemv.json
```

Run returned exit 2, explicitly `status: unavailable` on Windows 11 build 26200 / Python 3.13.2, RTX 3050 Laptop GPU CC 8.6. Installed Numba 0.61.2 and NumPy 2.2.5; CuPy absent. Numba reports CUDA available, but `cuda.select_device(0); cuda.current_context()` raises **`IndexError: list index out of range`** in `numba.cuda.cudadrv.devices._get_or_create_context_uncached`, indexing `self.gpus[ac.devnum]`. Direct allocation in an initial run raised this same IndexError, then `OSError: exception: access violation reading 0xFFFFFFFFFFFFFFFF` on a retry. The final script fails fast at context validation before allocating a 170–340 MiB matrix. Full traceback and machine-readable result: `notes/ffn_gemv.json`. No CUDA GEMV launched, so **no five samples, correctness outcome, or effective GB/s measurement exists**. The script does not mislabel a transfer/copy as GEMV. Its proposed Numba kernel is a 256-thread-per-output-row parallel reduction, with BF16 uint16 bits expanded to F32 before F32 accumulation; JIT and transfers are excluded from measured timing once backend works.

Constraint: device enumeration succeeds (one 4,294,443,008-byte RTX 3050) but active CUDA context creation fails with the exact IndexError above. Two routes:

1. Repair the existing Numba CUDA primary-context selection so `cuda.current_context()` succeeds; rerun the unchanged benchmark without installing packages.
2. Locate an already-installed compatible cuBLAS DLL and use `ctypes` `cublasSgemv`/`cublasGemmEx` with explicit symbol checks and correctness, measuring the same shape and dtype. The initial `ctypes.WinDLL('cublas64_12.dll')` probe returned `FileNotFoundError: Could not find module 'cublas64_12.dll' (or one of its dependencies)`; an absolute-path/library-dependency inventory is needed before this route.

## Status / Numbers / Next Experiment

- **Status:** Unavailable; kernel/context boundary recorded rather than substituting bandwidth.
- **Numbers:** 17408 × 5120, M=1; BF16 178,257,920 bytes/F32 356,515,840 bytes; target 5 samples + 1 warmup; actual 0 samples, effective GB/s unavailable.
- **Next Experiment:** Cheapest: `python -c "from numba import cuda; print(len(cuda.gpus)); cuda.select_device(0); print(cuda.current_context())"` — expected measurable result is one enumerated device and a valid context, or the reproducible IndexError; on success run `python scripts/s12_ffn_gemv.py --output notes/ffn_gemv.json` and inspect 5 timings, correctness, and GB/s for each dtype.

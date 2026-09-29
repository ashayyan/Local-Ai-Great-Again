# E0 GPU Transfer

## Run 1

Hypothesis before run: CUDA driver API copies should produce repeatable median bandwidth at 1, 16, and 64 MiB, with pinned transfers at least as fast as pageable transfers. Numeric target: 3 sizes × 5 timed samples after 1 warmup for D2D, pinned/pageable H2D/D2H; numeric correctness true; otherwise explicit unavailable error.

Exact command:

```powershell
python scripts/s10_cuda_transfer.py --sizes-mib 1 16 64 --samples 5 --warmups 1 --output notes/gpu_transfer.json --run-id E0-GPU-transfer-run1
```

Result: measured on Windows 11 build 26200, Python 3.13.2, NVIDIA GeForce RTX 3050 Laptop GPU (4,294,443,008 bytes, compute capability 8.6); no errors. Every transfer size/direction reported `correct: true`. Median bandwidth in MiB/s:

| MiB | D2D | H2D pinned | D2H pinned | H2D pageable | D2H pageable |
|---:|---:|---:|---:|---:|---:|
| 1 | 15408.3 | 7007.7 | 7315.3 | 4340.3 | 4045.3 |
| 16 | 72365.5 | 1860.5 | 2126.0 | 1743.6 | 1925.9 |
| 64 | 69656.1 | 6796.7 | 2032.0 | 1832.9 | 4433.4 |

The full repeated samples, inventory, and correctness flags are in `notes/gpu_transfer.json`. Results include transfer-call plus synchronization timing; they are not a claim of peak PCIe capability. Pinned/pageable ordering varies by direction and size, so the hypothesis is only partially supported; correctness and reproducibility target passed for this run.

## Run 2 (variance check)

Hypothesis before run: repeating the same bounded protocol should keep device identity and numeric correctness stable while exposing timing variance. Numeric target: 3 sizes × 5 samples + 1 warmup, all correctness flags true, no API errors.

Exact command:

```powershell
python scripts/s10_cuda_transfer.py --sizes-mib 1 16 64 --samples 5 --warmups 1 --output notes/gpu_transfer_run2.json --run-id E0-GPU-transfer-run2
```

Result: measured same RTX 3050 Laptop GPU (CC 8.6), no errors, and all 15 correctness checks true. Two run2 invocations accidentally used the same output path while execution was concurrent. The **current preserved JSON** `notes/gpu_transfer_run2.json` is run ID `E0-GPU-transfer-run2` and reports medians MiB/s: 1 MiB D2D 37,594; pinned H2D 9,506; pinned D2H 9,479. At 16 MiB: D2D 69,085; pinned H2D 1,842; pinned D2H 2,072. At 64 MiB: D2D 76,445; pinned H2D 5,769; pinned D2H 5,720. The overwritten concurrent run reported 1/16/64 MiB pinned H2D 9,390/5,669/1,897 MiB/s but its raw samples are not retained and are **excluded from reproducible comparisons**. Across the two retained runs, pinned H2D at 16 MiB differs by -1.0%, while 1 MiB differs by +35.6% and 64 MiB by -15.1%. These are observed synchronous host-call timings, not stable peak-link specifications; the next run must have a unique output path and fixed power/clock state.

## Status / Numbers / Next Experiment

- **Status:** Native ctypes driver API probe measured; no torch, nvcc, package install, or model weights used.
- **Numbers:** 1/16/64 MiB, 5 samples + 1 warmup. Medians are reported in MiB/s: D2D 15,408/72,366/69,656; pinned H2D 7,008/1,860/6,797; pinned D2H 7,315/2,126/2,032; all 15 transfer cases numerically correct.
- **Next Experiment:** Collect a third uniquely named run under fixed AC/GPU clocks and recorded negotiated PCIe link state; compare variance and rerun outlier sizes before using these as a T1 offload model.

# Hardware Profile

Run: e0-table-final. Raw samples: notes\e0-table-final/hardware.json. Units: MB in the GPU inventory are decimal labels reported by nvidia-smi; SSD MB/s below uses MiB (1048576 bytes) and is a single cached read, **not** a sustained SSD ceiling.

| Quantity | Observed value | Status |
|---|---:|---|
| GPU | NVIDIA GeForce RTX 3050 Laptop GPU | measured |
| VRAM | 4096 MiB reported | measured |
| Compute capability | 8.6 | measured |
| NVIDIA driver | 610.62 | measured |
| GPU achievable bandwidth (copy) | — | unavailable: CUDA helper pending |
| FFN GEMV/GEMM achievable bandwidth | — | unavailable: CUDA helper pending |
| CPU | 11th Gen Intel(R) Core(TM) i5-11400H @ 2.70GHz, 6C/12T | measured |
| RAM capacity | 17179869184 bytes | measured |
| STREAM RAM bandwidth | — | unavailable: helper pending |
| PCIe negotiated link | Gen 2 x8 | measured; this is not H2D throughput |
| Pinned H2D/D2H bandwidth | — | unavailable: CUDA helper pending |
| SSD sample read | 2482.58 MiB/s (67108864 byte cached sample) | measured, not a sustained ceiling |
| SSD sample write | 1625.52 MiB/s (67108864 byte sample) | measured, not a sustained ceiling |
| OS | Microsoft Windows 11 Pro, build 26200 | measured |

## Status / Numbers / Next Experiment
- **Status:** Partial hardware inventory; GPU, CPU, PCIe transfer, and sustained SSD bandwidth gates remain open.
- **Numbers:** 4096 MiB VRAM, 17179869184 bytes RAM, PCIe Gen 2 x8; GPU/CPU/pinned-transfer bandwidth unmeasured.
- **Next Experiment:** Implement pinned CUDA copy/FFN GEMV and CPU STREAM helpers; rerun twice with identical settings and a cold SSD file exceeding RAM cache.

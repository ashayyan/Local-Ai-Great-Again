# Hardware Profile

Run: e0-execute-current. Raw samples: C:\Users\lahd2\OneDrive\Desktop\ai local\notes\e0-execute-current/hardware.json. Units: MB in the GPU inventory are decimal labels reported by nvidia-smi; SSD MB/s below uses MiB (1048576 bytes) and is a single cached read, **not** a sustained SSD ceiling.

| Quantity | Observed value | Status |
|---|---:|---|
| GPU | NVIDIA GeForce RTX 3050 Laptop GPU | measured |
| VRAM | 4096 MiB reported | measured |
| Compute capability | 8.6 | measured |
| NVIDIA driver | 610.62 | measured |
| GPU achievable bandwidth (copy) | — | unavailable: CUDA helper pending |
| FFN GEMV/GEMM achievable bandwidth | — | unavailable: CUDA helper pending |
| CPU | 11th Gen Intel(R) Core(TM) i5-11400H @ 2.70GHz, 6C/12T; AVX2, AVX-512, BMI2 | measured by llama.cpp |
| RAM capacity | 17179869184 bytes | measured |
| STREAM RAM bandwidth | — | unavailable: helper pending |
| PCIe negotiated link | Gen 2 x8 | measured; this is not H2D throughput |
| Pinned H2D/D2H bandwidth | — | unavailable: CUDA helper pending |
| SSD sample read | 1573.16 MiB/s (67108864 byte cached sample) | measured, not a sustained ceiling |
| SSD sample write | 967.58 MiB/s (67108864 byte sample) | measured, not a sustained ceiling |
| OS | Microsoft Windows 11 Pro, build 26200 | measured |

## Status / Numbers / Next Experiment
- **Status:** Hardware identity and CPU feature record updated; bandwidth probes remain separately logged.
- **Numbers:** i5-11400H, 6 cores/12 threads, AVX2, AVX-512, BMI2; 4096 MiB VRAM; 17179869184 bytes RAM; PCIe Gen 2 x8.
- **Next Experiment:** Use the measured 16.94 GB/s Triad and 0.95 GB/s SSD readings as the E1/T3 placement budget; run only targeted kernels after the one-shard smoke exists.

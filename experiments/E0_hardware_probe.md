# E0 Hardware Probe

## Status / Numbers / Next Experiment

- **Status:** Partial E0 hardware profile measured on two Windows-native runs. No inference benchmark was run.
- **Numbers:** RTX 3050 Laptop GPU, 4,096 MB VRAM, compute capability/SM 8.6, NVIDIA driver 610.62, Windows 11 Pro build 26200; Intel i5-11400H, 6 cores/12 logical processors; 16 GiB RAM; SSD sample 60.13 MB/s write and 138.83 MB/s read for a 1 MiB temporary file; GPU temperature 54 C on the first run. PCIe, GPU copy/GEMV/GEMM, CPU STREAM, and pinned H2D/D2H remain unmeasured. `nvidia-smi -q -d PCI` returned `Failed to parse --display/-d flags`.
- **Next Experiment:** Correct the supported PCIe query, add a pinned CUDA transfer/FFN microbenchmark and CPU STREAM helper, then rerun twice with a larger SSD test file and append the measured values without overwriting prior artifacts.

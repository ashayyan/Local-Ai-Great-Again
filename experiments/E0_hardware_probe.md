# E0 Hardware Probe

## Status / Numbers / Next Experiment

- **Status:** Partial E0 hardware profile measured on two Windows-native runs. No inference benchmark was run.
- **Numbers:** RTX 3050 Laptop GPU, 4,096 MB VRAM, compute capability/SM 8.6, NVIDIA driver 610.62, Windows 11 Pro build 26200; Intel i5-11400H, 6 cores/12 logical processors; 16 GiB RAM; SSD sample 60.13 MB/s write and 138.83 MB/s read for a 1 MiB temporary file; GPU temperature 54 C on the first run. PCIe, GPU copy/GEMV/GEMM, CPU STREAM, and pinned H2D/D2H remain unmeasured. `nvidia-smi -q -d PCI` returned `Failed to parse --display/-d flags`.
- **Next Experiment:** Add a pinned CUDA transfer/FFN microbenchmark and CPU STREAM helper, then rerun twice with a cold SSD test file larger than RAM; append measured values without overwriting prior artifacts.

## E0-HW follow-up: corrected PCIe inventory and 64 MiB SSD sample

Hypothesis before run: a supported `nvidia-smi --query-gpu=pcie.link.gen.current,pcie.link.width.current` query returns negotiated link metadata; a 64 MiB temporary-file sample is recorded separately from the 1 MiB sample. Numeric target: nonempty link generation/width, no parse error, and one 64 MiB read/write timing. Exact command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s01_hardware_probe.ps1 -RunId e0-table-final -OutputRoot notes -Warmups 1 -Samples 2 -SsdTestBytes 67108864`. Model/quant/context and prefill/decode/quality: not applicable; peak VRAM/RAM not measured. Script git blob hash: `3113b50f2f0c3c2fd1c49dd54ddcd3cc0a8a9cc6`; parent commit before run: `bcefebe18a975864ec4671e8b16c455e98c23ae3`.

Observed: negotiated PCIe Gen 2 x8 at idle (not achievable H2D bandwidth); 64 MiB cached-read/write samples are in `notes/e0-table-final/hardware.json`. This size is smaller than the 16 GiB RAM cache, so these SSD numbers are not a sustained storage ceiling. CUDA/CPU/PCIe transfer bandwidth remains unmeasured. Routes: (1) compile native CUDA pinned-transfer/FFN microbenchmarks and STREAM, (2) provision a separately labeled WSL2 environment and run equivalent pinned benchmarks. Cheapest next experiment: a native CUDA pinned H2D/D2H sweep at 1, 16, and 256 MiB, expected to yield measured GB/s and latency or an explicit toolchain error.

### Status / Numbers / Next Experiment
- **Status:** PCIe inventory query corrected; E0 bandwidth/SSD ceiling gates open.
- **Numbers:** Negotiated idle PCIe Gen 2 x8; VRAM 4096 MiB; RAM 17179869184 bytes; pinned throughput unmeasured.
- **Next Experiment:** Run pinned host-device transfer benchmark and record clocks/link state during transfers.

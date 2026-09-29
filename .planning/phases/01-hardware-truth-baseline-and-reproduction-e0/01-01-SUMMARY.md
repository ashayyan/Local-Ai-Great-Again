# Plan 01-01 Summary — Hardware truth probe

**Status:** Partial hardware measurements; E0 hardware gate remains open.

- Implemented Windows-native inventory at `scripts/s01_hardware_probe.ps1`; ran two initial identity samples plus a corrected PCIe inventory and 64 MiB temporary-file samples. Raw JSON and current table are in `notes/`.
- Measured RTX 3050 Laptop GPU with 4096 MiB reported VRAM, compute capability 8.6, NVIDIA driver 610.62; i5-11400H 6C/12T and installed RAM 17,179,869,184 bytes. An idle negotiated PCIe reading was Gen 2 ×8, **not** transfer throughput.
- Added .NET 8 single-thread Triad benchmark `scripts/s09_cpu_stream.ps1` / `scripts/cpu_stream/Program.cs`: 7 samples, 2 warmups, 3 × 256 MiB arrays; median 11,978.009 MiB/s (~12.56 decimal GB/s). This is not a multicore DRAM ceiling.
- The 64 MiB SSD sample was cache-affected and cannot replace a sustained cold SSD read. CUDA copy/GEMV/GEMM, pinned H2D/D2H, GPU SM count, AVX2 capability confirmation, process RAM/VRAM peaks, and complete thermal-repeat controls remain pending.
- Original `pwsh` verifier was unavailable (Windows PowerShell 5.1 available); corrected unsupported `nvidia-smi -q -d PCI` route to supported query fields. No full model was run.

## Status / Numbers / Next Experiment
- **Status:** Hardware identity and partial CPU bandwidth measured; full E0 hardware truth not complete.
- **Numbers:** 4096 MiB reported VRAM, compute 8.6, 16 GiB RAM, 6C/12T CPU; single-thread Triad 11,978.009 MiB/s; idle PCIe Gen 2 ×8; achieved GPU and PCIe GB/s unmeasured.
- **Next Experiment:** Under fixed AC/clocks, run a native CUDA pinned H2D/D2H sweep and 17408×5120 GEMV/GEMM plus multicore STREAM; then perform a cold SSD read above available RAM, each with raw repeated samples and script hashes.

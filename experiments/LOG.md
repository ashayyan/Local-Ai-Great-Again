# Experiment Log

Every run records hypothesis, target, command, model, quant, context, VRAM/RAM peaks, prefill/decode speed, quality, script/hash, and Status / Numbers / Next Experiment.

## E0-HW manual-e0b / manual-e0c — 2026-09-29

- Hypothesis: Windows-native probe identifies actual laptop limits with repeatable medians.
- Numeric target: two runs; identity stable; repeated bandwidth/transfer samples; explicit unavailable fields.
- Command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s01_hardware_probe.ps1 -RunId manual-e0b/manual-e0c -OutputRoot notes -Warmups 1 -Samples 2 -SsdTestBytes 1048576`
- Script: `scripts/s01_hardware_probe.ps1`; model/quant/context: not applicable (hardware probe).
- Measured: RTX 3050 Laptop GPU, 4096 MB VRAM, compute capability 8.6, driver 610.62, Windows 11 Pro build 26200; i5-11400H, 6 cores/12 logical processors; RAM 17179869184 bytes; SSD probe 1 MiB write 60.13 MB/s/read 138.83 MB/s on run manual-e0b; GPU temperature 54 C; PCIe/CUDA bandwidth/STREAM unavailable.
- Failure: `nvidia-smi -q -d PCI` rejected the display flag; CUDA and STREAM helpers are not installed. Routes: (1) use corrected `nvidia-smi -q`/supported query plus native CUDA toolkit helper; (2) run WSL2 pinned CUDA/STREAM probes. Cheapest next experiment: correct PCI query and compile/run a 17408x5120 copy/GEMV microbenchmark.

### Status / Numbers / Next Experiment
- Status: Partial E0 hardware profile measured; identity repeated across two runs, bandwidth gates remain open.
- Numbers: 4 GB VRAM; SM 8.6; 16 GB RAM; 6C/12T CPU; SSD sample 60.13 write / 138.83 read MB/s; GPU/CPU bandwidth and PCIe application throughput unmeasured.
- Next Experiment: Run supported PCIe inventory and pinned H2D/D2H plus FFN GEMV/GEMM and STREAM helpers; update profile without overwriting prior run artifacts.


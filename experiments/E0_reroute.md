# E0 closure reroute

## Hardware facts and thesis routing

- Measured GPU VRAM: **4,096 MiB**. T2 whole-model-in-VRAM target (5.3 GB) is dormant on this machine. Revisit trigger: a machine with >=6 GB usable VRAM.
- Measured pinned H2D at 16 MiB: approximately **1.85 GiB-equivalent MiB/s** in two retained runs. This is below the pre-registered 8 GB/s T1 cross-bus streaming threshold. T1 is rerouted into T3 on this box: draft/verify split across CPU RAM rather than weight streaming across PCIe.
- Consequence: multicore RAM bandwidth is the single most decision-critical closure number for CPU-resident FFN execution. The measured 16.94 GB/s Triad is a memory benchmark, not ternary-kernel efficiency or end-to-end tok/s. A 1.3 GB hot-row cache does not imply 2× fewer CPU bytes/token; E3.1 must measure row-use/reuse traces, routing cost, and actual RAM traffic before promotion. The valid 10 KiB transfer result does not account for synchronization or 128 layer hops.

## Blocker routes and next experiment

1. **VRAM route:** retain T3 CPU-RAM draft/verify and hot-state GPU placement; alternatively run T2 on a >=6 GB-usable-VRAM machine. Cheapest test: complete the all-core Triad probe and compare its measured median against the 24 GB/s target.
2. **Transfer route:** use CPU-resident weights with hidden-state-only transfers; alternatively test a software/kernel path that improves SM86 transfer scheduling. Cheapest test: 10 KiB pinned H2D/D2H latency plus 256/512 MiB D2D and FFN-shaped GEMV.

## Status / Numbers / Next Experiment
- **Status:** Reroute is recorded as a measured constraint, not a conclusion about the model path.
- **Numbers:** 4,096 MiB VRAM; 16 MiB pinned H2D approximately 1.85 GB/s-equivalent; T1 threshold 8 GB/s; T2 working target 5.3 GB; revisit trigger >=6 GB usable VRAM.
- **Next Experiment:** Run all-core Triad, large-block D2D, FFN GEMV, 10 KiB PCIe latency, and cold SSD probes before acquiring weights.

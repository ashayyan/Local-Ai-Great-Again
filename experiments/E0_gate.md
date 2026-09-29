# E0 Decision Gate

| Requirement | Evidence | Decision |
|---|---|---|
| REQ-E0-01 | `notes/hardware_profile.json`, `experiments/LOG.md` | Partial: GPU/CPU/RAM identity recorded; controlled power/thermal duplicate and SIMD confirmation pending |
| REQ-E0-02 | `notes/hardware_profile.json`, `notes/multicore_triad.json`, `notes/cuda_closure.json`, `notes/latency_ssd.json` | Partial: multicore Triad, 256/512 MiB D2D, valid 10 KiB pinned latency, and 17 GiB SSD sample measured; FFN GEMV and thermal-controlled repeats remain open |
| REQ-E0-03 | `notes/model_compatibility.md`, `notes/model_metadata_followup.md`, `notes/toolchain_selection.json` | Partial: pinned model metadata parsed; official llama.cpp b11259 hash verified; qwen35/GDN load support unverified; 18/18 source shards absent |
| REQ-E0-04 | `experiments/E0_stock_baseline.md`, `experiments/E0_toolchain.md`, `experiments/E0_acquisition_recovery.md` | Open: pinned CLI version/help validated but reports zero CUDA devices; IQ3_S acquisition incomplete; zero inference runs |
| REQ-E0-05 | `experiments/E0_quant_ladder.md` | Open: zero quant tiers measured |
| REQ-E0-06 | `quality/manifest.json` | Partial: 50 eval + 5 calibration prompts, 4 image fixtures; reference outputs/PPL and processor revision pending |
| REQ-LOG-01 | `experiments/LOG.md` | Partial: hardware, manifest, baseline, CPU, and fixture attempts recorded; some early run records lack complete pre-registration or peaks |
| REQ-LOG-02 | `experiments/LOG.md` | Open: no inference measurements |
| REQ-LOG-03 | `scripts/s07_run_e0.ps1`, `scripts/s08_verify_e0_reproduction.ps1`, `notes/E0_headline_table.md` | Partial: six-stage orchestration and structural checks run; no fresh checkout or full-model rerun |

## Blocker routes

- **Constraint:** 4,096 MiB reported GPU VRAM; 0/18 indexed BF16 shards and 0 IQ3_S weights locally present; FFN GEMV unavailable due Numba context failure; valid 10 KiB latency now measured; six-thread Triad median 16.94 GB/s decimal; 17 GiB SSD read 945.51 MiB/s. No full-model speed/quality sample exists.
- **Route A:** Pin source revision, fetch metadata and NVFP4 shards, use compatible stock runtime with CPU/RAM offload.
- **Route B:** Pin compatible GGUF reference and run stock partial offload or CPU-only fallback; preserve model-feature support classification.
- **Cheapest next experiment:** Fetch tokenizer metadata at pinned SHA `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`, rerun `scripts/s02_model_manifest.ps1`; run an FFN-shaped GEMV microbenchmark and repeat pinned transfers at fixed AC/clocks.

## Decision-log corrections (E0 acquisition recovery)
- T2 wholly resident in 4 GiB VRAM is not currently budgeted to fit; T2 remains an active research route and is not proven dead.
- The 16.94 GB/s six-thread Triad is a measured memory benchmark, not ternary-kernel efficiency or end-to-end tok/s.
- A 1.3 GB hot-row cache does not imply 2x fewer CPU bytes/token; require row-use/reuse traces, routing cost, and measured RAM traffic before promoting T3+T4 speed predictions.
- The valid 10 KiB transfer result is useful, but transfer latency alone does not account for synchronization and 128 layer hops.

## Status / Numbers / Next Experiment
- **Status:** E0 gate remains open. Partial hardware/fixture evidence is committed; exact IQ3_S weights are not acquired or SHA-verified, so no load or inference claim is made.
- **Numbers:** 4,096 MiB VRAM, 16 GiB RAM, six-thread Triad 16.94 GB/s decimal, D2D 256/512 MiB 86,971/79,434 MiB/s, 10 KiB round trip 26.2 us, required IQ3_S 12,040,883,104 bytes, target SHA `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`, bounded HTTP range 4.20 MiB/s, prior full-route estimate ~35 KB/s, 0 verified model bytes, 0 reference runs.
- **Next Experiment:** Resume the preserved fastest IQ3_S route for a bounded 5-minute window or copy the exact artifact from a trusted cache/machine; verify byte count and SHA, then run a metadata/load smoke test and two context-2048 TEXT-ONLY stock references.

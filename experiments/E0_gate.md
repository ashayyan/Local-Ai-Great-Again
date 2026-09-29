# E0 Decision Gate

| Requirement | Evidence | Decision |
|---|---|---|
| REQ-E0-01 | `notes/hardware_profile.json`, `notes/driver_record.json`, `experiments/LOG.md` | Evidenced for identity/runtime; non-gating D2D/latency microprobes remain open |
| REQ-E0-02 | `notes/hardware_profile.json`, `notes/multicore_triad.json`, `notes/cuda_closure.json`, `notes/latency_ssd.json` | Evidenced for baseline decision; remaining microprobes are non-gating |
| REQ-E0-03 | `models/qwen3.8-27b-manifest.json`, `notes/model_metadata_followup.md`, `notes/toolchain_selection.json` | Evidenced for verified IQ3_S artifact and pinned runtime path |
| REQ-E0-04 | `experiments/E0_stock_baseline.md`, `experiments/E0_toolchain.md`, `experiments/E0_runtime_cuda124.md`, `experiments/E0_iq3s_routeA.md` | Evidenced: IQ3_S loaded and two baseline measurements are registered; CUDA device enumeration remains separately unresolved |
| REQ-E0-05 | `experiments/E0_quant_ladder.md` | Partial: IQ3_S measured; broader ladder remains open |
| REQ-E0-06 | `quality/manifest.json` | Partial: frozen fixtures exist; full quality scoring remains open |
| REQ-LOG-01 | `experiments/LOG.md` | Evidenced for registered baseline runs; supplied peak fields must be backfilled from raw telemetry if available |
| REQ-LOG-02 | `experiments/LOG.md` | Evidenced for the two supplied performance runs; MTP confirmation is pending |
| REQ-LOG-03 | `scripts/s07_run_e0.ps1`, `scripts/s08_verify_e0_reproduction.ps1`, `notes/E0_headline_table.md` | Partial: baseline is measured; clean-checkout reproduction remains open |

## E0 baseline bar

The measured IQ3_S bar is **1.8 decode tok/s and 10.3 prefill tok/s**, IQ3_S, context 2048, `-ngl 16`, `-ctk q8_0 -ctv q8_0`, seed 7. All E1/E2 theses must report against this bar. The two confirmed ledger entries are E0-baseline-01 and E0-baseline-02; their supplied evidence reports coherent output and intact thinking. Peak VRAM/RAM values are retained as `not supplied in the evidence packet` rather than inferred.

## Runtime root cause

CUDA enumeration is closed as a runtime packaging issue for the pinned b11259 package: the cudart/cublas split-asset DLLs were absent from the primary package and adding `cudart-llama-bin-win-cuda-12.4` is the recorded fix path. The CUDA 12.4 runtime remains the compatible build choice for driver 610.62 / CUDA UMD 13.3; `--list-devices` evidence must still be retained verbatim for any future CUDA claim.

## Acquisition root cause

The single-connection route was approximately 35 KB/s; the legal 16-range aria2 route completed and verified the exact 12,040,883,104-byte artifact at approximately 41 MiB/s transfer display / 28.080344 MiB/s end-to-end including verification.

## Status / Numbers / Next Experiment
- **Status:** E0 is **EVIDENCED** for the measured IQ3_S baseline bar. Remaining D2D/latency/thermal microprobes stay logged-open but are non-gating because the baseline supersedes them as evidence.
- **Numbers:** IQ3_S SHA exact; 12,040,883,104 bytes; baseline 1.8 decode / 10.3 prefill tok/s; 4,096 MiB VRAM; 16 GiB RAM; 16.94 GB/s multicore Triad; driver 610.62.
- **Next Experiment:** Run the pre-registered `llama-bench` `-ngl 0/8/16/24/99`, `-p 512 -n 128`, two repetitions each, with VRAM telemetry; then confirm MTP with paired repeated verbose CLI runs before opening E1.

# E0 Decision Gate

| Requirement | Evidence | Decision |
|---|---|---|
| REQ-E0-01 | `notes/hardware_profile.json`, `notes/driver_record.json`, `experiments/LOG.md` | Evidenced for identity/runtime; non-gating D2D/latency microprobes remain open |
| REQ-E0-02 | `notes/hardware_profile.json`, `notes/multicore_triad.json`, `notes/cuda_closure.json`, `notes/latency_ssd.json` | Evidenced for baseline decision; remaining microprobes are non-gating |
| REQ-E0-03 | `models/qwen3.8-27b-manifest.json`, `notes/model_metadata_followup.md`, `notes/toolchain_selection.json` | Evidenced for verified IQ3_S artifact and pinned runtime path |
| REQ-E0-04 | `experiments/E0_stock_baseline.md`, `experiments/E0_toolchain.md`, `experiments/E0_runtime_cuda124.md`, `experiments/E0_iq3s_routeA.md` | Evidenced: IQ3_S loaded and two baseline measurements are registered; CUDA device enumeration remains separately unresolved |
| REQ-E0-05 | `experiments/E0_quant_ladder.md`, fit-control ledger in `experiments/LOG.md` | Evidenced for IQ3_S quality bar plus IQ2_XXS fit control; IQ2 is not a replacement quality bar |
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

## Fit control

IQ2_XXS is a **fit control**, not a replacement for the IQ3_S quality bar: `Qwen3.8-27B-UD-IQ2_XXS.gguf`, 7,266,070,528 bytes (6.76 GiB), 26.90 B parameters, 2.0625 bpw. At `ngl=16`, context 2048, `pp512/tg128`, r=2 it measured **214.96 ± 3.50 prefill** and **2.64 ± 0.02 decode tok/s**. The matching interactive run measured **17.2 prompt tok/s** and **2.4 generation tok/s**. Bench prefill and interactive prefill are separate evidence classes.

The measured decode reads about 17–19 GB/s, matching the 16.94 GB/s multicore Triad. At that ceiling, 5 tok/s requires approximately 3.8 GB read per token; IQ2's 6.76 GiB is therefore a fit-control data point, not a complete system solution.

The >13 GiB clean `ngl=0` control is **RETIRED**, not failed: normal Windows residency provides about 7–8 GiB free, while IQ3_S itself is 11.2 GiB and cannot be fully resident.

## MTP and maximum offload classification

MTP on IQ2_XXS is **BLOCKED** with exact error: `context type MTP requested but model doesn't contain MTP layers.` The 26.90 B versus 27.32 B parameter gap is supporting evidence. Revisit only with a separate MTP-only GGUF passed through `--spec-draft-model`; do not retry `--spec-type draft-mtp` on IQ2_XXS. `ngl=99` is VRAM-overflow evidence, not an open crash: exit `-1073740791`, CUDA error at `ggml-cuda.cu:109`.

## Status / Numbers / Next Experiment
- **Status:** E0 is **EVIDENCED** for the IQ3_S quality bar and IQ2_XXS fit control; E1 is opened for the RAM-bounded one-shard smoke. Remaining microprobes are non-gating.
- **Numbers:** IQ3_S 1.8 decode / 10.3 prefill; IQ2 2.64 decode / 214.96 bench prefill / 2.4 interactive generation; 16.94 GB/s Triad; 3.8 GB/token at 5 tok/s; 7–8 GiB normal free RAM.
- **Next Experiment:** Run `scripts/s10_e1_layer_smoke.py` on one verified BF16 shard only; no full 55.6 GB load and no local alpha claim.

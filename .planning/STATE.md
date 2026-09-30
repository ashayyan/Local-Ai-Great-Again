---
gsd_state_version: "1.0"
status: unknown
stopped_at: Phase 0.1 context gathered
last_updated: "2026-09-29T14:33:25.853Z"
state_head: 6392c1ffe8bd730cebff9bd1a880371bfdd4db79
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
---

# Project State: Qwen3.8-27B on RTX 3050

**State:** E0 is evidenced with IQ3_S quality bar and IQ2_XXS fit control; E1 is open for the RAM-bounded one-shard smoke. Clean ngl=0 is retired; IQ2 MTP is blocked by missing MTP layers; E3.1 remains scaffolded.
**Mode:** MVP mode.
**Current stage:** Phase 1 / E0 — hardware truth, baseline, and environment capture.
**Strict sequence:** E0 → E1 → E2 → E3 → E4.
**Last transition:** Roadmap and state drafted from project requirements and research set.

## Current position

- E0 baseline evidence is complete for the IQ3_S bar; IQ2_XXS is a fit control only. The broader quant ladder and clean-checkout reproduction remain open.
- E1 is armed with `scripts/s10_e1_layer_smoke.py`; it must stream one verified BF16 shard, stop before 8 GiB RSS, and report FFN fake-quant MSE. The 20-prompt alpha run belongs on Kaggle/TPU.
- Baseline-first remains binding for promotion. E3.1 native activation profiling is explicitly resequenced to run in parallel with E2 because it is an independent evidence probe and now gates the T3/T4 hot-row placement design; no sparse optimization is promoted before its >=1,000-token evidence.
- The full Qwen3.8-27B remains the authoritative generator/verifier; drafts, students, fixtures, and text-only smoke paths cannot substitute for it.

## Evidence required before advancing

1. **E0:** EVIDENCED for IQ3_S quality bar and IQ2_XXS fit control; clean ngl=0 retired, IQ2 MTP blocked, ngl=99 classified overflow evidence.
2. **E1:** 200-prompt agreement, authoritative verifier/state correctness, alpha/quality decision, and explicit forks for failed routes.
3. **E2:** exact sm_86 kernels, AVX2 and transfer accounting, stock-offload then tiered placement traces, and numerical/end-to-end promotion decision.
4. **E3:** native activation evidence from ≥1,000 tokens, controlled sparse tests, and measured sparsity decision or fallback.
5. **E4:** unpruned visual prefill, verified eviction/state preservation, pruning/recovery comparison, full quality/performance acceptance, and decision-gate closure table.

## Active constraints and conditional forks

- Measured local hardware: RTX 3050 Laptop, 4,096 MiB VRAM, CC 8.6, i5-11400H 6C/12T, 16 GiB RAM. T2 whole-model-in-VRAM (5.3 GB target) is dormant here with revisit trigger >=6 GB usable VRAM. Pinned H2D ~1.85 GB/s-equivalent is below the 8 GB/s T1 threshold, so T1 merges into T3 CPU-RAM draft/verify. Multicore Triad measured 16.94 GB/s decimal median against a 24 GB/s target; closure probes remain open.
- If a loader or runtime lacks GDN, MTP, vision, or untied-head correctness, stop the affected comparison and use a pinned compatible runtime, WSL2, or a fixture/fork while recording the missing component.
- E1 promotion requires k=4 α≥0.6; α<0.4 requires layer-wise healing and remeasurement; intermediate alpha requires a documented comparison.
- Three failures on one route require a fork or dormant note with a measurable revisit trigger.
- E2 paging must be measured against stock partial offload; E3 sparsity must be measured before exploitation; E4 pruning must retain recovery/no-prune fallback.

## Required run record

Every attempt, including failure, must be pre-registered in `experiments/LOG.md` and machine-readable form with: hypothesis and numeric target, unique UTC run ID, one changed variable, exact command/script and commit, model/quant hashes, context and seed, warmups/repetitions, prefill/decode/TTFT, VRAM/RAM peaks, temperature/power and SSD/PCIe telemetry where applicable, quality output, failure evidence, and cheapest next experiment.

## Next experiment

Run `llama-bench` at `-ngl 0/8/16/24/99`, `-p 512 -n 128`, two repetitions per point, recording decode/prefill and VRAM telemetry. Then rerun baseline and `--spec-type draft-mtp` twice each at `-n 128 --verbose` to prove or reject MTP engagement. E1 opens after those pre-registered controls.

## Status / Numbers / Next Experiment

- **Status:** E0 **EVIDENCED** for IQ3_S quality bar and IQ2_XXS fit control; E1 opened for the one-shard smoke. Clean ngl=0 is retired, IQ2 MTP is blocked, and ngl=99 is classified VRAM-overflow evidence.
- **Numbers:** IQ3_S 1.8 decode / 10.3 prefill; IQ2 2.64 ± 0.02 bench decode / 2.4 interactive generation / 214.96 ± 3.50 bench prefill; 16.94 GB/s Triad; 3.8 GB/token needed at 5 tok/s; normal free RAM 7–8 GiB; CPU AVX2/AVX-512/BMI2.
- **Next Experiment:** Verify one BF16 shard, then run `python scripts/s10_e1_layer_smoke.py <shard>`; never load the full 55.6 GB BF16 model locally.

## Session

**Last session:** 2026-09-29T14:33:25.819Z
**Stopped at:** Phase 1 context gathered
**Resume file:** .planning/phases/01-e0-baseline/01-CONTEXT.md

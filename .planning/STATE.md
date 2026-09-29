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

**State:** Phase 1/E0 closure execution in progress; structural and hardware probes are partially evidenced, model baseline remains open.
**Mode:** MVP mode.
**Current stage:** Phase 1 / E0 — hardware truth, baseline, and environment capture.
**Strict sequence:** E0 → E1 → E2 → E3 → E4.
**Last transition:** Roadmap and state drafted from project requirements and research set.

## Current position

- No experiment is complete and no result is promoted.
- The immediate next action is the E0 hardware probe and its rerun, followed by the pinned model compatibility inventory.
- Baseline-first is binding: no custom kernel, model surgery, speculative speed claim, sparsity optimization, or multimodal pruning work advances ahead of its prerequisite gate.
- The full Qwen3.8-27B remains the authoritative generator/verifier; drafts, students, fixtures, and text-only smoke paths cannot substitute for it.

## Evidence required before advancing

1. **E0:** measured hardware identity/bandwidth, complete artifact compatibility, deterministic stock/reference path, frozen quality suite, stock quantization ladder, and fresh-checkout reproduction.
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

Run the pinned hardware probe (GPU identity/SM/VRAM, driver/CUDA/toolchain, CPU/SIMD, RAM, SSD, PCIe, clocks/power and bandwidth/transfer medians) twice. Then run the deterministic stock/reference smoke path at context ≥2048 where resources permit. Expected output is a measured, rerunnable report and either finite reference outputs or a numerically classified failure with at least two routes and a cheapest command. Do not begin E1 until E0 gates are evidenced.

## Status / Numbers / Next Experiment

- **Status:** E0 closure remains open; hardware/metadata/fixture evidence exists, but no full-model output has been produced.
- **Numbers:** 4,096 MiB VRAM; 16 GiB RAM; CPU Triad 16.94 GB/s decimal median (6 threads); pinned H2D ~1.85 GB/s-equivalent at 16 MiB; FFN GEMV unavailable due Numba context IndexError; primary GGUF IQ3_S 12.0 GB, IQ3_XXS 10.9 GB, IQ2_XXS 7.3 GB; Q4 marked unavailable-resource.
- **Next Experiment:** Complete all-core/large-block/10 KiB/SSD probes, pin or obtain llama.cpp qwen35/MTP runtime, then run IQ3_S at context 2048 twice or record exact loader/resource failure.

## Session

**Last session:** 2026-09-29T14:33:25.819Z
**Stopped at:** Phase 1 context gathered
**Resume file:** .planning/phases/01-e0-baseline/01-CONTEXT.md

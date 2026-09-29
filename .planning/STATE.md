# Project State: Qwen3.8-27B on RTX 3050

**State:** Planning complete; execution not started.
**Mode:** MVP mode.
**Current stage:** E0 Phase 0.1 — hardware truth and environment capture.
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

- Actual VRAM, bandwidth, PCIe, RAM, SSD, power, clocks, driver, CUDA and SIMD are unknown until E0; all research numbers are hypotheses or derived estimates.
- If a loader or runtime lacks GDN, MTP, vision, or untied-head correctness, stop the affected comparison and use a pinned compatible runtime, WSL2, or a fixture/fork while recording the missing component.
- E1 promotion requires k=4 α≥0.6; α<0.4 requires layer-wise healing and remeasurement; intermediate alpha requires a documented comparison.
- Three failures on one route require a fork or dormant note with a measurable revisit trigger.
- E2 paging must be measured against stock partial offload; E3 sparsity must be measured before exploitation; E4 pruning must retain recovery/no-prune fallback.

## Required run record

Every attempt, including failure, must be pre-registered in `experiments/LOG.md` and machine-readable form with: hypothesis and numeric target, unique UTC run ID, one changed variable, exact command/script and commit, model/quant hashes, context and seed, warmups/repetitions, prefill/decode/TTFT, VRAM/RAM peaks, temperature/power and SSD/PCIe telemetry where applicable, quality output, failure evidence, and cheapest next experiment.

## Next experiment

Run the pinned hardware probe (GPU identity/SM/VRAM, driver/CUDA/toolchain, CPU/SIMD, RAM, SSD, PCIe, clocks/power and bandwidth/transfer medians) twice. Then run the deterministic stock/reference smoke path at context ≥2048 where resources permit. Expected output is a measured, rerunnable report and either finite reference outputs or a numerically classified failure with at least two routes and a cheapest command. Do not begin E1 until E0 gates are evidenced.

## Status / Numbers / Next Experiment

- **Status:** Planning artifacts created; experiments remain unrun.
- **Numbers:** E0–E4 order; context ≥2048; 50-prompt frozen text suite; 200-prompt E1 agreement; k=4 α≥0.6 promotion and α<0.4 healing branch; ≥1,000 E3 activation tokens; initial quality delta ≤+15% PPL; ≥3 tok/s ambition and ≥5 tok/s project target.
- **Next Experiment:** E0 hardware probe and deterministic reference smoke test, logged before execution.

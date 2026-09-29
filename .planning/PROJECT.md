# Qwen3.8-27B on an RTX 3050 Laptop

## What This Is

A reproducible lab project to run the complete Qwen/Qwen3.8-27B multimodal model on the local RTX 3050 laptop through measured quantization, kernel, memory-tier, sparsity, and speculative-decoding experiments. The project turns the research theses T1–T5 into falsifiable engineering routes, with hardware truth and reference baselines established before invention work.

## Core Value

Demonstrate a reproducible full-model inference path at or above 5 decode tok/s with 4-bit-equivalent quality on the actual RTX 3050 laptop, while preserving multimodal behavior and reporting every constraint as measured data plus next experiments.

## Requirements

### Validated

(None yet — experiments establish validation.)

### Active

- [ ] Measure the real laptop hardware and replace all assumed bandwidth, VRAM, PCIe, RAM, SSD, driver, and CUDA figures.
- [ ] Establish stock NVFP4/reference inference and quality baselines before invention code.
- [ ] Execute E0–E4 in the prescribed order, logging hypotheses, commands, model/quant/context, peaks, speeds, quality, and failures.
- [ ] Kill/confirm T1 ternary-draft agreement and branch to healing or T2 when gates require it.
- [ ] Kill/confirm T2/T3 kernel and memory-tier routes with representative FFN benchmarks on sm_86 and AVX2 CPU.
- [ ] Measure activation sparsity for T4 and ViT eviction/prefill effects for T5.
- [ ] Produce a reproducible Phase 3 prototype for the winning route and a fixed-prompt quality gate.

### Out of Scope

- [ ] Silent abandonment of a route after failed runs — prohibited by the experiment protocol.
- [ ] Presenting a small distilled model as the answer — the full Qwen3.8-27B remains the verifier and quality reference.
- [ ] Cloud compute as the final deployment answer — free/borrowed compute may be used only for explicitly documented experiments or training requests.
- [ ] Unmeasured claims based only on assumed RTX 3050 SKU specifications.

## Context

The governing documents are `AGENTS.md` and `Deep Research  27B on RTX 3050.md`. The target architecture has 64 layers: 48 Gated DeltaNet linear-attention layers and 16 full gated-attention layers, 17.1B FFN parameters, an untied 1.27B lm_head, a roughly 0.4B vision tower, and one native MTP layer. The research estimates 25.6B streamed parameters/token and ranks five theses: T1 scalable-codec self-speculation, T2 BitDistill/Sherry/QTIP whole-model ternary, T3 CPU/GPU ternary split, T4 virtual-texturing sparsity, and T5 precision-per-subsystem VLM.

All experiment reports end with **Status / Numbers / Next Experiment**. Failures are first-class evidence. Three failures on one route require a written dormant note and a fork.

## Constraints

- **Hardware:** Actual RTX 3050 laptop, unknown SKU until E0; measure rather than assume 4/6/8 GB VRAM, bandwidth, SM count, PCIe, CPU, RAM bandwidth, SSD, driver, and CUDA.
- **Performance:** Target >=5 decode tok/s; initial reference threshold is documented after the first working baseline.
- **Quality:** Full model must remain coherent and instruction-following at context >=2048, with a fixed eval/perplexity delta documented against the reference.
- **Budget:** E1 strategy target is $0; use local CPU/GPU, free compute, or a documented compute request.
- **Reproducibility:** Every number cites a numbered script and commit/hash; models live under `/models` and are never committed.
- **Experiment discipline:** Hypothesis and numeric target precede each run; one variable changes per experiment; exact command and memory/speed measurements are mandatory.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Run E0 hardware truth before optimization | SKU assumptions determine all thesis math | — Pending |
| Establish stock/reference baselines before invention | Every thesis must beat a measurable bar | — Pending |
| Execute E0–E4 in queue order with explicit gates | Preserves the research protocol and prevents premature kernel work | — Pending |
| Treat T1 alpha >= 0.6 as the promotion gate | Cheapest kill/confirm test for quality-by-construction self-speculation | — Pending |
| Keep full-model verification authoritative | Distillation/drafting can accelerate but cannot replace final model behavior | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-29 after project initialization*

---
status: gaps_found
phase: 01-hardware-truth-baseline-and-reproduction-e0
verified: 2026-09-30
verifier: gsd-validate-phase
requirements: REQ-E0-01, REQ-E0-02, REQ-E0-03, REQ-E0-04, REQ-E0-05, REQ-E0-06, REQ-LOG-01, REQ-LOG-02, REQ-LOG-03
---

# Phase 01 Verification — Hardware Truth, Baseline, and Reproduction (E0)

## Scope and conclusion

This is an artifact-only verification. No model, experiment, or source/model-file command was run. The phase has useful measured and structural evidence, but the E0 gate is **not closed**. The correct status is `gaps_found`: several requirements remain open or only partially evidenced, and later-stage evidence cannot substitute for missing E0 artifacts.

The `01-UAT.md` document reports five inspection checks as passed, but those checks establish honest reporting and fixture presence; they do not establish all E0 requirements. In particular, the UAT itself says that full-model scoring and clean-checkout/full-model reproduction remain unclaimed.

## Must-have verification

| Requirement | Must-have check | Evidence inspected | Result |
|---|---|---|---|
| REQ-E0-01 | Two rerunnable identity probes with stable GPU identity and variance report, including toolchain, clocks/power, CPU/SIMD, RAM, SSD, PCIe and timestamp/command context | `notes/hardware_profile.json`, `notes/hardware_profile.md`, `01-01-SUMMARY.md`, `experiments/LOG.md` | **Partial / gap.** GPU (RTX 3050 Laptop, 4096 MiB, CC 8.6, driver 610.62), CPU/RAM, PCIe Gen2 x8 and timestamps are evidenced. The summary explicitly leaves GPU copy/GEMV/GEMM, pinned H2D/D2H, multicore STREAM closure, AVX2 confirmation, process peaks and thermal-repeat controls pending. The report also labels the SSD sample cache-affected. No complete two-run variance package is demonstrated by the current canonical report. |
| REQ-E0-02 | Device, RAM, host-device, SSD and available-memory limits measured with repetitions/medians and decision-critical bandwidth probes | `notes/E0_headline_table.md`, `notes/gpu_transfer*.json`, `notes/multicore_triad.json`, `notes/latency_ssd.json`, `notes/hardware_profile.md` | **Partial / gap.** D2D and pinned H2D figures, 16.94 GB/s multicore Triad, and latency/SSD artifacts exist, but the canonical profile still marks several probes unavailable and the summaries identify missing large-block D2D, 10 KiB latency and cold SSD evidence. Cached/single-sample SSD values are not a sustained cold-throughput gate. |
| REQ-E0-03 | Immutable source revision and SHA-256 coverage for all required model components; architecture and unsupported loader components classified without silent omission | `models/qwen3.8-27b-manifest.json`, `notes/model_compatibility.md`, `01-02-SUMMARY.md` | **Gap.** The manifest says source revision is unresolved, tokenizer/processor revisions are unresolved, model path has zero source files, and all eight component classes are missing. A disposable metadata fixture was explicitly not model evidence. Later IQ3_S GGUF hash notes do not replace the required complete language/embedding/head/GDN/attention/vision/processor/tokenizer/MTP manifest. |
| REQ-E0-04 | Pinned deterministic complete stock/reference path at context >=2048, with coherent output, timings, memory peaks, and explicit multimodal classification | `experiments/raw/stock/run.json`, `experiments/E0_stock_baseline.md`, `experiments/E0_gate.md`, `experiments/LOG.md`, `01-03-SUMMARY.md` | **Gap / conflicting partial evidence.** The planned stock runner's structured record is `blocked-no-weights` with zero local model files and null quality, prefill/decode and VRAM/RAM peaks. The ledger contains a separately supplied IQ3_S text bar (1.8 decode / 10.3 prefill at context 2048), but its peak fields are explicitly not supplied and no complete multimodal baseline is shown. Therefore a complete E0 stock/reference requirement is not verified. |
| REQ-E0-05 | Matched Q4/NVFP4, Q3/IQ3 and Q2/IQ2 ladder, one variable per run, with bytes/load/TTFT/speeds/peaks/quality and unsupported evidence | `experiments/E0_quant_ladder.md`, `quality/quant_ladder/ladder.json`, `01-04-SUMMARY.md` | **Gap.** All three ladder tiers are recorded as unavailable/no matching weights with null measurements; no tier has a matched quality comparison. The IQ3_S and IQ2_XXS measurements in the ledger are useful route evidence (IQ2 is explicitly a fit control), but they do not provide the required frozen quality ladder. |
| REQ-E0-06 | Frozen 50-prompt text suite, disjoint calibration/evaluation inputs, multimodal OCR/charts/spatial/multistep fixtures, reference outputs and score | `quality/manifest.json`, `quality/prompts/*`, `quality/images/*`, `01-04-SUMMARY.md`, `experiments/E0_quant_ladder.md` | **Partial / gap.** 50 evaluation prompts, 5 calibration prompts, disjoint IDs/hashes and four image categories are present. There are zero model outputs and no PPL/comparable score; multimodal behavior is unmeasured. |
| REQ-LOG-01 | Every attempt pre-registered with unique ID, hypothesis/target, exact command, one changed variable, hashes, environment, context/seed | `experiments/LOG.md`, numbered scripts and reports | **Partial.** Many ledger entries contain hypotheses, commands, IDs and numeric results, including failures. The E0 gate notes missing/backfill peak fields; the clean-checkout artifact is structural only. A complete requirement-wide audit of machine-readable records is not evidenced. |
| REQ-LOG-02 | Warmups/repetitions, phase-separated speed/latency, memory/telemetry, quality/failure evidence and cheapest next test | `experiments/LOG.md`, `notes/E0_headline_table.md`, raw experiment artifacts | **Partial / gap.** Several runs have repeated benchmark values and failure routes, but the blocked baseline has null peaks and the confirmed IQ3_S bar lacks supplied VRAM/RAM peaks. MTP confirmation remains pending in the log. |
| REQ-LOG-03 | Fresh-checkout rerun regenerates E0 artifacts from numbered scripts with pinned external assets and no hand-edited paths | `experiments/e0_runs/clean-checkout.json`, `scripts/s07_run_e0.ps1`, `scripts/s08_verify_e0_reproduction.ps1`, `01-05-SUMMARY.md` | **Gap.** Structural check is `status: partial`, `complete: false`, `model_reproduced: false`; note explicitly says no actual fresh clone, model rerun or E0 gate pass. |

## Evidence strengths

- Hardware identity is locally measured rather than assumed: RTX 3050 Laptop, 4096 MiB reported VRAM, compute capability 8.6, driver 610.62, i5-11400H 6C/12T, 16 GiB RAM and PCIe Gen2 x8.
- The repository preserves honest failure records rather than fabricating a baseline: the stock run reports `blocked-no-weights`, zero model files and null performance/quality fields.
- Frozen fixture scaffolding is substantive: 50 evaluation prompts, 5 calibration prompts, four hashed SVG categories (OCR, charts, spatial, multistep).
- Structural E0 orchestration exists and records six stages with no missing scripts, but its own JSON correctly says `model_reproduced=false`.
- The separately recorded IQ3_S bar (1.8 decode / 10.3 prefill at context 2048) and IQ2_XXS fit-control measurements are route evidence, not sufficient proof of the complete E0 gate.

## Gaps and risks

1. Complete model artifact provenance remains unresolved in the canonical manifest: no immutable source revision, tokenizer/processor revision, full shard/index evidence or complete component checksums.
2. A deterministic complete stock reference is not reproduced in the phase-owned baseline artifact; the primary runner is blocked and multimodal behavior is not measured.
3. No Q4/NVFP4, Q3/IQ3 and Q2/IQ2 matched quality ladder exists; all ladder rows are unavailable in `ladder.json`.
4. Frozen fixtures have no reference outputs or quality/PPL scores.
5. Hardware bandwidth/availability evidence is mixed across follow-up notes and the canonical profile; cold SSD, full transfer/GEMV/GEMM and repeat/thermal variance closure are not all present.
6. Run-contract evidence is incomplete for peak memory/telemetry and pending MTP controls.
7. Reproduction is structural rather than a genuine clean-checkout regeneration; therefore no fresh-checkout claim is valid.
8. `experiments/E0_gate.md` uses “EVIDENCED” language for some IQ3_S/route bars, but its own rows and the plan summaries retain open requirements. This verification treats the more specific raw/structured evidence and explicit nulls as authoritative and does not promote E0 to complete.

## Required next actions

1. Resolve and record an immutable Qwen source revision; acquire/hash metadata and all required model component classes, including tokenizer/processor, untied head/embeddings, GDN/full-attention, vision and MTP. Re-run the manifest and compatibility classification.
2. Pin the runtime and model artifact used for the IQ3_S result, retain raw stdout/stderr and exact command, and reproduce a deterministic context-2048 text run with VRAM/RAM peak telemetry plus one explicitly classified multimodal attempt.
3. Complete the matched Q4/NVFP4, Q3/IQ3 and Q2/IQ2 ladder with fixed settings and one variable (quantization) changed per run; preserve unavailable/failure evidence where unsupported.
4. Run the frozen suite to produce reference outputs and a declared text score/PPL plus OCR/chart/spatial/multistep multimodal results. Do not treat fixture existence as quality evidence.
5. Reconcile hardware artifacts: perform the remaining repeated cold SSD, transfer, FFN-shaped GEMV/GEMM, available-memory and thermal/power measurements and update the canonical report with medians, repetitions and variance.
6. Backfill every applicable ledger record with peaks, warmups/repetitions and phase-separated timing; finish or explicitly classify the pending MTP control.
7. Perform a real fresh-clone/worktree rehearsal using the numbered scripts and external asset hashes. Update `experiments/e0_runs/clean-checkout.json` only from that rehearsal, then revise `experiments/E0_gate.md` to show each requirement as pass, partial, fork or open.
8. Keep E1/E2 advancement gated on these unresolved E0 items; E1 alpha, one-shard smoke and E3 activation scaffolding cannot substitute for E0 completion.

## Verification Complete

- **Status:** `gaps_found` — Phase 01/E0 remains open; no full E0 completion claim.
- **Artifact:** `.planning/phases/01-hardware-truth-baseline-and-reproduction-e0/01-VERIFICATION.md`

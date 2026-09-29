# Requirements: Qwen3.8-27B on an RTX 3050 Laptop

**Defined:** 2026-09-29
**Core value:** A reproducible, complete Qwen/Qwen3.8-27B text-and-image inference path on the actual RTX 3050 laptop, targeting ≥5 sustained decode tokens/s with quality compared against a trusted full-model reference.
**Order of execution:** E0 hardware and reference → E1 agreement and route decisions → E2 kernels and memory tiers → E3 measured sparsity → E4 multimodal staging and final acceptance. Later-stage work does not substitute for an earlier gate. Names for E1–E4 in tooling research differ; the experiment order and gates in this document govern milestone acceptance.

## v1 Requirements

### E0 — Hardware truth and stock reference

- [ ] **REQ-E0-01 — Measured hardware identity:** A rerunnable probe records the actual GPU SKU, VRAM capacity, SM capability, driver/CUDA/toolchain, power/clocks, CPU/SIMD, RAM, SSD and PCIe link, with timestamp, command, script revision and environment identifier; a second run reproduces identity and reports measurement variance. Assumed SKU specifications are never reported as measured.
- [ ] **REQ-E0-02 — Bandwidth and memory truth:** Probe device bandwidth, CPU RAM bandwidth, pinned/pageable host-device transfer bandwidth and latency, SSD cold/warm throughput, and available VRAM/RAM under the documented power/thermal state; report units, repetitions and medians so subsequent route budgets can use measured limits. Closure reroute: measured 4,096 MiB VRAM makes T2 whole-model-in-VRAM (5.3 GB) dormant on this machine; revisit at >=6 GB usable VRAM. Measured pinned H2D ~1.85 GB/s is below the 8 GB/s T1 cross-bus threshold; T1 therefore merges into T3 CPU-RAM draft/verify on this box. Multicore RAM bandwidth is the decision-critical closure probe. Closure status: multicore managed Triad measured at 16.94 GB/s decimal median against the 24 GB/s hypothesis; large-block D2D, 10 KiB latency, and cold SSD remain open.
- [ ] **REQ-E0-03 — Complete-model artifact:** Pin and checksum the source model revision and all required language, untied embedding/head, GDN/attention, vision, processor/tokenizer and native MTP artifacts; verify architecture against model configuration and classify unsupported loader components rather than silently dropping them. Technical finding to record before baseline: NVFP4 GGUF inference requires sm_120 Blackwell CUDA kernels in the candidate path; this machine is sm_86. Missing piece: software NVFP4-to-SM86 kernel path. Status: dormant, not adopted as stock baseline. The minima-ai NVFP4 checkpoint remains the E1 quality teacher on documented free/borrowed compute.
- [ ] **REQ-E0-04 — Stock/reference baseline:** Before custom kernels or model surgery, run a deterministic, version-pinned full-model FP16/BF16 path where available or explicitly identified stock NVFP4/4-bit reference with CPU/RAM offload as needed; record a coherent instruction-following sample at context ≥2048 and distinguish any text-only compatibility smoke test from a complete multimodal baseline.
- [ ] **REQ-E0-05 — Stock quantization ladder:** Benchmark supported stock Q4/NVFP4, Q3/IQ3 and Q2/IQ2 levels (mark unsupported levels with reproducible evidence), changing one variable per run; table model bytes, load time, peak VRAM/RAM, prefill/decode tok/s, TTFT, context, quality and outputs. Compare forks only at matched model, quant, settings and model-feature correctness.
- [ ] **REQ-E0-06 — Frozen quality reference:** Freeze and hash a 50-prompt instruction suite, disjoint calibration/evaluation inputs, text PPL or comparable score, and a multimodal suite covering OCR, charts, spatial and multistep reasoning. Preserve processor/tokenizer revision, images, seeds, reference outputs, scoring scripts and raw results under `quality/`.

### E0–E4 — Reproducibility and experiment contract

- [ ] **REQ-LOG-01 — Pre-registered run:** Every E0–E4 attempt, including failure, starts with hypothesis and numeric target and logs a unique run ID, UTC time, exactly one changed variable, exact command/script and commit, environment, model/quant/hash, context, prompt-set revision and seed in `experiments/LOG.md` plus machine-readable data.
- [ ] **REQ-LOG-02 — Auditable measurements:** Every applicable run records warmups/repetitions, phase-separated prefill and sustained decode tok/s, TTFT/latency, VRAM allocated/reserved and device peak, RAM peak, temperature/power where available, SSD/PCIe traffic where relevant, quality score/sample, failure evidence and a cheapest next test. Classify each number as measured, derived, externally reported or hypothesis.
- [ ] **REQ-LOG-03 — Fresh-checkout rerun:** Numbered scripts and pinned model/runtime revisions fetch or checksum external assets and regenerate the headline table and evaluation from a clean checkout with no hand-edited paths. Keep large models and generated runtime binaries outside version control; report unavailable assets or hardware explicitly.

### E1 — Agreement and forks, after E0 baseline

- [ ] **REQ-E1-01 — Offline agreement:** Compare a ternary/base candidate against the trusted full-model NVFP4/4-bit verifier on 200 fixed held-out prompts, with greedy and k=4 draft settings; report tokenizer identity, per-token agreement, acceptance α and accepted-length distribution, stratified failures and logit/KL or PPL deltas with raw outputs.
- [ ] **REQ-E1-02 — Authoritative verification:** Draft tokens become final only through a tested verifier/rejection algorithm whose final distribution or seeded deterministic behavior matches the full 27B verifier; test recurrent GDN/KV reset and tokenizer/RNG correctness, and do not label a low-bit draft's output as full-model quality.
- [ ] **REQ-E1-03 — Explicit E1 decision:** Promote T1 agreement only when measured k=4 α≥0.6 and quality is acceptable; at α<0.4 run and remeasure layer-wise healing/distillation before route judgment; for intermediate α document a follow-up comparison. Measure end-to-end tok/s and latency separately from α before claiming speedup.
- [ ] **REQ-E1-04 — Route forks:** For every failed gate document the exact numeric constraint, at least two engineering routes and cheapest next experiment (command and expected measurable result); after three failures on the same route, record a fork or a `dormant because` note with a measurable revisit trigger. Capture stock/fork runtime compatibility and quality failures without skipping E1 evidence.

### E2 — Representative kernels and memory tiers, after E1 decision

- [ ] **REQ-E2-01 — Correct sm_86 kernel probes:** Verify actual GPU architecture and benchmark real FFN 17408×5120/5120×17408 shapes at M=1,4,8,16 plus representative GDN, attention and untied head projections; compare available ternary W1.58A8, structured 1.25-bit, 2–2.5-bit and stock 4-bit candidates with FP16 reference. Report packing bytes, numerical error, effective bandwidth, occupancy when accessible, warm kernel time and end-to-end effect; unsupported formats remain explicitly marked.
- [ ] **REQ-E2-02 — CPU split and transfer accounting:** On the measured CPU SIMD path (AVX2 unless a verified alternative), benchmark FFN GEMV against scalar correctness and measured STREAM, then test CPU/GPU split with hidden-state-only pinned transfers, synchronization and overlap times; treat ≥70% STREAM as a probe target, not an assumed result.
- [ ] **REQ-E2-03 — Measured placement and streaming:** Test stock partial offload before custom hot-VRAM/warm-RAM/cold-SSD paging, log actual tensor locations, copy/page-fault traces, cold/warm decode, state/KV residency and no silent eviction. Promote pipelining only if measured end-to-end latency/memory improves over the matched E0 stock run at context ≥2048 within quality tolerance.
- [ ] **REQ-E2-04 — Kernel promotion:** A candidate must pass declared numerical tolerance versus a reference, preserve output quality, and demonstrate repeatable end-to-end improvement; published desktop GPU/AVX-512 results and payload-only bandwidth calculations do not satisfy this gate.

### E3 — Measure then exploit sparsity, after E2 probes

- [ ] **REQ-E3-01 — Activation evidence:** Measure native SiLU/SwiGLU activation magnitudes on ≥1,000 representative tokens; report per-layer/neuron and prompt-category distributions, top-k mass and inactive fraction. Treat dReLU and claimed sparsity fractions as hypotheses requiring separate tests.
- [ ] **REQ-E3-02 — Controlled sparsity tests:** Compare at least static hot/cold placement and activation-aware paging or structured 3:4 ternary sparsity against the dense full-model reference using the frozen suite; log bytes read/token, page hit/fault rates, RAM/SSD traffic, decode speed and adversarial-prompt quality. Any dReLU conversion requires healed/evaluated model outputs before promotion.
- [ ] **REQ-E3-03 — Sparsity decision:** Promote a sparse path only for measured byte/time reduction within the agreed text quality delta; otherwise retain statistics and document a fork to mixed precision or memory-tier tuning with a revisit trigger.

### E4 — Complete image-text behavior, after E3 decision

- [ ] **REQ-E4-01 — Native visual prefill:** Run the pinned native processor and complete vision tower at BF16 or declared reference precision; report image preprocessing, visual-token count, visual phase latency, peak VRAM and reference quality for OCR, charts, spatial and multistep prompts.
- [ ] **REQ-E4-02 — Verified temporal eviction:** Synchronize after visual prefill, release/evict vision weights and temporary activations before language decode, and use allocator plus device-free-memory telemetry to demonstrate recovered usable VRAM; preserve projected visual embeddings and required GDN/KV state and check decoded image-text outputs.
- [ ] **REQ-E4-03 — Pruning and recovery comparison:** Compare no visual pruning with dynamic token-pruning and explicit recovery/no-prune fallback on the frozen multimodal suite; report retained tokens and per-category accuracy, not merely aggregate speed. Reject or fork pruning that loses task-critical content.

### E0–E4 — Completion and decision documentation

- [ ] **REQ-GATE-01 — Full-model quality:** Final text and image-text runs retain the complete 27B model as the authoritative generator/verifier at context ≥2048, are coherent and instruction-following, and report 50-prompt text plus multimodal scores against the pinned reference. Initial target is ≤+15% relative PPL increase or a predeclared comparable fixed-suite score delta; any changed threshold is justified and recorded before the candidate evaluation.
- [ ] **REQ-GATE-02 — Interactive performance:** On the measured laptop SKU, report warm sustained decode tok/s separately from prefill, TTFT and load time, with peak VRAM/RAM and SSD/PCIe traffic. Initial interactive ambition is ≥3 decode tok/s; project success target is ≥5 decode tok/s while passing REQ-GATE-01 and REQ-LOG-03. A missed target is reported numerically with forks and next experiment, never silently relabeled as success.
- [ ] **REQ-GATE-03 — Decision-gate record:** Publish an E0→E1→E2→E3→E4 gate table listing prerequisites, reference/candidate artifact hashes, measured evidence, pass/fork/dormant decision, constraint, ≥2 candidate routes where blocked, revisit trigger and next reproducible command. Distinguish measured outcomes from hypotheses and record any unresolved gate before claiming v1 completion.

## v2 Requirements — Advanced prototype work, deferred until v1 evidence

- [ ] **REQ-V2-01:** Build and evaluate a scalable-codec self-speculative full-model prototype with GPU ternary base, RAM enhancement residual, verifier-equivalent rejection sampling and optional native MTP; demonstrate measured wall-time benefit, not acceptance alone.
- [ ] **REQ-V2-02:** Explore full 27B BitDistill/QAT/healing, Sherry-style 1.25-bit FFNs, QTIP/AQLM mixed precision, nested/base-plus-enhancement representations and learned per-subsystem bit allocation, conditional on E1/E2 quality and kernel evidence.
- [ ] **REQ-V2-03:** Implement learned hot-page prediction, virtual-texturing neuron cache, dynamic recovery and trained dReLU only after E3 establishes natural sparsity and fixed-suite reference behavior.
- [ ] **REQ-V2-04:** Develop specialized fused sm_86 CUDA and AVX2 CPU kernels, tier scheduling, speculative tree/EAGLE/QSpec integration, long-context/KV optimization and server/batching/power autotuning after matched microbenchmarks and baseline reproduction.
- [ ] **REQ-V2-05:** Advance precision-per-subsystem VLM and aggressive visual-token pruning only after unpruned E4 image correctness and eviction are verified; measure modality-specific recovery.

## Out of Scope

| Item | Reason |
|------|--------|
| A small distilled or pruned student as the final answer | The complete 27B checkpoint or clearly identified full-model quantized representation must determine final behavior. |
| Cloud compute as final deployment | The acceptance machine is the actual RTX 3050 laptop; borrowed/free compute may support explicitly logged training or experiments only. |
| Claims of measured throughput, hardware fit, exact speculative distribution, sparsity, or eviction from research estimates alone | Such claims require hashed artifacts, correct runtime behavior and local telemetry. |
| Silent route abandonment, changing multiple variables in a comparison, or unlogged failed runs | These destroy falsifiability and reproducibility. |
| Full-model QAT, production serving, extreme context, and trained custom sparsification as v1 acceptance prerequisites | v1 validates the staged evidence and preserves these as conditional v2 prototype work. |

## Traceability / execution sequence

| Gate | Required v1 IDs | Decision before advancing |
|------|-----------------|---------------------------|
| E0 — hardware and stock reference | REQ-E0-01–06; REQ-LOG-01–03 | Hardware, complete model compatibility, fixed quality suite and first reference measured. |
| E1 — agreement and forks | REQ-E1-01–04; REQ-LOG-01–03 | α/quality and authoritative-verifier decisions recorded; unsuccessful routes forked. |
| E2 — kernels and memory | REQ-E2-01–04; REQ-LOG-01–03 | Numerical correctness and matched end-to-end result measured before integration. |
| E3 — sparsity | REQ-E3-01–03; REQ-LOG-01–03 | Natural activation statistics precede sparse optimization and quality decision. |
| E4 — VLM and closure | REQ-E4-01–03; REQ-GATE-01–03; REQ-LOG-01–03 | Eviction, full-model multimodal fidelity, speed and fresh-checkout reproduction accepted or explicitly unresolved. |

## Traceability / roadmap coverage

Each v1 requirement is mapped exactly once to one MVP roadmap phase. Shared experiment-contract requirements are split across E0 (definition and clean rerun) and then applied operationally to every later phase without duplicating ownership in the roadmap.

| Requirement | Sole roadmap owner | Observable coverage |
|---|---|---|
| REQ-E0-01 | Phase 0.1 | Identity probe and rerun variance |
| REQ-E0-02 | Phase 0.1 | Bandwidth/transfer/SSD/RAM medians |
| REQ-E0-03 | Phase 0.2 | Complete artifact manifest and compatibility classification |
| REQ-E0-04 | Phase 0.3 | Deterministic stock/reference text and multimodal status |
| REQ-E0-05 | Phase 0.4 | Matched Q4/Q3/Q2 ladder and unsupported evidence |
| REQ-E0-06 | Phase 0.4 | Frozen 50-prompt and multimodal quality reference |
| REQ-LOG-01 | Phase 0.1 | Pre-registration schema and unique run IDs |
| REQ-LOG-02 | Phase 0.5 | Auditable telemetry and failure records |
| REQ-LOG-03 | Phase 0.5 | Fresh-checkout regeneration |
| REQ-E1-01 | Phase 1.1 | 200-prompt agreement/alpha harness |
| REQ-E1-02 | Phase 1.2 | Verifier distribution and GDN/KV reset tests |
| REQ-E1-03 | Phase 1.3 | Alpha gates and explicit decision |
| REQ-E1-04 | Phase 1.3 | Numeric forks/dormant triggers |
| REQ-E2-01 | Phase 2.1 | sm_86 representative kernels |
| REQ-E2-02 | Phase 2.2 | AVX2 split and transfer accounting |
| REQ-E2-03 | Phase 2.3 | Stock offload and tiered paging traces |
| REQ-E2-04 | Phase 2.4 | Numerical/quality/end-to-end promotion |
| REQ-E3-01 | Phase 3.1 | Native activation statistics |
| REQ-E3-02 | Phase 3.2 | Controlled sparse placement/paging |
| REQ-E3-03 | Phase 3.3 | Sparse promotion or measured fallback |
| REQ-E4-01 | Phase 4.1 | Native visual prefill |
| REQ-E4-02 | Phase 4.2 | Telemetry-proven eviction and state preservation |
| REQ-E4-03 | Phase 4.3 | Pruning/recovery category comparison |
| REQ-GATE-01 | Phase 4.4 | Full-model fixed-suite quality |
| REQ-GATE-02 | Phase 4.4 | Separate speed, latency and memory acceptance |
| REQ-GATE-03 | Phase 4.5 | E0→E4 decision-gate record |

## Status / Numbers / Next Experiment

- **Status:** v1 requirements are specified as testable gates in E0→E4 order; roadmap/state artifacts now assign every v1 ID exactly once. No local run is represented as completed. v2 prototypes and out-of-scope substitutions remain explicit.
- **Numbers:** Context ≥2048; fixed text suite 50 prompts; E1 agreement 200 prompts and k=4 α≥0.6 promotion, α<0.4 healing branch; E3 activation sample ≥1,000 tokens; initial quality target ≤+15% relative PPL; interactive ambition ≥3 and project target ≥5 sustained decode tok/s. Actual VRAM/bandwidth and baseline quality/speed remain unmeasured.
- **Next Experiment:** E0: run `nvidia-smi --query-gpu=name,compute_cap,driver_version,memory.total --format=csv` and pinned bandwidth/RAM/SSD/PCIe probes, then capture a deterministic stock full-model reference at context 2048. Expected result: measured hardware report, exact command/model SHA, phase-separated timings and memory peaks in `experiments/LOG.md`, or a numerically classified loader/resource failure with two routes and cheapest next test.

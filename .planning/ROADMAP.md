# Roadmap: Qwen3.8-27B on RTX 3050

**Mode:** MVP mode — each phase is a smallest useful, observable experiment slice; no experiment is represented as complete until its evidence is logged.
**Order:** strict `E0 → E1 → E2 → E3 → E4`. A later phase cannot substitute for an unmet earlier gate.
**Baseline-first rule:** establish hardware truth, loader correctness, frozen quality reference, and stock/reference performance before invention code or custom kernels.
**Status:** Phase 1/E0 closure in progress. Hardware reroute recorded; stock baseline gate remains open. E3.1 activation profiling is resequenced to run in parallel with E2.

## Phase map

The installed GSD phase resolver accepts integer phase identifiers. The former decimal experiment slices are preserved as plan/task boundaries inside these integer phases.

| Phase | Stage | MVP deliverable | Requirement IDs (exactly once) | Advance gate / conditional fork |
|---|---|---|---|---|
| 1 | E0 | Hardware truth, environment report, model manifest, baseline, fixtures, and reproduction contract | REQ-E0-01–06, REQ-LOG-01–03 | Complete E0 evidence before E1; native failures fork to WSL2 or another labeled route without mixing measurements. |
| 2 | E1 | Ternary/base agreement harness, authoritative verifier checks, and route-fork record | REQ-E1-01–04 | k=4 α≥0.6 promotes T1; α<0.4 requires healing and remeasurement; three failures require a fork/dormant trigger. |
| 3 | E2 | sm_86 kernels, AVX2 split, transfer accounting, placement/paging, and promotion decision | REQ-E2-01–04 | Numerical correctness, quality, and repeatable end-to-end improvement must be measured; runs in parallel with E3.1 evidence only. |
| 4 | E3 | Native activation evidence, controlled sparse candidates, and sparsity decision | REQ-E3-01–03 | E3.1 activation profiling is resequenced to run in parallel with E2 because it gates T3/T4 hot-row placement; natural sparsity precedes exploitation. |
| 5 | E4 | Visual prefill, eviction, pruning/recovery, acceptance, and closure record | REQ-E4-01–03, REQ-GATE-01–03 | Full-model text/image quality, performance, and clean-checkout evidence are explicit before closure. |

## Phase details and observable success criteria

### Phase 1: Hardware truth, baseline, and reproduction (E0)

**Former experiment slices:** 0.1 hardware truth; 0.2 model artifact correctness; 0.3 stock/reference path; 0.4 frozen quality and quant ladder; 0.5 reproduction contract.

**MVP mode:** Deliver the complete E0 evidence package before any E1 work.
- Hardware and environment measurements are rerunnable with raw JSON and generated Markdown.
- Complete model artifacts and compatibility are classified.
- Stock/reference output, quality fixtures, quantization ladder, and clean-checkout regeneration are recorded.

### Phase 2: Agreement and verification (E1)

**Former experiment slices:** 1.1 agreement; 1.2 authoritative verification; 1.3 decision/forks.

### Phase 3: Kernels and memory tiers (E2)

**Former experiment slices:** 2.1 kernel probes; 2.2 CPU/GPU split; 2.3 placement/paging; 2.4 promotion.

### Phase 4: Activation sparsity (E3)

**Former experiment slices:** 3.1 activation evidence; 3.2 controlled sparsity; 3.3 decision/fallback.

### Phase 5: Multimodal closure (E4)

**Former experiment slices:** 4.1 visual prefill; 4.2 eviction; 4.3 pruning/recovery; 4.4 acceptance; 4.5 closure record.

## Detailed criteria (preserved from former slices)

### Phase 1 detail — Hardware truth (former 0.1)
**MVP mode:** one probe script, one rerun, one machine report.
- JSON/text report contains GPU SKU/VRAM/SM, driver/CUDA/toolchain, CPU/SIMD, RAM, SSD, PCIe, clocks/power and timestamp.
- Device, RAM, transfer, SSD and available-memory probes report units, repetitions, medians and thermal/power context.
- Second run reproduces identity and reports measurement variance; assumptions are labelled hypotheses.
- Every attempt has a pre-registered hypothesis, numeric target, exact command and unique run ID in the ledger.

### Phase 0.2 — Model artifact correctness (E0)
**MVP mode:** manifest and compatibility fixture before performance work.
- Source revision and checksums cover language, untied head/embedding, GDN/attention, vision, processor/tokenizer and MTP artifacts.
- Pinned config inspection confirms architecture fields and records unsupported loader components.
- A compatibility result distinguishes complete support, text-only smoke support, and blocked components.

### Phase 0.3 — Stock/reference path (E0)
**MVP mode:** one deterministic reference path, then one multimodal smoke attempt.
- Version-pinned FP16/BF16 or explicitly labelled stock NVFP4/4-bit run emits finite deterministic output at context≥2048.
- Coherent instruction-following sample and peak VRAM/RAM/load/prefill/decode measurements are recorded.
- Multimodal result explicitly says complete, text-only, or blocked; any blocker contains numeric constraint, two routes and cheapest next command.

### Phase 0.4 — Frozen quality and quant ladder (E0)
**MVP mode:** freeze fixtures first; vary only quantization thereafter.
- Hashed 50-prompt text, disjoint calibration/eval inputs, PPL/comparable score and multimodal OCR/chart/spatial/multistep cases are stored under `quality/`.
- Q4/NVFP4, Q3/IQ3 and Q2/IQ2 (or reproducibly marked unsupported) have matched tables for bytes, load, peaks, TTFT, prefill/decode, context, quality and samples.
- Reference outputs, tokenizer/processor revisions, seeds and scoring scripts are immutable.

### Phase 0.5 — Reproduction contract (E0)
**MVP mode:** regenerate E0 headline artifacts from a clean checkout.
- Applicable runs record warmups/repetitions, phase-separated speed, latency, memory, telemetry, quality, failure evidence and next test.
- Numbered scripts checksum/fetch assets and regenerate tables without hand-edited paths.
- Large models and generated binaries remain outside version control; unavailable assets/hardware are explicit.

### Phase 1.1 — Agreement (E1)
**MVP mode:** offline harness before custom kernels.
- 200 fixed held-out prompts run with greedy and k=4 settings against frozen full-model verifier.
- Tokenizer identity, per-token agreement, α, accepted-length distribution, KL/logit/PPL deltas and stratified failures are emitted as raw and summarized data.
- Draft quality is labelled draft quality, never full-model quality.

### Phase 1.2 — Authoritative verification (E1)
**MVP mode:** correctness before speed.
- Rejection algorithm's final distribution or seeded deterministic outputs match the verifier.
- GDN recurrent state/KV reset, tokenizer and RNG behavior pass independent tests.
- Verification records preserve draft tokens, logits, accepted prefix/length, α and fallback reason.

### Phase 1.3 — Decision/forks (E1)
**MVP mode:** one explicit route decision, no silent abandonment.
- α≥0.6 at k=4 is promotion evidence; α<0.4 runs layer-wise healing/distillation and remeasurement; intermediate α receives a documented comparison.
- End-to-end speed/latency is measured separately from α.
- Each failed gate states numeric constraint, two engineering routes and cheapest command; third same-route failure creates fork or dormant trigger.

### Phase 2.1 — Kernel probes (E2)
**MVP mode:** microbenchmarks before model integration.
- Exact 17408×5120/5120×17408 FFN and representative GDN/attention/head shapes run at M=1,4,8,16 on verified sm_86.
- FP16, stock 4-bit and available ternary/1.25/2–2.5-bit candidates report packing, warm time, error, effective bandwidth and occupancy where available.
- Unsupported formats/architectures are reproducibly marked.

### Phase 2.2 — CPU/GPU split (E2)
**MVP mode:** scalar correctness, then AVX2, then transfer overlap.
- AVX2 FFN GEMV matches scalar output and reports throughput against measured STREAM.
- Pinned/pageable hidden-state transfer latency and bandwidth, synchronization and overlap are measured.
- Any 70% STREAM result is labelled measured target evidence, not assumed.

### Phase 2.3 — Placement and paging (E2)
**MVP mode:** stock offload is the control; one placement variable per run.
- Tensor locations, copy/page-fault traces, state/KV residency, cold/warm behavior and context≥2048 decode are recorded.
- Hot VRAM, warm RAM and cold SSD pipeline is promoted only when matched end-to-end latency/memory improves within quality tolerance.
- Silent eviction is ruled out by telemetry.

### Phase 2.4 — Kernel promotion (E2)
**MVP mode:** promote only an end-to-end winner.
- Candidate passes declared numerical tolerance against FP16/reference.
- Fixed-suite quality is preserved.
- Repeat runs demonstrate end-to-end improvement; otherwise route is forked/dormant with numeric revisit trigger.

### Phase 3.1 — Activation evidence (E3)
**MVP mode:** measure native SiLU/SwiGLU before changing it.
- At least 1,000 representative tokens are profiled.
- Per-layer/neuron and prompt-category magnitude distributions, top-k mass and inactive fraction are stored.
- dReLU or borrowed sparsity percentages are not treated as evidence.

### Phase 3.2 — Controlled sparsity (E3)
**MVP mode:** static control before adaptive paging.
- Static hot/cold, activation-aware paging and structured 3:4 ternary sparsity are compared against dense reference.
- Bytes/token, page hits/faults, RAM/SSD traffic, decode speed and adversarial fixed-suite quality are reported.
- Any dReLU conversion includes healed/evaluated outputs before promotion.

### Phase 3.3 — Sparsity decision (E3)
**MVP mode:** retain evidence even when route loses.
- Sparse promotion requires measured byte/time reduction and declared text-quality delta.
- If rejected, statistics remain archived and a mixed-precision or memory-tier fork has a numeric revisit trigger.

### Phase 4.1 — Visual prefill (E4)
**MVP mode:** unpruned correctness before pruning.
- Native processor and complete vision tower run at declared precision.
- Preprocessing, visual-token count, visual latency, peak VRAM and OCR/chart/spatial/multistep quality are recorded.
- Unpruned image-text outputs are preserved as the reference for E4 comparisons.

### Phase 4.2 — Eviction (E4)
**MVP mode:** prove memory recovery, not merely call `free()`.
- Synchronization and allocator/device-free-memory telemetry show recovered usable VRAM.
- Visual embeddings and required GDN/KV state remain available for decode.
- Post-eviction outputs match the unpruned reference within the declared quality tolerance.

### Phase 4.3 — Pruning/recovery (E4)
**MVP mode:** compare no-prune, dynamic prune and explicit recovery.
- Retained tokens and per-category accuracy are reported.
- Task-critical losses reject pruning or trigger adaptive recovery/no-prune fallback.
- Speed/memory changes are separated from quality changes.

### Phase 4.4 — Acceptance (E4)
**MVP mode:** one fixed acceptance run, with no student substitution.
- Full 27B remains authoritative at context≥2048 with 50-prompt text and multimodal scores against pinned reference; target is ≤+15% relative PPL or predeclared equivalent delta.
- Warm sustained decode, prefill, TTFT, load time, VRAM/RAM and SSD/PCIe traffic are separately reported; ambition ≥3 tok/s and project target ≥5 tok/s are not relabelled if missed.
- Fresh-checkout scripts regenerate the acceptance evidence.

### Phase 4.5 — Closure record (E4)
**MVP mode:** publish decisions, not claims of unrun work.
- E0→E4 table lists prerequisite, artifact hashes, evidence, pass/fork/dormant status, constraint, two routes, trigger and next command.
- Unresolved gates are explicit and no experiment is described as complete without evidence.
- All failures remain in the append-only ledger.

## Conditional fork policy

- E0 loader/resource failure: newer pinned Transformers/model code, WSL2, or a small architecture fixture; do not call a generic loader valid.
- E1 α<0.4: layer-wise healing/distillation and repeat; intermediate α: compare mixed precision or verifier-residual route; three route failures: fork/dormant trigger.
- E2 unsupported kernel/build: preserve numerical harness, use FP16/INT4, WSL2, CPU AVX2 or a measured fork; no desktop result substitution.
- E2 paging regression: change page granularity/prefetch policy only as a new variable; retain stock offload control.
- E3 sparse quality loss/no reduction: retain statistics and fork to mixed precision/memory tiers; dReLU requires healing.
- E4 eviction failure: hard synchronization/allocator barrier or CPU-offloaded vision; pruning quality loss: recovery/no-prune fallback.
- Any blocker must state exact numeric constraint, at least two routes and cheapest next experiment. Three failures on one route require a fork or dormant note with measurable revisit trigger.

## Milestone sequencing

1. Complete all 0.x phases and pass the E0 gate.
2. Complete 1.x and record the E1 decision before any E2 work.
3. Complete 2.x and promote/fork a measured kernel/memory route before E3.
4. Complete 3.x and decide whether sparsity is promoted before E4.
5. Complete 4.x closure, then update project validation and unresolved work; never claim experiments complete from planning artifacts alone.

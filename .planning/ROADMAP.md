# Roadmap: Qwen3.8-27B on RTX 3050

**Mode:** MVP mode — each phase is a smallest useful, observable experiment slice; no experiment is represented as complete until its evidence is logged.
**Order:** strict `E0 → E1 → E2 → E3 → E4`. A later phase cannot substitute for an unmet earlier gate.
**Baseline-first rule:** establish hardware truth, loader correctness, frozen quality reference, and stock/reference performance before invention code or custom kernels.
**Status:** Planned only. No experiments are complete.

## Phase map

| Phase | Stage | MVP deliverable | Requirement IDs (exactly once) | Advance gate / conditional fork |
|---|---|---|---|---|
| 0.1 | E0 | Reproducible hardware and environment report | REQ-E0-01, REQ-E0-02, REQ-LOG-01 | Identity and bandwidth rerun; if native tooling fails, fork to WSL2 while preserving the same probe schema. |
| 0.2 | E0 | Immutable complete-model manifest and compatibility report | REQ-E0-03 | Config, tokenizer, GDN/attention, vision, MTP and untied head are classified; unsupported components trigger loader/fixture fallback, not silent omission. |
| 0.3 | E0 | Deterministic stock/reference text and multimodal smoke path | REQ-E0-04 | A coherent context≥2048 sample and explicit text-only vs complete multimodal status are recorded; loader/resource failures get two routes and a cheapest test. |
| 0.4 | E0 | Frozen quality fixtures and stock quantization ladder | REQ-E0-05, REQ-E0-06 | Baseline table and hashed 50-prompt/multimodal reference exist before E1; unsupported quant levels are evidence-backed. |
| 0.5 | E0 | Fresh-checkout run regeneration contract | REQ-LOG-02, REQ-LOG-03 | Machine-readable logs and numbered scripts reproduce the headline E0 table without hand-edited paths. |
| 1.1 | E1 | Matched ternary/base offline agreement harness | REQ-E1-01 | 200 held-out prompts, greedy/k=4, alpha and stratified errors are reported against the frozen verifier. |
| 1.2 | E1 | Authoritative verifier and recurrent-state correctness | REQ-E1-02 | Rejection/verifier outputs match seeded full-model behavior; tokenizer, RNG, GDN/KV reset tests pass. |
| 1.3 | E1 | Agreement decision and route-fork record | REQ-E1-03, REQ-E1-04 | k=4 α≥0.6 promotes T1; α<0.4 forces layer-wise healing/remeasurement; intermediate α gets comparison; three failures fork or record dormant trigger. |
| 2.1 | E2 | sm_86 representative kernel correctness/performance probes | REQ-E2-01 | Exact FFN/GDN/attention/head shapes at M=1,4,8,16 have numerical error, timing and bandwidth evidence; unsupported formats remain marked. |
| 2.2 | E2 | AVX2 CPU split and transfer accounting | REQ-E2-02 | Scalar-correct CPU baseline, STREAM comparison, hidden-state-only pinned transfer and overlap are measured; 70% STREAM remains a target, not an assumption. |
| 2.3 | E2 | Placement, paging and stock-offload comparison | REQ-E2-03 | Stock partial offload precedes custom hot/warm/cold paging; page traces, state residency and cold/warm decode are recorded. |
| 2.4 | E2 | Kernel/route promotion decision | REQ-E2-04 | Numerical tolerance, quality and repeatable end-to-end improvement are all demonstrated or route is forked/dormant with trigger. |
| 3.1 | E3 | Native activation sparsity measurement | REQ-E3-01 | ≥1,000 representative tokens yield layer/neuron/category distributions, top-k mass and inactive fraction before exploitation. |
| 3.2 | E3 | Controlled sparse placement/paging candidates | REQ-E3-02 | Static hot/cold, activation-aware paging and structured sparsity are compared on fixed quality suite with bytes/page/traffic/adversarial evidence. |
| 3.3 | E3 | Sparsity decision and fallback | REQ-E3-03 | Promote only measured byte/time reduction within quality delta; otherwise retain statistics and fork to mixed precision or memory-tier tuning. |
| 4.1 | E4 | Native visual prefill and unpruned reference | REQ-E4-01 | Native processor/tower run records visual tokens, latency, VRAM and category quality before pruning. |
| 4.2 | E4 | Verified vision eviction and state preservation | REQ-E4-02 | Synchronization, allocator and free-memory telemetry demonstrate recovered usable VRAM while embeddings and GDN/KV state survive. |
| 4.3 | E4 | Pruning/recovery comparison and multimodal decision | REQ-E4-03 | No-prune, dynamic pruning and recovery fallback are compared per category; task-critical losses reject or fork pruning. |
| 4.4 | E4 | Full-model quality and interactive performance acceptance | REQ-GATE-01, REQ-GATE-02 | Complete model remains authoritative at context≥2048; fixed text/image quality and separate TTFT/prefill/decode/memory metrics meet declared targets or are numerically reported as unresolved. |
| 4.5 | E4 | E0→E4 decision table and clean-checkout closure | REQ-GATE-03 | Every gate has artifact hashes, evidence, pass/fork/dormant decision, constraint, two routes, revisit trigger and next command; no completion claim hides unresolved gates. |

## Phase details and observable success criteria

### Phase 0.1 — Hardware truth (E0)
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

# FEATURES — Qwen3.8-27B on RTX 3050

## Purpose and product boundary

The v1 product is a measured, reproducible inference path for the **complete Qwen/Qwen3.8-27B multimodal checkpoint** on the actual laptop RTX 3050. A draft model, pruned model, or small distilled model may accelerate work, but it is never the authoritative answer: final tokens, quality comparisons, and acceptance decisions must be attributable to the full 27B model (or an explicitly identified full-model quantized representation).

The feature set is organized around the experiment queue E0–E4. Every feature produces an artifact and a gate, not merely a demo. A blocker is recorded as a numeric constraint, with at least two engineering routes and a cheapest next experiment.

## V1 requirements (must ship)

### 1. Hardware truth and environment capture (E0)

Capture, in a versioned machine report:

- Exact RTX 3050 laptop SKU, VRAM capacity, SM architecture (expected sm_86, verify), clocks, power mode, driver, CUDA/toolkit, and runtime/library versions.
- Measured VRAM bandwidth, host RAM size/type/bandwidth, CPU model and SIMD features (AVX2/AVX-512), SSD type and sequential/random throughput, PCIe link generation/width, and thermal/power state.
- A repeatable command that emits JSON/text plus timestamp and git/model hashes. Assumed 168–224 GB/s GPU bandwidth and 4–8 GB VRAM are hypotheses until measured.

**Gate:** another operator can rerun the probe and obtain the same hardware identity and comparable measurements; all performance claims cite this report.

### 2. Full-model reference and stock baselines (E0/E1)

Provide a known-good reference path before invention work:

- Download/checksum the complete Qwen3.8-27B checkpoint, including language model, untied input/output embeddings, vision tower, processor/tokenizer, and native MTP metadata. Record source revision and license.
- Establish the strongest available local baseline (FP16/BF16 if it can run, otherwise stock NVFP4/4-bit reference) with exact launch command, context >=2048, prompt template, image input path, and deterministic seed/settings.
- Produce a baseline table for at least one reference representation and progressively lower quantization (4-bit, 3-bit/2-bit where supported): model bytes, load time, VRAM/RAM peaks, prefill tok/s, decode tok/s, first-token latency, and output samples.
- Build a fixed 50-prompt text suite and a small multimodal suite. Store prompts, expected/reference outputs, tokenization metadata, and raw run outputs under `quality/`.

**Gate:** coherent instruction-following at context >=2048; baseline quality and speed are recorded, not inferred. The quality target is a documented delta against the first reference (initial project target is <=15% PPL or an agreed fixed-suite score delta).

### 3. Experiment ledger and reproducibility contract (all experiments)

Every E0–E4 run must log to `experiments/LOG.md` (failures included):

- Hypothesis and numeric target written before execution.
- Experiment ID, one changed variable, exact command, script and commit/hash, model file/checksum, quantization/packing, context, prompt/eval revision, and random seed.
- VRAM peak, RAM peak, temperature/power if available, prefill/decode tok/s, latency, acceptance rate where relevant, and quality sample/score.
- Failure mode, evidence, route status, and next experiment. Three failures trigger a fork and a written dormant note; never silently discard a route.

Reproduction must work from a fresh clone with scripts that fetch or validate models, configure runtime, run probes, and regenerate tables. Large models and generated binaries remain outside version control under `/models` and `/runtimes`.

**Gate:** a clean-machine checklist can reproduce the headline number and identify any unavailable hardware/model asset.

### 4. Ternary agreement and authoritative verification (E1)

Implement an offline agreement harness before custom kernels:

- Compare a ternary/base representation against the full-model NVFP4/4-bit reference on 200 fixed prompts, greedy and k=4 draft settings.
- Report per-token agreement, acceptance rate alpha, accepted-length distribution, logit/KL or PPL deltas, and failures by prompt category.
- Promotion criterion: alpha >= 0.6 for k=4 (project decision); if alpha <0.4, run layer-wise distillation/healing and repeat before judging the route. The verifier remains the full 27B model; speculative output is accepted only under an explicit verification algorithm.
- Include a quality-preserving fallback: mixed precision or ternary draft + higher-precision residual/verifier (T1), not a small-model replacement.

**Gate:** agreement report is statistically reproducible and demonstrates whether T1 is promoted, healed, or forked.

### 5. Kernel and memory-tier performance proof (E2)

Benchmark representative real tensor shapes before integrating end-to-end:

- FFN GEMV: 17,408 x 5,120 (and batched M=1,4,8,16), GDN projections, full-attention projections, and untied lm_head. Cover ternary W1.58A8, 1.25-bit 3:4, QTIP/AQLM-like 2–2.5-bit, and stock 4-bit reference where available.
- Measure effective bandwidth, kernel time, occupancy/utilization, correctness against FP16, and decode throughput on sm_86. Test BitNet/bitnet-tc, BitBLAS, and an AVX2 CPU path where applicable; do not assume published hardware numbers transfer.
- Exercise CPU/GPU split and pipelined copies with hidden-state-only transfers. Record PCIe transfer time, synchronization count, and overlap efficiency.
- Keep context and KV settings fixed while comparing kernels; one variable changes per experiment.

**Gate:** kernel numerical error is within the declared tolerance; the winning path reaches a measurable fraction of STREAM/device bandwidth and improves the end-to-end baseline without violating quality gates.

### 6. Sparsity measurement and controlled exploitation (E3)

First measure, then exploit:

- Collect SwiGLU activation magnitudes over >=1K representative tokens and report top-k mass, inactive fraction, layer/neuron distributions, and prompt sensitivity. Qwen3.8's native SiLU behavior is authoritative; dReLU conversion is an experiment, not an assumption.
- Test static hot/cold placement, activation-aware neuron paging, structured 3:4 ternary sparsity, and (only if healed/evaluated) dReLU sparsification. Report bytes read/token, page faults, RAM/SSD traffic, and quality impact.
- Compare dense full-model output with sparse output on the fixed text suite and identify adversarial prompts where static pruning fails.

**Gate:** a sparsity route is promoted only if it reduces measured bytes/time and remains within the declared quality delta; otherwise retain measurement artifacts and fork to precision/memory-tier optimization.

### 7. VLM prefill and vision-tower eviction (E4)

Preserve complete image-text behavior while preventing vision memory overlap with decode:

- Run the native vision processor/tower in BF16 or the selected reference precision during prefill; measure image preprocessing, vision peak VRAM, visual-token count, prefill latency, and multimodal quality.
- Evict/release vision weights and temporary activations before language decode; verify via allocator telemetry and post-eviction VRAM. Ensure visual embeddings and required recurrent/KV state survive exactly.
- Compare no-pruning, dynamic visual-token pruning, and recovery/fallback behavior on a fixed multimodal suite (OCR, charts, spatial relations, multi-step visual reasoning). Report MMMU-like subset score or task accuracy and visual-token retention.
- Test temporal separation: vision and language weights need not coexist in VRAM. Do not claim eviction if the allocator merely caches the memory.

**Gate:** image-text output remains coherent and instruction-following, eviction is observable, and decode speed/memory improve or remain within a documented budget.

### 8. Quality, speed, and completion gates

A route is v1-complete only when all are true:

- Full-model behavior: text and multimodal inference work at N>=2048 context; no silent substitution of a student model.
- Quality: fixed 50-prompt text evaluation and multimodal subset are compared with the reference; PPL/score delta is documented, with initial target <=15% PPL or an agreed equivalent.
- Performance: actual decode speed is measured; project core target is >=5 tok/s, with the initial ambition >=3 tok/s before optimization. TTFT, prefill, and sustained decode are separate numbers.
- Memory: peak VRAM/RAM and any SSD/PCIe traffic are reported; the path works on the measured 3050 SKU rather than an assumed SKU.
- Reproducibility: scripts from a fresh checkout regenerate the benchmark and logs, with model/runtime hashes and environment capture.

## Deferred differentiators (after v1 gates)

These are valuable only after E0 baselines and the full-model quality contract are stable:

- Scalable-codec self-speculation with ternary VRAM base plus RAM enhancement residual and rejection sampling (T1), including native Qwen MTP composition.
- Full 27B ternary QAT/BitDistill-style healing, Sherry 1.25-bit FFN, QTIP mixed precision, and large-scale teacher distillation; v1 can validate layer-local probes and agreement first.
- Learned hot-page predictors, virtual-texturing neuron cache, dynamic sparsity recovery, and dReLU conversion; natural sparsity measurement is v1, training the new activation is deferred.
- Matryoshka/base-plus-enhancement representations, AQLM/QTIP decoder specialization, custom fused sm_86 kernels, and AVX2 FairyFuse-style CPU kernels beyond the minimum benchmark.
- Speculative tree drafting, EAGLE/QSpec integration, continuous batching, server packaging, and power/thermal autotuning.
- Long-context optimization beyond the v1 >=2048 gate (OSCAR 2-bit KV, sliding-window behavior where architecture permits). Hybrid GDN state and low KV footprint make this promising but not a prerequisite.
- Aggressive visual-token pruning and heterogeneous BF16-ViT/sub-2-bit language precision after unpruned multimodal correctness is established.
- Cloud/borrowed compute for explicitly logged healing or training experiments only; it is not the deployment answer.

## Feature-to-artifact matrix

| Area | Required artifact | Promotion evidence |
|---|---|---|
| E0 hardware | `hardware_report` + environment lock | measured SKU/bandwidth/VRAM/RAM/PCIe/SSD |
| E0 baseline | launch scripts, checksums, quality fixtures, baseline table | full-model coherent text + image runs |
| E1 agreement | agreement JSON/CSV, plots, raw outputs | alpha and quality gate decision |
| E2 kernels | correctness tests, microbenchmark table, profiler captures | error tolerance + bandwidth/time result |
| E3 sparsity | activation statistics, cache traces, sparse outputs | bytes/time reduction at quality delta |
| E4 VLM | eviction telemetry, multimodal outputs, token-count table | observable eviction + multimodal gate |
| Reproducibility | scripts, lockfiles, hashes, run manifest | clean checkout rerun |

## Status / Numbers / Next Experiment

- **Status:** FEATURES v1 is defined around E0–E4, with the complete Qwen3.8-27B as the authority. Ternary, custom kernels, sparsity, speculation, and aggressive VLM pruning are differentiated from the minimum evidence needed to establish a trustworthy path.
- **Numbers:** Architecture inputs are 64 layers (48 GDN + 16 full attention), ~25.6B streamed parameters/token, ~17.1B FFN parameters, and a ~0.4B vision tower. Gates: context >=2048; 50-prompt text suite; 200-prompt E1 agreement; k=4 alpha >=0.6 promotion (alpha <0.4 triggers healing); initial quality target <=15% PPL delta; project performance target >=5 decode tok/s.
- **Next Experiment:** Run E0 hardware truth first. Record exact VRAM/SKU, measured GPU/RAM/SSD/PCIe bandwidth, driver/CUDA/runtime hashes, and a repeatable report. Then establish the stock full-model/4-bit reference before changing quantization or kernels; log the command and peaks to `experiments/LOG.md`.

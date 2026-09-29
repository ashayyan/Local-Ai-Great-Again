# Research Summary — Qwen3.8-27B on an RTX 3050 Laptop

## Executive Summary

The project is to run the **complete Qwen/Qwen3.8-27B multimodal checkpoint** on the actual RTX 3050 laptop. A draft, pruned student, or distilled model may accelerate experiments, but the full model (or an explicitly identified full-model quantized representation) remains authoritative for tokens, quality, and promotion decisions.

The target architecture is hybrid: 64 layers, including 48 Gated DeltaNet (GDN) layers and 16 full-attention layers, with hidden size 5120, FFN width 17,408, 24 query heads/4 KV heads, an untied ~1.27B lm_head, a 27-layer vision tower, and one MTP layer. The dominant decode burden is streamed weight traffic, especially the approximately 17.1B FFN parameters and lm_head; GDN/recurrent state and KV are expected to be smaller than in a dense-attention model, but exact allocations require measurement.

The roadmap is deliberately ordered E0→E4. E0 establishes hardware truth, loader correctness, and a labeled reference. E1 establishes compatible stock quantized baselines and the ternary-agreement decision. E2 measures kernels, placement, and hot/warm/cold memory execution. E3 measures native sparsity and integrates controlled low-bit, split, and speculative routes. E4 closes multimodal staging, vision eviction, quality, speed, and fresh-checkout reproduction. No estimate from another GPU, model, batch size, or runtime is a laptop result.

## Key Findings

### Architecture and footprint

- **Architecture facts (reported/derived; verify against the pinned model revision):** 64 layers; 48 GDN + 16 full attention; hidden 5120; FFN 17,408; 24 Q heads/4 KV heads; untied embeddings/output; 27-layer vision tower; one MTP layer.
- **Derived traffic estimate:** approximately 25.6B parameters are streamed per decode token, with about 17.1B in FFNs. This is a lower-bound model, not a device trace: scales, metadata, dequantization, rereads, synchronization, lm_head strategy, and recurrent-state traffic are excluded.
- **Derived payload arithmetic:** ideal 1.58-bit storage for 27B weights is about 5.33 GB; common 2-bit packing is about 6.75 GB before scales, metadata, workspace, state, and headroom. A mixed 1.25/2.5-bit payload near 5.3 GB is a design estimate, not proof of fit on a 6 GB card.
- **Measured status:** no laptop-specific VRAM, bandwidth, PCIe, SSD, RAM, thermal, throughput, or quality number exists until E0. The RTX 3050 SKU must be queried; 4/6/8 GB, 35–80 W, bus width, clocks, and PCIe topology vary.

### Evidence and candidate routes

- Stock Q4/NVFP4 and lower-bit formats are the fastest baseline, but a runtime must prove Qwen3.8 GDN state, MTP, and multimodal preservation. A generic Qwen3 loader or text-only process exit is not sufficient.
- **T1 (leading hypothesis):** a ternary base in VRAM plus enhancement residual in RAM, with full-model verification and exact rejection sampling. The E1 decision gate is `k=4 alpha >= 0.6` to promote; `alpha < 0.4` requires layer-wise healing before judgment. Alpha and projected ~7 tok/s are hypotheses until measured.
- **T2:** whole-model mixed precision (roughly 1.25-bit FFN and 2–2.5-bit sensitive/non-FFN tensors), requiring block or layer healing. There is no target-scale quality evidence yet.
- **T3:** CPU/AVX2 FFN with GPU-resident GDN, attention, and head; transfer hidden state only where possible. Published AVX-512 or desktop numbers do not establish laptop AVX2 performance. The >=70% measured STREAM target is a hypothesis.
- **T4:** activation-aware hot/cold neuron paging and possible dReLU healing. Native SiLU sparsity must be measured; an inactive-fraction claim from another model is not evidence.
- **T5:** temporal vision staging: run the vision tower during prefill, serialize projected visual state, evict vision allocations, then decode. Visual-token pruning is optional and must be category-tested, especially OCR, charts, small objects, spatial relations, and multi-step reasoning.

### Measurement and reproducibility discipline

Every E0–E4 run appends to `experiments/LOG.md`, including failures. The record must include hypothesis and numeric target written before execution, exact command, model/runtime/artifact hashes, quant/context/placement, prompt and seed, warmups, VRAM/RAM peaks, prefill/decode tok/s, latency, quality output, failure mode, and next route. One variable changes per experiment. Three failures on one route trigger a fork and a written dormant trigger.

Native Windows is first; WSL2 is the documented fallback for Linux-first tools. Pin model revision, runtime commit, Python/PyTorch/CUDA/compiler versions, and CUDA architecture (`sm_86` once verified). Separate batch-1 decode GEMV from prefill GEMM, and separate GPU DRAM, CPU/RAM, PCIe, and SSD measurements. Warmup, clocks, power, thermal state, and cold/warm paging must be recorded.

## Roadmap Implications and Exact Gates

### E0 — Hardware truth, loader smoke test, and reference

Query the exact GPU/SKU and capture driver, CUDA/toolchain, CPU SIMD, RAM, SSD, PCIe, clocks, power, and measured bandwidth. Pin the Qwen3.8 revision and verify config fields, tokenizer, GDN/full-attention implementation, MTP metadata, and vision processor. Establish deterministic text logits/output and a multimodal smoke test where supported. Use FP16/BF16 where possible; otherwise label NVFP4/4-bit or CPU/offload execution explicitly as the teacher/reference.

**Gate:** reproducible hardware report and correct model class/output, including a coherent sample at context `N >= 2048`. A loader or memory failure is classified precisely and recorded with two candidate routes plus the cheapest next experiment. Do not start E1 until architecture correctness and hardware truth are recorded.

### E1 — Stock quantized baseline and ternary agreement

Run compatible upstream llama.cpp/runtime first, then pinned forks only when needed. Measure Q4, Q3, IQ3, IQ2, or available QTIP-like variants with fixed prompt, context, sampler, seed, and one changed variable. Confirm GDN state, MTP, and vision behavior. Build the 200-prompt agreement harness against the full-model NVFP4/4-bit reference before custom kernels; report per-token agreement, `k=4` alpha, accepted-length distribution, PPL/logit/KL deltas, and stratified failures.

**Gate:** baseline speed/quality/memory table plus a reproducible agreement report. `alpha >= 0.6` at `k=4` promotes T1; `alpha < 0.4` triggers layer-wise distillation/healing and repetition. Intermediate results fork to mixed precision or verifier-residual routes, never to silent student-model substitution.

### E2 — Kernel, placement, and memory-tier performance

Benchmark exact shapes: FFN GEMV `17,408 x 5,120` at `M={1,4,8,16}`, GDN and attention projections, untied lm_head, and stock 4-bit reference. Compare FP16/INT8/INT4 and available INT2/ternary kernels in BitBLAS/BitNet or a controlled harness. Compile explicitly for `sm_86`, warm up, check numerical error, and measure effective bandwidth, kernel time, occupancy where available, and CPU AVX2 versus measured STREAM. Measure pinned 10 KB H2D/D2H and hidden-state-only transfer separately.

Then implement VRAM-hot/RAM-warm/SSD-cold placement and asynchronous prefetch only from baseline evidence. Record page misses, PCIe copies, synchronization, overlap, and cold/warm SSD behavior; do not treat PCIe weight streaming as GPU-DRAM bandwidth.

**Gate:** declared numerical tolerance and a complete, non-OOM decode path at context `N >= 2048`, with measured prefill/decode and memory telemetry. Unsupported GDN/vision/MTP or `sm_86` kernels preserve the numerical harness and select the documented fallback/fork.

### E3 — Controlled sparsity, mixed precision, and speculative integration

Measure native SwiGLU activation magnitudes over at least 1K representative tokens before dReLU or paging. Report top-k mass, inactive fraction, layer/neuron distribution, prompt sensitivity, bytes read/token, page faults, and quality impact. Test static hot/cold placement before learned predictors. Integrate T1/T2/T3 in order—one FFN block, one layer, then full model—and validate single-path logits and recurrent-state reset before MTP or a small drafter.

**Gate:** a promoted sparsity/low-bit route must reduce measured bytes or time while remaining within the declared quality delta. Exact speculative verification must preserve the verifier distribution; report draft cost, verifier batch latency, accepted tokens/cycle, wall tok/s, and p50/p95 latency. The AVX2 target is `>= 70%` of measured STREAM, explicitly a target rather than a result. Acceptance is not speedup.

### E4 — Multimodal and quality closure

Run vision prefill in the selected precision, measure visual-token count and phase peak, synchronize, release vision tensors, and verify allocator-visible recovery before language decode. Compare no pruning, dynamic pruning, and recovery/no-prune fallback across fixed OCR, chart, spatial, small-object, and multi-step suites. Preserve visual embeddings and required GDN/KV state exactly.

**Gate:** full text and image behavior at `N >= 2048`; fixed-suite quality delta documented; sustained decode and TTFT measured separately; VRAM/RAM/PCIe/SSD telemetry captured; and fresh-checkout scripts reproduce the run. A faster route that changes or silently drops multimodal behavior is not promoted.

## Quality, Performance, and Completion Contract

The initial quality target is `<= +15%` PPL delta (or an explicitly agreed fixed-suite equivalent) against the first trusted reference. The initial performance ambition is `>= 3` decode tok/s; the project core target is `>= 5` decode tok/s. These are gates/targets, not current measurements. The fixed evaluation must include a 50-prompt text suite and a multimodal subset; the E1 agreement test uses 200 prompts. TTFT, prefill, sustained decode, accepted length, and p50/p95 inter-token latency remain separate metrics.

## Confidence and Gaps

**High confidence:** E0–E4 order, full-model authority, experiment ledger, one-variable rule, three-failure fork rule, and quality gates are binding project requirements. The broad hybrid architecture and streamed-weight concern are grounded in the model/config research, pending immutable-revision verification.

**Medium confidence:** GDN may tolerate more aggressive quantization; ternary kernels, tiered paging, speculative verification, and temporal vision separation are credible mechanisms. Their combination and Windows/sm_86 behavior are unvalidated.

**Low confidence / explicit gaps:** all laptop performance, memory, thermal, bandwidth, PCIe, SSD, fit, and quality figures; ideal 5.33 GB/derived 5.3 GB footprints; projected 24 tok/s ceiling; T1 ~7 tok/s; T3 6–8 tok/s; >=85% inactivity; speculative break-even; and actual vision allocator reclamation. No target-scale published ternary conversion establishes quality for this pretrained 27B model. Windows support across runtimes and Chinese-language/patent evidence remain incomplete.

## Sources

- [`STACK.md`](STACK.md) — pinned runtime/toolchain strategy, E0–E4 ladder, instrumentation, and run schema.
- [`FEATURES.md`](FEATURES.md) — product boundary, artifact gates, quality suites, and feature-to-artifact matrix.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — artifact/tier/runtime contracts, scheduler, verifier, and multimodal staging.
- [`PITFALLS.md`](PITFALLS.md) — bandwidth, footprint, quality, kernel, AVX2, PCIe, Windows, VLM, and claims-audit risks.
- Qwen3.8 [config.json](https://huggingface.co/Qwen/Qwen3.8-27B/blob/main/config.json) and [model repository](https://huggingface.co/Qwen/Qwen3.8-27B/tree/main).

## Status / Numbers / Next Experiment

**Status:** Research synthesis complete. E0→E4 is the binding roadmap; T1 is the leading quality-preserving hypothesis and T2–T5 are measured alternatives. No laptop-specific number is promoted to a result before E0.

**Numbers:** 64 layers (48 GDN, 16 full attention); hidden 5120; FFN 17,408; ~25.6B streamed parameters/token; ~17.1B FFN parameters; ideal 1.58-bit payload ~5.33 GB; common 2-bit payload ~6.75 GB before overhead; mixed 1.25/2.5-bit estimate ~5.3 GB; `alpha >= 0.6` at `k=4`; quality `<= +15%` PPL delta; performance ambition `>=3` tok/s and core target `>=5` tok/s. All except the gates/targets and architecture facts are derived, reported, or hypothesized—not laptop measurements.

**Next Experiment:** E0 only. Run `nvidia-smi --query-gpu=name,compute_cap,driver_version,memory.total --format=csv`, capture CPU/RAM/SSD/PCIe/toolchain data, verify Qwen3.8 GDN/MTP/vision fields, and produce deterministic text plus multimodal/reference outputs at context 2048 where supported. Append exact command, model revision/hash, measured peaks, timings, quality sample, and any failure with two candidate routes to `experiments/LOG.md`. Do not begin E1 until E0 architecture correctness and hardware truth are recorded.

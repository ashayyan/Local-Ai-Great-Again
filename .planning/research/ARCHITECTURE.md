# Architecture Research — Qwen3.8-27B on RTX 3050

## Scope and design principles

The target is the complete Qwen3.8-27B multimodal behavior on a 4–8 GB RTX 3050 laptop, not a smaller substitute. The architecture treats memory bandwidth and movement as first-class constraints. From the research brief: 64 layers, 48 Gated DeltaNet (GDN) layers, 16 full-attention layers, 24 Q heads/4 KV heads, 5120 hidden size, 17,408 FFN width, untied 1.27B-parameter `lm_head`, a 27-layer vision tower, and one native MTP layer. Approximately 25.6B parameters are streamed per decode token; hybrid attention keeps KV/state relatively small.

The system is organized as reproducible data planes rather than a single launcher:

```text
models/ (immutable artifacts)
   -> manifests + converters
runtimes/ (pinned engines and forks)
   -> scripts/ (thin reproducible commands)
benchmarks/quality/ (fixed inputs and scorers)
   -> experiments/ (append-only measurements)
reports/ (derived tables and decisions)
```

Every experiment has a hypothesis, one changed variable, exact artifact hashes, hardware telemetry, throughput, and quality output. Failed runs are valid records and trigger a route fork after three failures.

## Components and contracts

### 1. Artifact registry and model storage (`models/`)

Store source checkpoints, quantized variants, tokenizer/config, vision weights, and residual/enhancement layers as immutable content-addressed artifacts. Never overwrite a model file. Each artifact has a sidecar manifest:

```yaml
artifact_id: qwen3.8-27b-nvfp4-<sha256>
source_revision: <HF commit>
format: safetensors|gguf|custom
quant: bf16|nvfp4|qtip2|sherry1.25|ternary
parameter_scope: full|ffn|gdn|attention|lm_head|vision
shape_schema: qwen3.8-27b-v1
bytes: <integer>
calibration_set: <quality id or null>
parent_artifact: <artifact id or null>
```

A composite model is a manifest, not a concatenated opaque file: `base_weights`, `enhancement_weights`, `kv_format`, `vision_format`, and `tokenizer_revision` must be explicit. NVMe is the cold source; mmap/page cache is the warm tier; VRAM is the hot tier.

### 2. Runtime adapters (`runtimes/`)

Pin llama.cpp/ik_llama.cpp, BitNet/BitBLAS, pipelined sharding, AirLLM/FlexGen experiments, and local forks by commit. An adapter exposes one normalized invocation contract:

```json
{"model_manifest":"...","prompt":"...","images":[],"context":2048,
 "memory_policy":{"vram":"...","ram":"...","ssd":"..."},
 "decode":{"temperature":0,"seed":0,"draft":null},
 "output":{"tokens":[],"timings":{},"telemetry":{}}}
```

The adapter must preserve exact logits/token IDs for deterministic verification, or state why a kernel is nondeterministic. It must distinguish prefill, decode, draft, verify, and image phases.

### 3. Scripts and orchestration (`scripts/`)

Use small composable scripts: `download_model`, `convert_quant`, `inspect_config`, `launch_runtime`, `profile_memory`, `benchmark_decode`, `benchmark_prefill`, `run_quality`, `run_speculative`, `run_multimodal`, and `summarize_experiments`. A script accepts a manifest and emits JSONL records; shell wrappers are convenience only. Fresh-clone reproduction must require no hand-edited paths.

### 4. Experiment ledger (`experiments/LOG.md` plus one file/run)

Append one record per run, including failures:

```yaml
run_id: E1-2026...
parent_run: E0-...
hypothesis: "... numeric target ..."
changed_variable: "one variable only"
command: "exact command"
artifact_ids: ["..."]
context: 2048
hardware: {gpu: "RTX 3050", vram_gb: 6, ram_gb: null, driver: "..."}
telemetry: {vram_peak_mb: 0, ram_peak_mb: 0, ssd_read_mb_s: 0, pcie_mb_s: 0}
performance: {prefill_tok_s: 0, decode_tok_s: 0, ttft_ms: 0}
quality: {ppl: null, pass_rate: null, accepted_length: null, sample: "..."}
status: pass|fail|fork
failure_fork: "route and trigger"
```

JSONL is the machine-readable source; Markdown is the human-readable index. No result is accepted without its artifact hash and quality-set revision.

### 5. Benchmark harness and quality set (`quality/`, `benchmarks/`)

Maintain three fixed sets: (a) 50 prompt instruction set for coherence and instruction following, (b) perplexity text shards with an FP16/NVFP4 reference, and (c) multimodal smoke/MMMU-style samples covering OCR, chart, spatial, and multi-step image reasoning. Freeze prompts, images, tokenizer revision, seeds, and scoring code. Report delta against the first trusted reference; quality gate is coherent N≥2048 and typically ≤+15% PPL or documented pass-rate delta.

Benchmark output contract:

```json
{"run_id":"...","set_id":"quality-v1","item_id":"...","input_hash":"...",
 "reference":{"artifact":"...","score":0},"candidate":{"artifact":"...","score":0},
 "metrics":{"ppl":0,"pass_rate":0,"exact_match":0},"raw_output_path":"..."}
```

Separate performance from quality: never call a faster but lower-quality draft the final model.

### 6. Hardware profiler and tier manager

`profile_memory` records VRAM/RAM, PCIe, SSD throughput, kernel time, power/temperature, and synchronization. The tier manager owns three explicit stores:

* **VRAM/hot:** active weights, attention/GDN state, KV, small page cache.
* **RAM/warm:** enhancement residuals, CPU FFN pages, mmap cache, prefetch queue.
* **SSD/cold:** immutable shards and inactive vision/weight pages.

A page descriptor carries `{tensor, offset, bytes, precision, tier, priority, last_use, checksum}`. The scheduler supports double buffering and backpressure; it must never silently evict KV or recurrent GDN state. At decode, only hidden state crosses PCIe where possible; weights move in layer/tensor pages.

### 7. Speculative verification service

Implement draft and verifier as separate runtime roles with a shared tokenizer and sampling seed. The verifier is authoritative. A verification record contains `{draft_tokens, verifier_logits, accepted_prefix, alpha, accepted_length, fallback_reason}`. Rejection sampling must produce the verifier distribution. T1's base ternary model drafts while RAM enhancement residuals produce a batched higher-precision verification pass; native Qwen MTP and a <=1B drafter are alternative branches, not hidden assumptions.

### 8. Multimodal staging

Image prefill is a separate transaction: load BF16/appropriate vision weights, preprocess and optionally dynamically prune visual tokens, run vision tower, serialize projected visual embeddings, then evict vision weights before language decode. Contract:

```json
{"image_hash":"...","processor_revision":"...","vision_precision":"bf16",
 "tokens_in":0,"tokens_kept":0,"embedding_path":"...","vram_peak_mb":0,
 "pruning_policy":"none|dynamic","quality_item":"..."}
```

This temporal separation prevents the ~0.8 GB vision footprint competing with decode weights. Any visual-token pruning must be evaluated for reasoning recovery, not only average speed.

## Phased architecture and experiment map

E stages are gates; T tracks are implementation routes. Each stage can fork without invalidating prior artifacts.

### E0 — Inventory and reference

Build manifests from `config.json`, measure actual VRAM/RAM/SSD/PCIe bandwidth, verify tokenizer and image preprocessing, and establish FP16 where possible plus the NVFP4 Qwen3.8 reference. Produce the quality-v1 set and baseline outputs. Contract: immutable artifact manifest + profiler JSON + reference benchmark record.

**Exit:** reproducible command, hardware numbers, reference scores, and a 2048-context coherent sample. If FP16 cannot be resident, use CPU/reference execution or NVFP4 as the explicitly labeled teacher; do not erase the distinction.

### E1 — Quantized baseline and subsystem sensitivity

Run Q4/NVFP4, Q3/IQ3/IQ2 or QTIP variants with one variable per run. Quantize GDN first (research reports it is relatively robust), then attention, FFN, and `lm_head`; measure layer/block output error and end-to-end quality. This is the baseline against which inventions are judged.

**Exit:** throughput/quality/memory table and per-subsystem bit allocation proposal. Failure fork: if a format lacks Qwen3.8/GDN support, add a converter/adapter or switch runtime; record three attempts before dormancy.

### E2 — Tiered memory and pipelined execution

Implement VRAM hot/RAM warm/SSD cold placement, async prefetch, and CPU/GPU split. First use stock partial offload, then pipelined sharding or a custom page scheduler. Profile page misses and PCIe copies separately from GEMV. Contract: page trace + scheduler policy + exact hidden-state transfer sizes.

**Exit:** a complete decode path at context 2048 with measurable tokens/s and no OOM. Routes include layer streaming, tensor-level FFN offload, and resident hot tensors. A wall means a fork to a different page granularity or prefetch policy, not a verdict.

### E3 — Ternary/mixed precision and speculative verification

Implement T2/T3 kernels and T1's scalable codec in stages: one FFN block, one layer, then full model. T1 stores ternary base in VRAM and enhancement residual in RAM; T2 targets 1.25-bit FFN plus 2.5-bit attention/GDN/lm_head; T3 places FFN on CPU for 4 GB SKUs. Add native MTP or <=1B drafter only after single-path logits are validated.

**Exit:** alpha/accepted-length distribution, verifier-equivalent outputs, and quality delta. Target T1 alpha >=0.6 at k=4; if alpha <0.4, fork to layer-wise distillation healing before kernel optimization. Target T3 AVX2 GEMV >=70% of measured STREAM bandwidth.

### E4 — Multimodal and quality closure

Stage BF16 vision prefill, dynamic visual-token pruning, eviction, then T1/T2/T3 language decode. Run OCR/chart/spatial/multi-step image tests and compare against the reference. Promote a route only if it satisfies full behavior, N>=2048 coherence, documented quality delta, and an interactive target (initial ambition >=3 decode tok/s).

**Exit:** fresh-clone reproduction from scripts, complete run ledger, route decision, and dormant-route triggers. T5 is the multimodal integration route; T4's dReLU/neuron-page cache is an optional acceleration branch evaluated here or in E3.

## Thesis-to-component map (T1–T5)

| Thesis | Primary components | Data contract / decisive metric | Main fork |
|---|---|---|---|
| **T1 scalable-codec self-speculation** | nested artifact manifest, ternary GPU kernel, RAM residual GEMV, speculative verifier | base/enhancement hashes; alpha, accepted length, verifier distribution; target alpha >=0.6 at k=4 and ~7 tok/s estimate | alpha <0.4 -> layer-wise distillation heal; PCIe bound -> CPU residual or larger batch |
| **T2 whole-model ternary** | Sherry/BitNet QAT or block healing, QTIP non-FFN, 2-bit KV, resident tier manager | per-layer block MSE, PPL/pass-rate delta, VRAM peak; target ~5.5 GB on 6 GB SKU | quality loss -> retain 2.5–4-bit sensitive tensors; compute cost -> block-local healing |
| **T3 CPU/GPU split** | AVX2 ternary FFN, GPU GDN/attention/head, pipelined scheduler | GEMV bandwidth fraction, hidden-state transfer trace, decode tok/s; target 6–8 tok/s estimate on 4 GB SKU | CPU below 70% STREAM -> bitnet.cpp/FairyFuse port, larger tile, or T1 residual route |
| **T4 virtual-texturing FFN** | activation profiler, dReLU healing, neuron page cache, hot/cold scheduler | activation mass/top-k, page hit rate, quality delta; hypothesis ~85% inactive and ~0.4 GB active FFN bytes | sparsity absent -> mixed precision without sparsity; misses high -> static hot set |
| **T5 precision-per-subsystem VLM** | vision staging, dynamic token pruning/recovery, multimodal benchmark, T2/T3 body | image hash, tokens in/kept, vision peak, MMMU/OCR delta; vision transient ~0.8 GB | pruning harms reasoning -> dynamic recovery or no pruning; overlap OOM -> stricter eviction barrier |

## Decision tradeoffs and failure forks

* **Quality vs footprint:** below ~1.6-bit PTQ has poor published large-model evidence; prefer training-aware healing or T1's verifier. If PPL rises >15%, preserve sensitive attention/head/GDN tensors at 2.5–4 bits and spend savings on FFN.
* **Bandwidth vs compute:** ternary reduces bytes but may underuse sm_86 if unpacking dominates. Benchmark GEMV at batch 1 and M=4/8/16; if MTP verification becomes compute-bound, reduce k or use a lower-cost drafter.
* **VRAM vs latency:** larger hot cache lowers SSD/RAM misses but steals KV/vision headroom. Use telemetry to set a page-cache budget, never a fixed guessed number.
* **RAM vs SSD:** mmap warm pages improve repeat runs but can evict OS memory. Cap warm cache and log major faults; if SSD is saturated, compress cold pages or prefetch earlier.
* **Multimodal fidelity vs prefill speed:** static visual pruning can fail on multi-step reasoning. Require recovery policy and modality-specific quality gates.
* **Stock runtime vs fork:** stock tools are the fastest baseline; fork only at a measured contract gap (unsupported GDN/MTP, no tensor placement, or missing ternary kernel). Keep adapter boundary stable so routes remain comparable.

Every failed route records exact constraint, at least two candidate engineering routes, and the cheapest next experiment. Three similar failures trigger a written fork/dormant note with a numeric revisit condition.

## Status / Numbers / Next Experiment

**Status:** Architecture specified as reproducible artifacts, scripts, tier manager, benchmark/quality contracts, speculative verifier, and staged multimodal pipeline. T1–T5 map to E0–E4 gates without conflating a draft with the authoritative full model.

**Numbers:** 25.6B streamed parameters/token; mixed 1.25/2.5-bit estimate ~5.3 GB; hybrid KV/state roughly 0.2 GB at 4K; T1 estimate ~7 tok/s; T3 estimate 6–8 tok/s; initial quality target <=+15% PPL delta and >=3 decode tok/s; T1 alpha target >=0.6 at k=4; T3 CPU target >=70% STREAM.

**Next Experiment:** E0 hardware/reference inventory. Run the profiler and one deterministic NVFP4 baseline at context 2048, then append a complete JSONL/Markdown record to `experiments/LOG.md` with VRAM/RAM peaks, SSD/PCIe bandwidth, prefill/decode tok/s, and 50-prompt quality results. The first route decision is whether measured bandwidth and quality support E1 quantization or require E2 tier scheduling first.

# AGENTS.md — Project: 27B on a 3050 Laptop

## MISSION (read first, always)

**Goal: Run Qwen/Qwen3.8-27B (55.6 GB, Apache-2.0, multimodal image-text-to-text) efficiently and fully on an RTX 3050 laptop GPU.**

- Repository: https://huggingface.co/Qwen/Qwen3.8-27B/tree/main
- Hardware: RTX 3050 laptop (4–8 GB VRAM), laptop DDR RAM, NVMe/SATA SSD.
- "Efficiently and fully" means: real inference quality, usable tokens/sec, and the complete model behavior — not a toy demo we quietly renounce later.

## CORE PHILOSOPHY — BANNED OUTPUT

We are inventing a new way from the ground up. From zero. Re-engineering the model itself is ON the table. Therefore:

**FORBIDDEN phrases and their equivalents in ANY language:**
- "This is impossible"
- "It will not work"
- "The hardware is not enough"
- "Simply not feasible" / "No way to do this"
- Any reasoning that ends with "give up" instead of "next experiment."

**MANDATORY replacement pattern:**
Every time a blocker is found, output:
1. The exact constraint (numbers, not feelings): e.g., "VRAM is 6 GB, model is 55.6 GB FP16, gap = X."
2. At least 2 candidate engineering routes to close the gap.
3. The cheapest next experiment (command + expected measurable result).

A constraint is data, not a verdict. Ratio 6 GB VRAM to 27B parameters is the puzzle, not the gravestone.

## ENGINEERING ATTACK VECTORS (investigate in this order, extend freely)

### Vector A — Aggressive quantization + partial offload (baseline, must be done first)
- Converters: GGUF via llama.cpp. Start with Unsloth's dynamic quants, e.g. `unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL`, then push down: Q3_K, IQ3, IQ2_XXS — measure quality loss per tier.
- llama.cpp flags: `-ngl 99` with partial offload, `-ot` tensor-override flags to pin FFN/expert tensors to CPU RAM while keeping attention + KV on GPU, quantized KV cache (`-ctk q8_0 -ctv q8_0`), small context first (2048), then grow.
- Also evaluate forks: ik_llama.cpp (better low-bit kernels), ktransformers.
- Deliverable: token/s + perplexity (or lm-eval pass rate) table per quant level.

### Vector B — Layer streaming (disk-paged inference)
- AirLLM / FlexGen / ollm-style: keep ONE layer on the GPU at a time; VRAM need = largest single layer, not the model. This runs 70B-class dense models on 4 GB GPUs.
- Requirements: model sharded on a fast SSD, async prefetch (double-buffer layer N+1 while N computes), optional 4-bit/8-bit block compression.
- Deliverable: working AirLLM (or custom paged loader) run of the 27B model + tok/s measurement + SSD bandwidth profiling. If stock AirLLM doesn't support this architecture, FORK and port it — that is exactly the "new way" we're building.

### Vector C — Surgical model re-engineering (the invention track)
This is where we redesign the model itself:
1. Depth pruning: identify and drop low-contribution transformer layers (measure with perplexity deltas per removed layer), then heal with light fine-tuning / LoRA.
2. Width pruning: structured prune attention heads and MLP neurons by activation importance.
3. Mixed-precision per-tensor surgery: attention + output heads at Q8/FP8, MLP blocks at Q2–Q4 (hot/cold importance profiling decides who gets bits).
4. MoE-ification: convert dense FFNs into expert shards so only the active experts occupy VRAM; experts live in RAM/SSD and stream in on routing. Expert-level offload (`-ot ffn=CPU` style in llama.cpp, or custom expert cache in a modified runtime).
5. Weight sharing / low-rank refactors: SVD factorize big matrices, store factors, reconstruct fused kernels.
6. Distillation fallback only as co-strategy: a distilled student accelerates prefill/speculative drafts, but the FULL model still decides final tokens — never present a tiny model as "the answer".

### Vector D — Decode-path optimization (once it runs, make it USABLE)
- Quantized KV cache, sliding-window attention if architecture allows.
- Speculative decoding: tiny drafter (≤1B) + the 27B as verifier → multiplies effective tok/s.
- Batch/continuous serving only when interactive latency is already acceptable.
- Preload + mmap tricks so RAM acts as a warm tier between SSD and VRAM (tiered memory: VRAM hot → RAM warm → SSD cold).

## EXPERIMENT PROTOCOL (mandatory for every attempt)

1. State hypothesis + numeric target before running (e.g., "IQ3 + ngl=99 + ffn=CPU should give ≥ 4 tok/s").
2. Record: exact command, model file, quant, context size, VRAM peak, RAM peak, tok/s prefill and decode, quality sample output.
3. Log every run to `experiments/LOG.md` — failures included, failures are the map.
4. One variable changes per experiment. If three things changed, the experiment is void.
5. If a route hits a wall 3 times, fork the route (variation) before abandoning; abandonment requires a written "dormant because" note with a trigger to revisit.

## FOLDER LAYOUT (create and maintain)

```
/models          # downloaded shards, GGUF conversions (never commit)
/runtimes        # cloned/forked llama.cpp, airllm, ktransformers + our patches
/scripts         # conversion, launch, benchmark scripts
/experiments     # LOG.md + one .md per experiment
/quality         # eval prompts, reference outputs, perplexity runs
/notes           # architecture notes on Qwen3.8-27B from config.json/model card
```

## QUALITY GATE — "fully" defined

A solution counts as DONE only when:
- The model produces coherent, instruction-following output at N≥2048 context.
- Benchmark: perplexity or a fixed 50-prompt eval within a documented acceptable delta vs the FP16 reference (we define the delta after first baseline; typical target ≤ +15%).
- Speed: ≥ measurable interactive threshold we set after the first working run (initial ambition: ≥ 3 tok/s decode).
- The whole pipeline reproduces from `scripts/` on a fresh clone.

## HOW TO COMMUNICATE IN THIS PROJECT

- Direct, engineering tone. Numbers over adjectives.
- Never apologize for the hardware. The hardware is the specification.
- Every report ends with: **Status / Numbers / Next Experiment**.
- If asked "can this work?", the answer is always: "Here is the current best route and the next test," never a verdict.

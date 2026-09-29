# Deep Research: Novel Inference Route for Qwen3.8-27B on an RTX 3050 Laptop

Date: 2026-09-29. Scope: raw mechanisms that can be combined into something new. The exclusions in the brief were followed: no layer streaming, no prune-and-accept, no stock GGUF offload recipes.

Coverage note: this was a focused pass, about 25 queries and 15 primary sources. Axes 1, 3 and parts of 2 and 5 are sourced. The Axis 4 cross-domain analogies (game engines, codecs, HPC) are my own reasoning and are marked **[synthesis]**. The Chinese-language search and the patent search were not done and are listed under the gap map.

---

## 0. The Physics, Using the Real Architecture

### 0.1 Architecture facts that change the math
From [config.json](https://huggingface.co/Qwen/Qwen3.8-27B/blob/main/config.json): hidden 5120, FFN intermediate 17408, 64 layers, 24 query heads / 4 KV heads, head_dim 256, vocab 248,320, **untied** embeddings, a 27-layer vision tower (hidden 1152), and **1 built-in MTP layer**. According to the [vLLM-Ascend model guide](https://docs.vllm.ai/projects/ascend/en/latest/tutorials/models/Qwen3.8-27B.html), only **16 of the 64 layers are full (gated) attention**. The other 48 are **Gated DeltaNet (linear attention) with a constant recurrent state**, and the model ships with native `qwen3_5_mtp` speculative decoding.

### 0.2 Parameter budget, derived from config
| Block | Math | Params | Share |
|---|---|---|---|
| FFN (SwiGLU, 3 mats × 64 layers) | 3·5120·17408·64 | **17.1 B** | 64% |
| GDN projections (48 layers) | ≈(10240+6144+6144)·5120·48 | ≈5.5 B | 20% |
| Full-attn projections (16 layers, gated Q) | ≈(12288+2048+6144)·5120·16 | ≈1.7 B | 6% |
| lm_head (untied) | 248320·5120 | **1.27 B** | 5% |
| Input embedding (lookup only, 1 row read/token) | 248320·5120 | 1.27 B | read ≈ 0 |
| Vision tower | 27 layers @1152 | ≈0.4 B | only during prefill |

**Bytes streamed per decode token ≈ 25.6 B params** (everything except the embedding table and the ViT).

### 0.3 Bandwidth floor
tok/s ≤ η · BW / bytes_per_token. RTX 3050 laptop SKUs are roughly 168–224 GB/s depending on bus width. Treat this as unverified and measure it with a bandwidth test on the actual machine. η ≈ 0.6–0.8 for good GEMV kernels.

| Representation of the 25.6 B streamed params | GB/token | Ceiling @180 GB/s, η=0.7 |
|---|---|---|
| BF16 | 51.2 | 2.5 tok/s (and it doesn't fit) |
| 4-bit | 12.8 | 9.8 (doesn't fit) |
| 2.0-bit | 6.4 | 19.7 (doesn't fit in 6 GB with KV) |
| **1.58-bit ternary** | **5.06** | **24.9** |
| **1.25-bit (Sherry 3:4)** | **4.0** | **31.5** |
| Mixed: FFN 1.25 b + GDN/attn 2.5 b + lm_head 2.5 b | 2.67+2.25+0.40 = **5.3** | **23.7** |

**Stress test of the "27B ternary ≈ 5.3 GB" claim.** The claim holds. 27e9 × 1.58 / 8 = 5.33 GB of pure payload. Real packing is 2 bits/weight in most kernels (e.g., FairyFuse packs 16 ternaries per 32 bits), which gives 6.75 GB. Group scales add about 0.25–0.5%. So "fits in 6 GB VRAM" needs one of these:
- a true base-3 packing (5 trits per byte = 1.6 b), or
- Sherry-style 1.25 b, or
- keeping lm_head and the vision tower outside VRAM.

### 0.4 The non-weight memory is tiny, thanks to hybrid attention
- KV cache (16 full layers × 4 KV heads × 256 × K+V × 2 B): **65.5 KB/token**. That is 134 MB at 2K context and 2.1 GB at 32K. With 2-bit KV (OSCAR-style) it drops to about 0.27 GB at 32K.
- GDN recurrent state (48 layers × 48 value heads × 128×128): **75 MB in FP16**, constant at any context length.
- **Conclusion:** unlike dense-attention 27B models, context length is nearly free here. Almost the whole VRAM budget can go to weights. This property of Qwen3.8 is the main enabler for everything below.

### 0.5 Quality evidence for ≥20B models below 2 bits (every number found)
| Method | Model | bits | Quality vs FP16 | Type |
|---|---|---|---|---|
| AQLM + PV-Tuning ([paper](https://arxiv.org/html/2405.14852v2)) | Llama-2-70B | **1.14** | Wiki2 PPL 5.52 vs 3.12; zero-shot 64.58 vs 72.40 | PTQ + FT |
| AQLM + PV-Tuning | Llama-3-70B | 1.01 | Wiki2 8.67 vs 2.59; zero-shot 51.47 vs 75.37 (collapse) | PTQ + FT |
| QTIP ([paper](https://arxiv.org/pdf/2406.11235)) | Llama-2-70B | 2 | Wiki2 5.86 vs 3.12 as extracted. The [QTIP breakdown](https://theorempath.com/papers/qtip) instead reports 3.87 for the fine-tuned variant, so check which table row is FT | PTQ |
| QTIP | Llama-3-70B | 2 | ArcC 28.0 vs 60.5 (the Llama-3 family is much harder to compress) | PTQ |
| AQLM-PV 2-bit ([HF card](https://huggingface.co/ISTA-DASLab/Llama-2-70b-AQLM-PV-2Bit-1x16-hf)) | Llama-2-70B | 2 | Wiki2 3.78 | PTQ + FT |
| NVFP4 W4A4 ([arXiv 2609.04098](https://arxiv.org/html/2609.04098v1)) | **Qwen3.8-27B** | 4 | PPL 7.67 vs 6.95 @4K; 5-task avg 85.10 vs 85.62 | PTQ |

Reading of the evidence:
- (a) Post-training quantization below about 1.6 b on modern, heavily trained models (Llama-3 class, and Qwen3.8 is heavier still) loses a lot of quality.
- (b) Training-aware ternary (BitDistill, Sherry, BitNet) has only been measured at **≤8B**.
- (c) **No published ≥20B general-purpose ternary conversion from a pretrained model exists.** That is the largest gap, and it is unexplored rather than blocked.

---

## 1. Findings by Axis

### Axis 1: Sub-2-bit representation

**F1. BitNet Distillation (BitDistill).** Microsoft. [arXiv 2510.13998](https://arxiv.org/html/2510.13998v1), preprint, code in [microsoft/BitNet](https://github.com/microsoft/BitNet).
- **Mechanism:** Converts a pretrained FP16 model to ternary W1.58A8. It inserts SubLN, runs 10B tokens of continued pretraining, then applies logit distillation plus single-layer multi-head-attention-relation distillation.
- **Numbers:** Tested on Qwen3 0.6B / 1.7B / 4B. Task scores match FP16 within about 0.1–0.2 (e.g., CNNDM 27.44 vs 27.58). CPU speed 1,135 vs 427 tok/s, memory 0.11 vs 1.20 GB.
- **Transfer:** This is the closest thing to "ternary without full retraining," but it is task-specific and ≤4B. Scaling it to 27B for general chat is the open problem. The main costs are 10B tokens of CPT at 27B (a GPU cluster) plus a teacher.
- **Trust:** single lab, code released.

**F2. Sherry (1.25-bit, 3:4 sparse ternary).** Tencent. [arXiv 2601.07892](https://arxiv.org/pdf/2601.07892), code at [AngelSlim](https://github.com/Tencent/AngelSlim), shipped model [Hy-MT1.5-1.8B-1.25bit-GGUF](https://huggingface.co/tencent/Hy-MT1.5-1.8B-1.25bit-GGUF).
- **Mechanism:** In every block of 4 weights, 3 are ±1 and 1 is 0. Each block packs into 5 bits, which restores power-of-two alignment. "Arenas" is an annealed full-precision residual path (λ→0) that prevents weights from getting trapped during QAT.
- **Numbers:** On LLaMA-3.2 1B/3B, ARC-c gap to BF16 <0.5%. The 3B model runs at 45.6 tok/s in 712 MB on an i7-14700HX, 18–27% faster than bitnet.cpp TL2.
- **Transfer:** 1.25 b puts the whole 17.1 B FFN at 2.67 GB. The 3:4 structure is a fixed-pattern sparse format that maps well to GPU lookup tables (5-bit index → 32-entry table of partial sums).
- **Trust:** single paper, but a product shipped.

**F3. AQLM + PV-Tuning.** ISTA / Yandex. [arXiv 2405.14852](https://arxiv.org/html/2405.14852v2), NeurIPS 2024, [code](https://github.com/Vahe1994/AQLM).
- **Mechanism:** Additive multi-codebook vector quantization. PV-Tuning alternates optimization of continuous parameters (codebooks, scales) and discrete parameters (codes), going beyond the straight-through estimator.
- **Numbers:** Lowest bits at 70B are listed in the table above. The 70B model decodes at 7.2 tok/s on an RTX 3090. The [AQLM repo](https://github.com/Vahe1994/AQLM) reports a 1-bit Llama-2-7B at Wiki2 PPL 7.85.
- **Transfer:** This is the **record holder** found for the lowest documented bits at ≥20B (1.01–1.14 b). Its decoder is codebook-lookup-bound; 1×16 codebooks (65K entries × 8 dims) do not fit in an Ampere L1 cache.
- **Trust:** replicated by the community, code released.

**F4. QTIP (trellis-coded quantization + incoherence processing).** Cornell RelaxML. [arXiv 2406.11235](https://arxiv.org/pdf/2406.11235), NeurIPS 2024, [code](https://github.com/Cornell-RelaxML/qtip).
- **Mechanism:** Replaces vector-quantization codebooks with a bitshift trellis. The "codebook" is computed from the state bits with a few instructions, so no lookup table is needed. Random Hadamard transforms first make the weights Gaussian-like.
- **Numbers:** 2-bit 70B at 23.5 tok/s on an RTX 6000 Ada, batch 1, faster than its 4-bit variant.
- **Transfer:** This is the right decoder for the **non-FFN tensors at 2–2.5 b**, because it needs compute rather than memory, which suits a bandwidth-starved 3050.
- **Trust:** high, code released.

**F5. PTQ1.61.** [arXiv 2502.13179](https://arxiv.org/abs/2502.13179), [code](https://github.com/zjq0455/PTQ1.61).
- **Mechanism:** Binary weights plus a 1-D structured mask that allocates 4 bits to salient input channels, at only 0.0002 bit/weight of mask overhead.
- **Transfer:** Usable as the salience allocator for mixed precision.
- **Trust:** no ≥20B numbers were extracted. Evidence is thin; the cheapest probe is to run their repo on one Qwen3.8 FFN block and measure layer output MSE.

**F6. Matryoshka Quantization.** Google DeepMind. [arXiv 2502.06786](https://arxiv.org/html/2502.06786v1), ICLR 2025 oral.
- **Mechanism:** Trains int8 weights so that their most significant bits form a usable int4 and int2 model. int2 gains about +1.65% from the nested supervision.
- **Transfer:** This is the **scalable-codec (base + enhancement layer) primitive**. The ternary/2-bit base stays in VRAM and the enhancement bits live in RAM. It is central to Thesis 1.
- **Trust:** peer-reviewed; public code not verified.

**F7. Vortex.** [arXiv 2609.12208](https://arxiv.org/pdf/2609.12208), preprint.
- **Mechanism:** 2-bit weight vector quantization plus KV vector quantization plus codebook-wise contextual sparsity (30%). Execution switches between a MUF path for batch M<16 and a LUF path for M≥16.
- **Numbers:** ≥95% of dense-AQLM accuracy at 25–30% sparsity. Effective bits fall below 2. Measured on a custom accelerator only (20.4 tok/s on 64 GB/s DDR4).
- **Transfer:** The **idea to steal** is the M-dependent dual path, because speculative verification pushes M from 1 up to 4–8. The hardware results do not transfer. Tested only on 7–13B.
- **Trust:** single paper, no code.

**F8. ParetoQ / ternary scaling laws.** [arXiv 2502.02631](https://arxiv.org/html/2502.02631v2) finds that ternary, 2-bit and 3-bit QAT sit on a similar size–accuracy Pareto front and beat 4-bit and binary. [arXiv 2506.23025](https://arxiv.org/html/2506.23025v1) reports ternary-layer kernels 7–8× faster than FP16 at batch 16–32 for 70B–405B shapes on an L40S.
- **Transfer:** Supports ternary as the right target bit-width and supports a GPU ternary kernel.

### Axis 2: Compute path

**F9. FairyFuse.** [arXiv 2604.20913](https://arxiv.org/html/2604.20913v1), preprint, code not public.
- **Mechanism:** Ternary GEMV using BMI2 `pext` to extract ± masks and AVX-512 masked add/sub. The inner loop has zero FP multiplies, and 8 sub-GEMVs are fused.
- **Numbers:** 7B at 2 b runs at 32.4 tok/s on a 48-core Xeon (~200 GB/s), 1.24× faster than Q4_K_M. PPL 5.52 vs 5.47.
- **Transfer:** Laptop CPUs often lack AVX-512, so an AVX2 port is needed. It proves **ternary makes CPU RAM bandwidth usable**: 2.67 GB of FFN at 50 GB/s DDR5 is about 19 tok/s for that half of the model. This is the basis of Thesis 3.

**F10. BitNet CUDA W1.58A8 kernel and bitnet-tc.** [BitNet 2B4T report](https://arxiv.org/html/2504.12285v1) and the [bitnet-tc kernel for sm_80–sm_90](https://huggingface.co/kernels/phanerozoic/bitnet-tc). The 3050 is sm_86 and is covered.
- **Transfer:** This is roughly 60% of the GPU half of Theses 1–3. No GPU tok/s was reported, so kernel efficiency η must be measured.

**F11. BitBLAS.** Microsoft. [repo](https://github.com/microsoft/bitblas). Mixed-precision GEMM supporting INT2/INT1/ternary weights with FP16/INT8 activations and tunable kernels. The fastest path to a measured η on sm_86.

**F12. EAGLE-3.** [arXiv 2503.01840](https://arxiv.org/pdf/2503.01840), [code](https://github.com/SafeAILab/EAGLE). 3.0–6.5× speedup and acceptance length τ of 4.05–7.5 on models up to Llama-3.3-70B.

**F13. Native Qwen MTP in practice.**
- Speedup depends on the setup. A Qwen3.5-122B NVFP4 GGUF measured **+46% at 2.46 effective tokens per decode step** ([HF card](https://huggingface.co/Incarnas/Qwen3.5-122B-A10B-NVFP4-MTP-GGUF)).
- A Qwen3.5-9B user measured a **−24% slowdown** at draft-n 6 ([HF discussion](https://huggingface.co/Qwen/Qwen3.5-9B/discussions/56)).
- An [ik_llama.cpp discussion](https://github.com/ikawrakow/ik_llama.cpp/discussions/1394) reports high acceptance under SGLang.
- **Transfer:** On a bandwidth-bound 3050, verifying k tokens costs about one weight read, so MTP should help as long as the verify kernel stays bandwidth-bound at M=k. Evidence thin; the cheapest probe is to measure the GEMV time ratio at M=1 vs M=4 on sm_86.

**F14. QSpec.** [arXiv 2410.11305](https://arxiv.org/abs/2410.11305), EMNLP 2025, [code](https://github.com/hku-netexplo-lab/QSpec).
- **Mechanism:** The same weights serve as a low-precision drafter (W4A4) and a high-precision verifier (W4A16).
- **Transfer:** This is **precedent for "the model drafts for itself at lower precision."** It has not been pushed to ternary draft + 4-bit verify, or to verifier bits split across memory tiers.

**F15. PowerInfer (activation sparsity, hot/cold neurons).** [repo](https://github.com/SJTU-IPADS/PowerInfer). TurboSparse-Mixtral-47B runs at 11.68 tok/s on consumer hardware.
- **Limit:** requires ReLU-family activations. [SparseQwen2-7B](https://huggingface.co/PowerInfer/SparseQwen2-7B) shows SiLU→dReLU conversion with continued training.
- **Transfer:** Could be combined with ternary QAT in a single healing run (Thesis 4).

### Axis 3: Memory architecture

**F16. Pipelined sharding.** [arXiv 2604.26334](https://arxiv.org/html/2604.26334), open-source llama.cpp fork.
- **Mechanism:** Sub-layer CPU/GPU sharding, pipelined copy/compute, prioritized VRAM placement and token-tier scheduling. For vision-language models (VLMOpt) it adds vision CPU offload, Q-chunked FlashAttention and avoidance of vision/language VRAM overlap.
- **Numbers:** up to 30× TPS and 6.7× TTFT, VRAM cut 10× (20→2 GB). The closest analog to our setup, Qwen-235B Q2_K at 2 GB VRAM, ran at **7.7 TPS**, but that is an MoE with about 22B active parameters. Hardware floor tested: RTX 3500 12 GB, PCIe 13 GB/s.
- **Limits:** no quality benchmarks; dense 27B was not tested at a 4 GB VRAM budget.
- **Transfer:** Its planner is the scheduler for Thesis 3. Its VLMOpt already solves "ViT and LLM must not coexist in VRAM."

**F17. XQuant.** [arXiv 2508.10395](https://arxiv.org/abs/2508.10395).
- **Mechanism:** Caches quantized layer inputs X instead of K/V and recomputes K and V on the fly. The cross-layer variant reaches 10× savings at 0.01 PPL loss and 12.5× at 0.1.
- **Transfer:** Low priority. KV is already only 65.5 KB/token here, and recomputing K/V needs the K/V weights for all 16 layers resident.

**F18. OSCAR.** [project page](https://oscar-quantize.github.io/), [alphaXiv 2605.17757](https://www.alphaxiv.org/abs/2605.17757v1).
- **Mechanism:** Offline covariance rotations plus 2-bit KV, with a BF16 sink (64 tokens) and a recent window (256 tokens). 2.28 b/element.
- **Numbers:** Qwen3-32B gap to BF16 is −0.02 points on GPQA/AIME/LiveCodeBench.
- **Transfer:** Applies to the 16 full-attention layers and makes 128K context about 1 GB. Directly usable.

**F19. GDN is easy to quantize.** [arXiv 2609.04098](https://arxiv.org/html/2609.04098v1), with the checkpoint [minima-ai/mnma_qwen3.8_27b_nvfp4](https://huggingface.co/minima-ai/mnma_qwen3.8_27b_nvfp4).
- **Numbers:** All 496 linear layers of **Qwen3.8-27B** at W4A4: −0.52 average points, +0.72 PPL at 4K.
- **Why it matters:** The authors explain mechanistically why the recurrent half is the *easy* half to quantize.
- **Transfer:** Direct evidence on our exact model. It suggests the 5.5 B GDN projections can go below 4 b before the attention layers do. It also provides a ready 4-bit reference checkpoint (≈14 GB) to use as the verifier or teacher.

### Axis 4: Cross-domain transfer [synthesis]
- **Scalable video coding (SVC) and progressive JPEG.** A base layer is decodable alone and an enhancement layer refines it. Mapped here: ternary weights W₀ in VRAM, plus a residual ΔW (MatQuant low bits, or a low-rank plus sparse correction) in RAM. The drafter uses W₀. The verifier uses W₀+ΔW, computed once per k drafted tokens. Rate-distortion view: spend bits where the verifier disagrees with the drafter, not uniformly. **Thesis 1.**
- **Virtual texturing / Nanite.** A GPU feedback buffer records which texture pages were sampled, and those pages are streamed at the needed mip level. Mapped here: per-token FFN neuron activity (after dReLU) is the feedback buffer, pages are neuron rows, and the "mip level" is bit-width. Hot rows stay resident at high precision; cold rows are fetched at ternary or skipped. **Thesis 4.**
- **Opus/iLBC and BlackBerry.** They send parameters of a model instead of raw samples, with the receiver holding the generator. Mapped here: weights stored as indices into shared learned bases (AQLM/QTIP are this; "weight-as-program" is the extreme form). The design principle: move computation to where the data already is, and send only innovations. The hidden state crossing PCIe is only 10 KB/layer; that is the "innovation" worth sending, never the weights.
- **Communication-avoiding GEMM (HPC).** Maximize arithmetic intensity by reusing each loaded weight tile across many right-hand sides. Speculative verification with M=k is exactly this: k tokens per weight read. Tree drafting raises M further at nearly zero bandwidth cost until the kernel becomes compute-bound. On a 3050 at 1.58 b that happens around M≈16–32 (estimate; measure it).

### Axis 5: Multimodal
- **Temporal separation.** The ViT (≈0.4 B, ≈0.8 GB BF16) runs only during prefill. So it can be staged in VRAM, run, and evicted before decode. Pipelined sharding's VLMOpt already does this.
- **Visual token pruning.** [HiPrune](https://arxiv.org/html/2508.00553) keeps 93% of performance at 11.1% of tokens. The [ECCV'26 DSTP note](https://en.papernotes.org/ECCV2026/vlm_efficiency/why_and_when_visual_token_pruning_fails_a_study_on_relevant_visual_information_s/) shows static pruning fails during multi-step reasoning and proposes dynamic recovery.
- **Hybrid-attention bonus.** Visual tokens pass through GDN layers into a constant-size state. Only the 16 full-attention layers keep per-token KV, so pruning mainly saves prefill compute, not memory.
- **Gap:** no paper was found on heterogeneous-precision VLM inference (BF16 ViT + ternary LLM body). This is unexplored.

---

## 2. Ranked Invention Theses

### T1. Scalable-Codec Self-Speculation (ternary base in VRAM + enhancement residual in RAM)
- **What:** Nested weights W₄ = W₀(ternary) + ΔW(≈2.5 b). The base drafts k tokens on GPU at base speed. The full model verifies them in one batched pass: GPU reads W₀, CPU reads ΔW (or ΔW is streamed over PCIe), and the partial sums are added. Rejection sampling makes the output **exactly the W₄ distribution**, which is about −0.5 points vs BF16 per F19. Quality equals 4-bit by construction.
- **Math (6 GB SKU):**
  - W₀ ≈ 5.3 GB mixed (see §0.3) → draft ≈ 40–70 ms/token.
  - ΔW ≈ 25.6 B × 2.5 b ≈ 8 GB in RAM → CPU reads at 50 GB/s ≈ 160 ms per verify.
  - With k=4 and about 3 accepted tokens per cycle: cycle ≈ 4×55 + 160 + 55 ≈ 435 ms → **≈ 7 tok/s at 4-bit-equivalent quality**.
  - With native MTP on top of the base drafter, k can grow further.
- **Kill/confirm experiment:** Offline, with no kernels, simulate token agreement between a ternary-PTQ'd Qwen3.8-27B and the NVFP4 checkpoint on 200 prompts. Measure the acceptance rate α at k=4. It must reach α≥0.6. If PTQ ternary gives α<0.4, add a healing run of about 1B tokens of distillation from the NVFP4 teacher before judging.
- **Existing code covering ~60%:** QSpec (dual-precision spec loop), MatQuant (nested bits), BitBLAS/bitnet-tc (GPU ternary), FairyFuse (CPU residual GEMV, AVX2 port needed).
- **Why nobody shipped it:** QSpec stays inside one memory tier. No one has split the verifier's bits across VRAM and RAM. Status: unexplored.

### T2. Whole-model-in-VRAM ternary via BitDistill-at-27B with a 4-bit teacher
- **What:** Sherry 1.25 b for the FFN, 2.5 b QTIP for GDN/attention, 2-bit KV via OSCAR. Distill from the NVFP4 27B checkpoint.
- **Math:** 5.3 GB of weights + 0.15 GB KV/state @4K ≈ 5.5 GB → fits the 6 GB SKU. Ceiling ≈ 24 tok/s; with native MTP (2.46 effective tokens per step) the expected range is **12–25 tok/s**.
- **Kill/confirm experiment:** Convert one layer's FFN with Sherry and heal it with layer-local distillation (block-output MSE vs teacher) on a single consumer GPU. Then measure end-to-end PPL with that layer swapped in. Extrapolate using the per-layer PPL deltas.
- **Existing code:** AngelSlim, BitNet/BitDistill, QTIP.
- **Missing piece:** CPT compute. Layer-wise distillation (like GPTQ/PV-tuning block-wise tuning) is feasible on consumer hardware. Full logit-level distillation is not; the source would be free research credits, TPU Research Cloud, or community compute.

### T3. Ternary CPU-GPU split for the 4 GB SKU
- **What:** GDN, attention and lm_head stay on GPU at 2.5 b (≈2.6 GB). The FFN runs on the CPU at 1.25 b (2.67 GB) with an AVX2 FairyFuse-style kernel. The pipelined-sharding planner handles scheduling. Only the 10 KB hidden state crosses PCIe, twice per layer.
- **Math:**
  - GPU 2.6 GB/150 GB/s ≈ 17 ms.
  - CPU 2.67 GB / 45 GB/s ≈ 59 ms.
  - 128 syncs × ~30 µs ≈ 4 ms.
  - Total ≈ **12 tok/s ceiling, 6–8 realistic**, before MTP.
- **Kill/confirm experiment:** Benchmark one AVX2 ternary GEMV of 17408×5120 on the actual laptop. The target is ≥70% of STREAM bandwidth.
- **Existing code:** pipelined-sharding fork, bitnet.cpp TL2 kernels.

### T4. Virtual-texturing FFN: dReLU + ternary + neuron-page cache
- **What:** Heal SiLU→dReLU in the same run as ternary QAT. A predictor marks the active neuron rows. Hot rows are VRAM-resident; cold rows are fetched from RAM on demand.
- **Math:** If 85% of FFN neurons are inactive per token (PowerInfer-class sparsity), FFN bytes per token fall from 2.67 GB to ≈0.4 GB. That frees VRAM for T1's enhancement layer.
- **Kill/confirm experiment:** Measure the natural activation-magnitude sparsity of Qwen3.8-27B's SwiGLU on 1K tokens: what fraction of |act| mass sits in the top 20% of neurons. No training needed.
- **Existing code:** PowerInfer, SparseQwen2 recipe.

### T5. Precision-per-subsystem VLM
- **What:** The ViT runs in BF16 on GPU during prefill and is then evicted. Visual tokens are pruned dynamically (DSTP-style). The LLM body uses T2 or T3.
- **Math:** 0.8 GB transient. A 4K-image prefill with 11% token retention cuts full-attention prefill FLOPs about 9×.
- **Kill/confirm experiment:** VLMOpt from pipelined sharding + HiPrune on the NVFP4 checkpoint. Measure an MMMU subset delta.

---

## 3. Gap Map
| Combination | Status | Reason |
|---|---|---|
| Ternary QAT/distillation of a ≥20B general model from pretrained weights | **Unexplored** | Public work stops at 8B; compute cost, not a technical block |
| Speculative decoding with verifier bits split across memory tiers (T1) | **Unexplored** | QSpec and MatQuant each exist; not combined |
| Ternary quantization on a hybrid GDN model | **Unexplored** | Only 4-bit tested (F19); GDN robustness suggests it may go lower |
| LUT/ternary kernel η measured on sm_86 laptop GPUs | **Unexplored** | Kernels exist for sm_80+; no laptop benchmark |
| dReLU sparsification + ternary in one heal | **Unexplored** | Two separate lines of work |
| Heterogeneous-precision VLM (BF16 ViT + sub-2-bit body) | **Unexplored** | No paper found |
| PTQ-only below 1.6 b at ≥20B with <15% PPL delta | **Blocked (technical)** | Measured: PV-Tuning at 1.14 b gives +77% PPL on Llama-2-70B. Missing piece: training-aware healing (T2) |
| AQLM 1×16 codebooks on a 3050 | **Blocked (technical)** | 65K×8 codebook exceeds L1. Missing piece: QTIP-style computed codebooks |
| Chinese-language literature and patents | **Not searched this pass** | Next step: search 三值量化 大模型, 1.58比特 蒸馏, and Google Patents for "ternary weight lookup table GPU" |

---

## Status / Numbers / Next Experiment
- **Status:** Physics recomputed on the real config. Hybrid attention makes KV+state ≈0.2 GB at 4K, so VRAM is essentially all weight budget. Five theses ranked. **T1 preserves 4-bit quality by construction.**
- **Numbers:**
  - 25.6 B params streamed per token.
  - Mixed 1.25/2.5-bit footprint ≈ 5.3 GB, ceiling ≈ 24 tok/s on the 6 GB SKU.
  - T1 estimate ≈ 7 tok/s at 4-bit-equivalent quality.
  - T3 estimate 6–8 tok/s on the 4 GB SKU.
  - Record found for sub-2-bit PTQ at ≥20B: 1.14 b with +77% PPL (Llama-2-70B).
- **Next experiment (cheapest, no kernels):** Hypothesis: a ternary-PTQ'd Qwen3.8-27B agrees with the NVFP4 checkpoint at α≥0.6 per token (k=4, greedy). Run both in fake-quant PyTorch on a rented or borrowed GPU, or layer-by-layer on the laptop, over 200 prompts. Log α, the accepted-length distribution and PPL of both models to `experiments/LOG.md`.
  - If α≥0.6, T1 is confirmed and kernel work starts.
  - If α<0.4, fork the route: layer-wise distillation heal of W₀, then re-measure.

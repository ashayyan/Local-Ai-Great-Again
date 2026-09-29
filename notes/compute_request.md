# Free-compute request: Qwen3.8-27B agreement and sparsity runs

## Request
Please provide a short-lived GPU allocation for the E1 agreement harness and E3.1 activation profile. The local RTX 3050 is the control machine only; it has 4,096 MiB VRAM and 16 GiB RAM, while the authoritative teacher is `minima-ai/mnma_qwen3.8_27b_nvfp4` and must remain the final verifier.

## Kaggle T4×2 request
Requested environment: two NVIDIA T4 GPUs, CUDA-compatible PyTorch/Transformers, local NVMe scratch, and enough wall time for a 200-prompt × 128-token agreement run plus a 1,000-token activation profile. Preserve tokenizer/model revision hashes, seeds, prompt-manifest hash, and raw logits/accepted-prefix records. Do not substitute a student for the teacher. The draft is an absmean ternary fake-quant approximation built by streaming the 55 GB BF16 shards layer-by-layer so RAM holds no more than one layer at a time.

## TPU Research Cloud application paragraph
I am requesting TPU Research Cloud access to measure an auditable, reproducible agreement harness for Qwen3.8-27B. The experiment compares a layer-streamed absmean ternary draft against the pinned `minima-ai/mnma_qwen3.8_27b_nvfp4` teacher, with 200 frozen held-out prompts, greedy and k=4 decoding, per-token agreement, accepted-prefix length, KL/logit deltas, and explicit recurrent-state reset checks. A parallel E3.1 profile records per-layer SwiGLU magnitude histograms, top-k mass, inactive fractions, and consecutive-token reuse across at least 1,000 tokens. All large artifacts remain outside Git; outputs are hashed and the run is fully pre-registered.

## Promotion gate
E1 promotion requires k=4 agreement alpha **>= 0.6**. Alpha < 0.4 triggers layer-wise healing/distillation and remeasurement; intermediate alpha requires a documented comparison. A local 20-prompt × 128-token smoke is correctness-only and must report projected full-run wall time before the remote run.

## Hardware / control summary
- Local control: RTX 3050 Laptop GPU, CC 8.6, 4,096 MiB VRAM, 16 GiB RAM, i5-11400H 6C/12T.
- Measured RAM Triad: 16.94 GB/s decimal median.
- Measured pinned H2D: approximately 1.85 GB/s-equivalent at 16 MiB.
- IQ3_S control bar: 1.8 decode tok/s, 10.3 prefill tok/s at context 2048, `-ngl 16`, q8_0 KV, seed 7.

## Status / Numbers / Next Experiment
- **Status:** Request artifact authored; no external allocation claimed.
- **Numbers:** alpha gate 0.6 at k=4; local control 4 GiB VRAM / 16 GiB RAM; 200 prompts remote, 20×128 local smoke.
- **Next Experiment:** Implement and run the local smoke harness with deterministic fixture hashes, then submit this request with the resulting projected wall time.

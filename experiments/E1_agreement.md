# E1 Agreement Harness Scaffold

## Pre-registration

Hypothesis: an absmean ternary fake-quant draft, constructed by streaming the 55 GB BF16 checkpoint one layer at a time, can reach k=4 agreement alpha >= 0.6 against the pinned `minima-ai/mnma_qwen3.8_27b_nvfp4` teacher while preserving verifier correctness.

Target: 200 frozen held-out prompts, greedy and k=4 modes; per-token agreement alpha, accepted-prefix distribution, KL/logit deltas, PPL delta, tokenizer identity, GDN recurrent-state reset, and seeded deterministic output checks.

## Frozen inputs

- Prompt manifest: `quality/manifest.json` plus a new 200-prompt held-out manifest; hash before execution.
- Draft: absmean ternary fake-quant; layer-streamed from BF16 shards, maximum one layer resident in RAM.
- Teacher: `minima-ai/mnma_qwen3.8_27b_nvfp4`; revision and tokenizer hash must be pinned before remote execution.
- k values: 1 (greedy control) and 4 (promotion setting).
- Local smoke: 20 prompts × 128 generated tokens, correctness only; projected full-run wall time is required before remote submission.

## Required records

Each prompt records prompt hash, tokenizer hash, seed, draft tokens/logits, teacher logits, accepted prefix, rejection reason, GDN/KV reset state, and final output hash. Raw records are JSONL outside Git; summary includes stratification by prompt category and sequence position.

## Route policy

The local 20×128 smoke validates harness plumbing only. The full 200-prompt run moves to approved free compute. If alpha < 0.4, run layer-wise healing/distillation and repeat. If 0.4 <= alpha < 0.6, retain comparison and test targeted healing. Three failures on one execution route require a fork with a numeric revisit trigger.

## Status / Numbers / Next Experiment
- **Status:** E1 scaffold authored; no agreement score is claimed.
- **Numbers:** 200 prompts remote target; 20×128 local smoke; k=4 alpha gate 0.6.
- **Next Experiment:** Freeze/hash the 200-prompt manifest and execute the local smoke with a projected wall-time estimate.

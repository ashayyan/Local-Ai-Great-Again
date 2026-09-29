# E0 pinned-model metadata follow-up

**2026-09-29.** The original offline inventory in [model_compatibility.md](<model_compatibility.md>) remains a historical record of the initially empty `models/` directory. This follow-up does **not** upgrade the full-model compatibility or stock-inference gate.

Hypothesis stated before retrieval: official repository metadata at immutable revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` includes config and a complete index without fetching weight shards. Target: at least config and index hashes; 0 safetensors downloads; verify 64 layers with a 48/16 split, 27 vision layers and native MTP indicator. Command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s02_fetch_metadata.ps1 -Revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -ModelPath models -TimeoutSeconds 30`, followed by `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s02_model_manifest.ps1 -ModelPath models -Output models/qwen3.8-27b-manifest.json -Revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -TokenizerRevision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -ProcessorRevision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 -Offline`. External repository SHA observed via [official model API](https://huggingface.co/api/models/Qwen/Qwen3.8-27B); file bytes retrieved from revision-pinned resolve URLs. No local signatures or model inference were verified.

| Item | Observation |
|---|---:|
| Metadata files hashed | 7 |
| Config SHA-256 | `191e0af232104ed8b65258cf3fb2b842e288008baca7633c11b82a1ac7203aab` |
| Index SHA-256 | `77042094076611b69791a610065f28b7013b8c621795fa86ddccc8bac7d1b9df` |
| Indexed tensors | 1,199 |
| Indexed weight shards | 18; **18 missing locally** |
| Config layers | 64; 48 linear/GDN, 16 full attention |
| Hidden / FFN / vocabulary | 5120 / 17408 / 248320 |
| Vision depth / MTP depth | 27 / 1 |
| Untied output head | `tie_word_embeddings=false`; `lm_head.weight` appears in index |
| Tokenizer weights and processor completeness | Tokenizer config and preprocessor config only; tokenizer.json and all weights still absent |

Constraint: indexed weight bytes `55,562,855,904` from the model index, installed RAM `17,179,869,184` bytes, GPU reports 4,096 MiB VRAM. This is a sizing datum, not a result of inference. Routes: (1) download pinned NVFP4 shards and use a correctly supporting full-model runtime with CPU/RAM tiering; (2) obtain pinned GGUF stock quant and partial-offload it for baseline, auditing GDN/vision/MTP coverage. Cheapest next experiment: fetch `tokenizer.json` alone at the same SHA, verify its hash and image processor configuration, then test a pinned loader without the full shard download.

## Status / Numbers / Next Experiment
- **Status:** Source metadata pinned and parsed; all model weights and reference outputs are still absent.
- **Numbers:** 7 metadata hashes, 1,199 indexed tensors, 18/18 indexed shards missing locally, 64/48/16 layer split, 27 vision layers, 1 MTP layer.
- **Next Experiment:** Fetch pinned tokenizer/processor metadata and test loader architecture support; choose a stock weight acquisition route before any throughput claim.

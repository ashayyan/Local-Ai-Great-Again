# Qwen3.8-27B artifact compatibility — E0-02

Run 2026-09-29, Windows-native offline inventory, **not inference**. Reproduce: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s02_model_manifest.ps1 -ModelPath models -Output models/qwen3.8-27b-manifest.json -Offline`. The generated JSON stays uncommitted under ignored `models/`. No source checkout, model card, configuration, tokenizer, processor, safetensors, GGUF, NVFP4 checkpoint, or reference output was present in the inspected `models/` directory. The generated manifest itself is excluded from enumeration. It records zero asset files, no asset SHA-256, and an unresolved source revision; the source name `Qwen/Qwen3.8-27B` is an intended repository, **not a verified revision**.

## Component matrix

| Component | Status | Evidence and boundary |
|---|---|---|
| Language body | missing | 0 safetensors/GGUF files; no weight index. |
| Input embedding and untied output lm_head | missing | No weight index or shards; untied head remains a research expectation, not verified here. |
| GDN blocks | missing | No weights/config; 48 GDN blocks cannot be confirmed locally. |
| Full attention blocks | missing | No weights/config; 16 attention blocks cannot be confirmed locally. |
| Vision tower/projector | missing | No vision weight index/config; text-only substitutes are not complete. |
| Tokenizer | missing | No tokenizer.json/tokenizer.model/vocab.json. Revision unresolved. |
| Image processor | missing | No processor/preprocessor JSON. Revision unresolved. |
| Native MTP | missing | No indexed MTP tensor or config. Runtime support untested. |
| Runtime loading, GDN state, vision projection, MTP decoding | unsupported (unverified) | No pinned model loader/runtime build or execution record; do not infer support from filename/exit status. |

## Architecture comparison (expected vs observed)

| Field | Research expectation, **not measured here** | Local config-derived value |
|---|---:|---|
| Layers | 64 total, 48 GDN + 16 full attention | unavailable: config.json missing |
| Hidden / FFN | 5120 / 17408 | unavailable |
| Vocab | 248320 | unavailable |
| Query / KV heads | 24 / 4 | unavailable |
| Embeddings | untied input/output head | unavailable |
| Vision tower | 27 layers | unavailable |
| Native MTP | 1 layer | unavailable |

These expected fields come from `Deep Research  27B on RTX 3050.md` and `.planning/research/STACK.md`; they are hypotheses to cross-check against a pinned config. The script exposes actual config values when present and never replaces absent values with expectations. `source_revision_status=unresolved-offline`; `tokenizer_revision=unresolved`; `processor_revision=unresolved`. Loader/runtime version: **none installed under `runtimes/`, none tested**. No claim of text or image compatibility is made.

## Constraint, routes and next experiment

Exact inventory constraint: 0 source files / 0 checksums / 8 missing required component classes; expected unquantized weights ~55.6 GB (externally reported), locally measured VRAM 4096 MB and RAM 17179869184 bytes in E0-HW. This run allocates no weights, so peak VRAM/RAM, context, prefill/decode tokens/s and quality are not applicable.

1. Cheapest route: fetch **metadata only** into `models/` from `Qwen/Qwen3.8-27B`, pin the resolved 40-hex commit, then regenerate SHA-256 records for downloaded files and check config against the table. Example (requires network + `huggingface_hub`):
   ```powershell
   python -c "from huggingface_hub import HfApi; print(HfApi().model_info('Qwen/Qwen3.8-27B').sha)"
   # Substitute printed immutable SHA and fetch metadata only, not *.safetensors:
   python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3.8-27B', revision='<40-hex-SHA>', local_dir='models', allow_patterns=['config.json','generation_config.json','tokenizer*','preprocessor_config.json','processor_config.json','model.safetensors.index.json'])"
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s02_model_manifest.ps1 -ModelPath models -Revision '<40-hex-SHA>' -TokenizerRevision '<40-hex-SHA>' -ProcessorRevision '<40-hex-SHA>' -Offline
   ```
   Expected measurement: metadata hashes, 64/48/16 architecture check where config exposes layer types, and index shard/tensor counts; 0 weight shards downloaded. Pinning via `-Revision` is an asserted input until the fetched metadata's origin is independently confirmed; never call it verified solely because it matches a SHA pattern.
2. Alternative route: export a metadata-only snapshot from a trusted machine/cache (record repo SHA and transfer hashes), rerun offline inventory. For loader support, pin a Transformers/llama.cpp commit with explicit GDN + vision + MTP support and test each capability; if native Windows loader blocks, try a separately labeled WSL2 build or a minimal architecture fixture. Neither route substitutes for complete checkpoint verification.

`models/` is excluded from version control. When actual shards arrive, compare `missing_index_shards` and tensor names against embedding/head, attention/GDN, vision, and MTP expectations before upgrading any component from unsupported to verified.

## Status / Numbers / Next Experiment
- **Status:** Inventory complete for available local path; full-model compatibility not yet measured.
- **Numbers:** 0 files, 0 hashes, 8 missing component classes, 0 pinned loader versions; target architecture 64/48/16 is research-only.
- **Next Experiment:** Fetch pinned metadata only using the command above; expect SHA-256 and config/weight-index coverage without downloading ~55.6 GB weights.
